
from pydash import get, gt, lines, nth, last, has_substr, lower_case, trim
import traceback
import moneylover
import gmail
import re

DAVIVIENDA_EMAIL = 'BANCO_DAVIVIENDA@davivienda.com'
SCOTIABANK_EMAIL = 'colpatriaInforma@colpatria.com'
PSE_EMAIL = 'serviciopse@achcolombia.com.co'

def process_davivienda_message(message):
    print('processing davivienda message')
    amount = re.sub(r'[^\d.]', '', nth(lines(message.string), 6))
    category_type = nth(lines(message.string), 7)
    if has_substr(lower_case(category_type), 'deposito') or has_substr(lower_case(category_type), 'abono'):
        category_type = moneylover.CATEGORY_TYPE['income']
        category_item = 'Award' # TO DO: Define category item
    else:
        category_type = moneylover.CATEGORY_TYPE['expense']
        category_item = 'Bills & Utilities' # TO DO: Define category item
    desc = trim(nth(lines(message.string), 8))
    return amount, {'type': category_type, 'item': category_item}, desc

def process_scotiabank_message(message):
    desc = nth(message.table.find_all('p'), 2).string
    amount = re.sub(r'[^\d.]', '', nth(message.table.find_all('p'), 3).string)
    return amount, {'type': 'EXPENSE', 'item': 'Bills & Utilities'}, desc

def process_pse_message(message):
    data = lines(last(message.table.table.find_all('span')))
    desc = re.sub(r'<[^<>]*>', '', nth(data))
    amount = re.sub(r'[^\d.]', '', nth(data, 2))
    is_visa = has_substr(lower_case(desc), 'credito visa')
    if is_visa:
        visa_category_type = moneylover.CATEGORY_TYPE['income']
        visa_category_item = 'Award' # TO DO: Define category item
    category_type = moneylover.CATEGORY_TYPE['expense']
    category_item = 'Bills & Utilities' # TO DO: Define category item
    return amount, {'type': category_type, 'item': category_item}, desc, {'type': visa_category_type, 'item': visa_category_item} if is_visa else None

def update_davivienda_wallet(messages):
    if not messages: return
    print('General: Updating davivienda wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc = process_davivienda_message(message)
        moneylover.add_transaction('DAVIVIENDA', amount, category, desc)
    print('General: Updating davivienda wallet process finished')

def update_scotiabank_wallet(messages):
    if not messages: return
    print('General: Updating scotiabank wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc = process_scotiabank_message(message)
        moneylover.add_transaction('VISA', amount, category, desc)
    print('General: Updating scotiabank wallet process finished')

def update_pse_wallet(messages):
    if not messages: return
    print('General: Updating davivienda(pse) wallet process started')
    for msg_id in messages:
        message = gmail.get_message(msg_id)
        amount, category, desc, visa_category = process_pse_message(message)
        moneylover.add_transaction('DAVIVIENDA', amount, category, desc)
        if visa_category:
            moneylover.add_transaction('VISA', amount, visa_category, desc)
    print('General: Updating davivienda(pse) wallet process started')

if __name__ == '__main__':
    gmail.get_oauth_token()
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
