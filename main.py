from pydash import nth, has_substr
from categorizer import categorize
from moneytracker import MoneyTracker
from datetime import datetime
import gmail
import re
from constants import RECURRING_TRANSACTIONS, BANCOLOMBIA_EMAIL, SCOTIABANK_EMAIL, CATEGORY_TYPE, BANCOLOMBIA_ACCOUNT, SCOTIABANK_ACCOUNT

moneytracker = MoneyTracker()
are_messages_processed = True

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

def update_bancolombia_account(messages):
    global are_messages_processed
    if not messages: return
    print('Bancolombia: Updating account process started')
    for msg_id in messages:
        try:
            message = gmail.get_message(msg_id)
            if has_substr(message.text.strip().lower(), 'transf. internacional'): # Ignore international transfer (Manual Input) - We can not know with full accuraccy what the actual income in COP is, because there is not notifification when converting usd to cop
                continue
            amount, category, desc, visa_category = process_bancolombia_message(message)
            moneytracker.add_transaction(BANCOLOMBIA_ACCOUNT, amount, category, desc)
            if visa_category:
                moneytracker.add_transaction(SCOTIABANK_ACCOUNT, amount, visa_category, desc)
        except Exception as e:
            print(f'Bancolombia: Error processing message {msg_id}: {e}')
            are_messages_processed = False
    print('Bancolombia: Updating account process finished')

def update_scotiabank_account(messages):
    global are_messages_processed
    if not messages: return
    print('Scotiabank: Updating account process started')
    for msg_id in messages:
        try:
            message = gmail.get_message(msg_id)
            amount, category, desc = process_scotiabank_message(message)
            moneytracker.add_transaction(SCOTIABANK_ACCOUNT, amount, category, desc)
        except Exception as e:
            print(f'Scotiabank: Error processing message {msg_id}: {e}')
            are_messages_processed = False
    print('Scotiabank: Updating account process finished')

def add_recurring_transactions():
    for transaction in RECURRING_TRANSACTIONS:
        if transaction['day'] == datetime.now().day:
            print(f'{transaction["account"]}: Adding recurring transaction: {transaction}')
            moneytracker.add_transaction(transaction['account'], transaction['amount'], transaction['category'], transaction['description'])

if __name__ == '__main__':
    bancolombia_messages = gmail.get_messages(BANCOLOMBIA_EMAIL)
    scotiabank_messages = gmail.get_messages(SCOTIABANK_EMAIL)
    update_bancolombia_account(bancolombia_messages)
    update_scotiabank_account(scotiabank_messages)
    add_recurring_transactions()

    if not are_messages_processed:
        raise Exception('Failed to process some messages')
    