from pydash import lines, nth, last, has_substr, lower_case, trim, upper_case, split
from categorizer import categorize
import traceback
from moneylover import MoneyLover, CATEGORY_TYPE
import gmail
import re

BANCOLOMBIA_EMAIL = 'alertasynotificaciones@notificacionesbancolombia.com'
SCOTIABANK_EMAIL = 'colpatriaInforma@colpatria.com'
PSE_EMAIL = 'serviciopse@achcolombia.com.co'
moneylover = MoneyLover()

def process_bancolombia_message(message):
    print('Bancolombia: processing message')
    content = message.text.strip()
    match = re.search(r'Bancolombia le informa.*\$([\d,.]+)', content)
    amount = match.group(1).replace(',', '')
    if has_substr(content, 'PSE'):  # TODO: Validate other income (transfers), validate pse expenses, validate other expenses, validate cases agains 'bancolombia le informa...' paragraph data
        print('Bancolombia: Ignored PSE payment')
        return None, None, None
    if has_substr(content, 'deposito') or has_substr(lower_case(category_type), 'abono'):
        category_type = CATEGORY_TYPE['income']
        desc = 'Honorarios'
        category_name = 'Salary' if has_substr(upper_case(desc), 'ACH GNB SUDAMERIS') else 'Others'
    else:
        category_type = CATEGORY_TYPE['expense']
        desc = 'Transferencias'
        category_name = 'Others'
    return amount, {'type': category_type, 'name': category_name}, desc

def process_scotiabank_message(message):
    print('Scotiabank: processing message')
    cells = message.select('table table tr:last-child td')
    desc = nth(cells).string
    amount = re.sub(r'[^\d.]', '', nth(cells, 1).string)
    category_name = categorize(desc)
    return amount, {'type': CATEGORY_TYPE['expense'], 'name': category_name}, desc

def process_pse_message(message):
    print('PSE(bancolombia): processing message')
    data = lines(last(message.table.table.find_all('span')))
    desc = re.sub(r'<[^<>]*>', '', nth(data, 1)).strip()
    amount = re.sub(r'[^\d,]', '', nth(data, 3)).replace(',', '.')
    is_visa = has_substr(lower_case(desc), 'credito visa')
    if is_visa:
        visa_category_type = CATEGORY_TYPE['income']
        visa_category_name = 'Payment'
    category_type = CATEGORY_TYPE['expense']
    category_name = categorize(desc)
    return amount, {'type': category_type, 'name': category_name}, desc, {'type': visa_category_type, 'name': visa_category_name} if is_visa else None

def update_bancolombia_wallet(messages):
    if not messages: return
    print('Bancolombia: Updating wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc = process_bancolombia_message(message)
        if amount:
            moneylover.add_transaction('Bancolombia', amount, category, desc)
    print('Bancolombia: Updating wallet process finished')

def update_scotiabank_wallet(messages):
    if not messages: return
    print('Scotiabank: Updating wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc = process_scotiabank_message(message)
        moneylover.add_transaction('VISA', amount, category, desc)
    print('Scotiabank: Updating wallet process finished')

def update_pse_wallet(messages):
    if not messages: return
    print('PSE(bancolombia): Updating wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc, visa_category = process_pse_message(message)
        moneylover.add_transaction('DAVIVIENDA', amount, category, desc)
        if visa_category:
            moneylover.add_transaction('VISA', amount, visa_category, desc)
    print('PSE(bancolombia): Updating bancolombia(pse) wallet process started')

if __name__ == '__main__':
    # bancolombia_messages = gmail.get_messages(BANCOLOMBIA_EMAIL)
    scotiabank_messages = gmail.get_messages(SCOTIABANK_EMAIL)
    pse_messages = gmail.get_messages(PSE_EMAIL)
    try:
        # update_bancolombia_wallet(bancolombia_messages)
        update_scotiabank_wallet(scotiabank_messages)
        update_pse_wallet(pse_messages)
    except:
        traceback.print_exc()
    moneylover.sign_out()
