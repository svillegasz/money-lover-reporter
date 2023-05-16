
from pydash import get, find
import requests
import os
import re
import datetime

CATEGORY_TYPE = {
    'income': 1,
    'expense': 2
}

class MoneyLover:
    URL = 'https://web.moneylover.me'
    AUTH_URL = 'https://oauth.moneylover.me'

    def __init__(self):
        self.login()
        self.set_categories()
        self.set_wallets()

    def login(self):
        print('Money lover: Starting login process')
        global access_token, refresh_token
        response = requests.post(
            f'{self.AUTH_URL}/token',
            headers=self.get_login_headers(),
            data={
                "client_info": True,
                "email": os.getenv('MONEY_LOVER_USER'),
                "password": os.getenv('MONEY_LOVER_PASSWORD')
            })
        self.check_response(response)
        access_token = get(response.json(), 'access_token')
        refresh_token = get(response.json(), 'refresh_token')      

    def get_login_headers(self):
        response = requests.post(
            f'{self.URL}/api/user/login-url',
            data={
                "force": False,
                "callback_url": self.URL
            })
        self.check_response(response)

        login_url = get(response.json(), 'data.login_url')
        match = re.search(r'client=(.*)&token=(.*)&', login_url)
        client = match.group(1)
        token = match.group(2)
        return {
            'client': client,
            'Authorization': f'Bearer {token}'
        }

    def sign_out(self):
        print('Money Lover: Starting sign out process')
        response = requests.post(
            f'{self.URL}/api/user/logout',
            headers={
                'authorization': f'AuthJWT {access_token}'
            },
            data={
                'refreshToken': refresh_token
            })
        self.check_response(response)

    def add_transaction(self, wallet, amount, category, description):
        print(f'Money lover: starting to add new transaction for "{description}" in wallet {wallet} for category {category}')
        print({
                "account": get(self.get_wallet(wallet), '_id'),
                "category": get(self.get_category(category, wallet), '_id'),
                "amount": amount,
                "note": description,
                "displayDate": (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            })
        response = requests.post(
            f'{self.URL}/api/transaction/add',
            headers={
                'authorization': f'AuthJWT {access_token}'
            },
            data={
                "account": get(self.get_wallet(wallet), '_id'),
                "category": get(self.get_category(category, wallet), '_id'),
                "amount": amount,
                "note": description,
                "displayDate": (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            }
        )
        self.check_response(response,
                            f'Money lover: Transaction with description "{description}" finished SUCCESS for wallet {wallet}',
                            f'Money lover: Transaction with description "{description}" finished FAILED for wallet {wallet} with error ')

    def get_wallet(self, name):
        return find(self.wallets,
                    lambda wallet: get(wallet, 'name').casefold() == name.casefold())

    def set_categories(self):
        print('Money lover: retrieving all existing categories')
        response = requests.post(
            f'{self.URL}/api/category/list-all',
            headers={
                'authorization': f'AuthJWT {access_token}'
            })
        self.check_response(response)
        self.categories = get(response.json(), 'data')

    def get_category(self, category, wallet):
        return find(self.categories,
                    lambda c: get(c, 'name').casefold() == get(category, 'name').casefold() and
                            get(c, 'type') == get(category, 'type') and
                            get(c, 'account') == get(self.get_wallet(wallet), '_id'))

    def set_wallets(self):
        print('Money lover: retrieving all existing wallets')
        response = requests.post(
            f'{self.URL}/api/wallet/list',
            headers={
                'authorization': f'AuthJWT {access_token}'
            })
        self.check_response(response)
        self.wallets = get(response.json(), 'data')

    def check_response(self, response, success='Request call was SUCCESS', failure='Request call FAILED'):
        if response.ok and ( get(response.json(), 'error') == 0 or get(response.json(), 'e') == 0 or get(response.json(), 'status') ):
            print(f'Money lover: {success} for endpoint {response.url}')
        else:
            print(f'Money lover: {failure} for endpoint {response.url} with status {response.reason} and error: {response.text}')
