
from pydash import get, gt, lines, nth, last, has_substr, lower_case, trim, upper_case, split
from categorizer import categorize
import traceback
import moneylover
import gmail
import re

DAVIVIENDA_EMAIL = 'BANCO_DAVIVIENDA@davivienda.com'
SCOTIABANK_EMAIL = 'colpatriaInforma@colpatria.com'
PSE_EMAIL = 'serviciopse@achcolombia.com.co'

def process_davivienda_message(message):
    print('Davivienda: processing message')
    amount = re.sub(r'[^\d.]', '', nth(lines(message.string), 6))
    category_type = nth(lines(message.string), 7)
    desc = trim(nth(split(nth(lines(message.string), 8), ':'), 1))
    if has_substr(upper_case(desc), 'PSE'):
        print('Davivienda: Ignored PSE payment')
        return None, None, None
    if has_substr(lower_case(category_type), 'deposito') or has_substr(lower_case(category_type), 'abono'):
        category_type = moneylover.CATEGORY_TYPE['income']
        category_item = 'Salary' if has_substr(upper_case(desc), 'ACH GNB SUDAMERIS') else 'Others'
    else:
        category_type = moneylover.CATEGORY_TYPE['expense']
        category_item = categorize(desc)
    return amount, {'type': category_type, 'item': category_item}, desc

def process_scotiabank_message(message):
    print('Scotiabank: processing message')
    desc = nth(message.table.find_all('p'), 3).string
    amount = re.sub(r'[^\d.]', '', nth(message.table.find_all('p'), 4).string)
    category_item = categorize(desc)
    return amount, {'type': 'EXPENSE', 'item': category_item}, desc

def process_pse_message(message):
    print('PSE(davivienda): processing message')
    data = lines(last(message.table.table.find_all('span')))
    desc = re.sub(r'<[^<>]*>', '', nth(data))
    amount = re.sub(r'[^\d.]', '', nth(data, 2))
    is_visa = has_substr(lower_case(desc), 'credito visa')
    if is_visa:
        visa_category_type = moneylover.CATEGORY_TYPE['income']
        visa_category_item = 'Payment'
    category_type = moneylover.CATEGORY_TYPE['expense']
    category_item = categorize(desc)
    return amount, {'type': category_type, 'item': category_item}, desc, {'type': visa_category_type, 'item': visa_category_item} if is_visa else None

def update_davivienda_wallet(messages):
    if not messages: return
    print('Davivienda: Updating wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc = process_davivienda_message(message)
        if amount:
            moneylover.add_transaction('DAVIVIENDA', amount, category, desc)
    print('Davivienda: Updating wallet process finished')

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
    print('PSE(davivienda): Updating wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc, visa_category = process_pse_message(message)
        moneylover.add_transaction('DAVIVIENDA', amount, category, desc)
        if visa_category:
            moneylover.add_transaction('VISA', amount, visa_category, desc)
    print('PSE(davivienda): Updating davivienda(pse) wallet process started')

if __name__ == '__main__':
    davivienda_messages = gmail.get_messages(DAVIVIENDA_EMAIL)
    scotiabank_messages = gmail.get_messages(SCOTIABANK_EMAIL)
    pse_messages = gmail.get_messages(PSE_EMAIL)

    moneylover.login()
    try:
        update_davivienda_wallet(davivienda_messages)
        update_scotiabank_wallet(scotiabank_messages)
        update_pse_wallet(pse_messages)
    except:
        traceback.print_exc()
    moneylover.sign_out()
