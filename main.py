from pydash import nth, has_substr, get
from categorizer import categorize
import traceback
from moneylover import MoneyLover, CATEGORY_TYPE
import gmail
import re
import os
import requests

BANCOLOMBIA_EMAIL = 'alertasynotificaciones@notificacionesbancolombia.com'
SCOTIABANK_EMAIL = 'colpatriaInforma@colpatria.com'
moneylover = MoneyLover()


def usd_to_cop(usd):
    print('Categorizer: searching {text} in google'.format(text=text))
    headers = {
        "X-RapidAPI-Key": os.getenv('RAPID_KEY'),
        "X-RapidAPI-Host" : os.getenv('RAPID_HOST')
    }
    params = {
        "format": 'json',
        "from": "USD",
        "to": "COP",
        "amount": usd
    }
    response = requests.get(
        "https://currency-converter5.p.rapidapi.com/currency/convert",
        headers=headers,
        params=params)

    if response.status_code == 200:
        return get(response.json(), 'rates.COP.rate_for_amount')

def process_bancolombia_message(message):
    print('Bancolombia: processing message')
    content = message.text.strip().lower()
    match = re.search(r'(\$[\d,.]+|[\d,.]+ usd)', content)
    amount = re.sub(r'[^\d.]', '', match.group(1))
    is_expense = has_substr(content, 'compra por') or has_substr(content, 'pago por')
    if is_expense:
        if  has_substr(content, 'compra por'):
            print(match.group(1))
            amount = re.sub(r'[^\d,]', '', match.group(1)).replace(',', '.')
        category_type = CATEGORY_TYPE['expense']
        match = re.search(r'(\d a .+ desde|en .* \d\d:\d\d)', content)
        desc = re.sub(r'(\d a | desde|en | \d\d:\d\d)', '', match.group(1))
        category_name = categorize(desc)
    elif has_substr(content, 'recepcion transferencia'):
        category_type, desc, category_name = (CATEGORY_TYPE['income'], 'Transferencias', 'Others')
    elif has_substr(content, 'transf. internacional'):
        print('Bancolombia: International transfer ignored')
        return None, None, None, None  # Disabled until better approach. Right now there's not a notification of the actual moment I convert the international transfer to money into my account
        category_type, desc, category_name = (CATEGORY_TYPE['income'], 'Honorarios', 'Salary')
        amount = usd_to_cop(re.sub(r'[^\d,]', '', match.group(1)).replace(',', '.'))
    else:
        if  has_substr(content, 'retiro'):
            amount = re.sub(r'[^\d,]', '', match.group(1)).replace(',', '.')
        category_type = CATEGORY_TYPE['expense']
        desc, category_name = ('Retiro', 'Withdrawal') if has_substr(content, 'retiro') else ('Transferencia', 'Others')

    is_visa_expense = is_expense and has_substr(content, 'scotiabank')
    if is_visa_expense: 
        visa_category_type, visa_category_name = (CATEGORY_TYPE['income'], 'Payment')
    
    return amount, {'type': category_type, 'name': category_name}, desc, {'type': visa_category_type, 'name': visa_category_name} if is_visa_expense else None

def process_scotiabank_message(message):
    print('Scotiabank: processing message')
    cells = message.select('table table tr:last-child td')
    desc = nth(cells).string
    amount = re.sub(r'[^\d.]', '', nth(cells, 1).string)
    category_name = categorize(desc)
    return amount, {'type': CATEGORY_TYPE['expense'], 'name': category_name}, desc

def update_bancolombia_wallet(messages):
    if not messages: return
    print('Bancolombia: Updating wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc, visa_category = process_bancolombia_message(message)
        if not amount:
            continue
        moneylover.add_transaction('Bancolombia', amount, category, desc)
        if visa_category:
            moneylover.add_transaction('VISA', amount, visa_category, desc)
    print('Bancolombia: Updating wallet process finished')

def update_scotiabank_wallet(messages):
    if not messages: return
    print('Scotiabank: Updating wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc = process_scotiabank_message(message)
        moneylover.add_transaction('VISA', amount, category, desc)
    print('Scotiabank: Updating wallet process finished')

if __name__ == '__main__':
    bancolombia_messages = gmail.get_messages(BANCOLOMBIA_EMAIL)
    scotiabank_messages = gmail.get_messages(SCOTIABANK_EMAIL)
    try:
        update_bancolombia_wallet(bancolombia_messages)
        update_scotiabank_wallet(scotiabank_messages)
    except:
        traceback.print_exc()
    moneylover.sign_out()
