from pydash import nth, has_substr
from categorizer import categorize
import traceback
from moneylover import MoneyLover, CATEGORY_TYPE
import gmail
import re

BANCOLOMBIA_EMAIL = 'alertasynotificaciones@bancolombia.com.co OR alertasynotificaciones@notificacionesbancolombia.com'
SCOTIABANK_EMAIL = 'colpatriainforma@scotiabankcolpatria.com'
moneylover = MoneyLover()


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
    elif has_substr(content, 'recepcion transferencia') or has_substr(content, 'bancolombia: recibiste'):
        category_type, desc, category_name = (CATEGORY_TYPE['income'], 'Transferencias', 'Others')
    else:
        if  has_substr(content, 'retiro'):
            amount = re.sub(r'[^\d,]', '', match.group(1)).replace(',', '.')
        category_type = CATEGORY_TYPE['expense']
        desc, category_name = ('Retiro', 'Withdrawal') if has_substr(content, 'retiro') else ('Transferencia', 'Others')

    is_visa_expense = is_expense and has_substr(content, 'pagos electronicos s')
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
        if has_substr(message.text.strip().lower(), 'transf. internacional'): # Ignore international transfer (Manual Input) - We can not know with full accuraccy what the actual income in COP is, because there is not notifification when converting usd to cop
            continue
        amount, category, desc, visa_category = process_bancolombia_message(message)
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
