
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
        access_token = get(response.json(), 'access_token')
        refresh_token = get(response.json(), 'refresh_token')

    def get_login_headers(self):
        response = requests.post(
            f'{self.URL}/api/user/login-url',
            data={
                "force": False,
                "callback_url": self.URL
            })

        login_url = get(response.json(), 'data.login_url')
        match = re.search(r'client=(.*)&token=(.*)&', login_url)
        client = match.group(1)
        token = match.group(2)
        return {
            'client': client,
            'Authroization': f'Bearer {token}'
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

        if response.status_code == 200:
            print('Money Lover: Starting sign out process')

    def add_transaction(self, wallet, amount, category, description):
        print('Money lover: starting to add new transaction for wallet {wallet}'.format(wallet=wallet))
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
        if response.status_code == 200:
            print(f'Money lover: Transaction with description "{description}" finished SUCCESS for wallet {wallet}')
        else:
            print(f'Money lover: Transaction with description "{description}" finished FAILED for wallet {wallet} with error {response.text}')

    def get_wallet(self, name):
        print(f'Money lover: retrieving data for wallet {name}')
        return find(self.wallets,
                    lambda wallet: get(wallet, 'name').casefold() == name.casefold())

    def set_categories(self):
        print('Money lover: retrieving all existing categories')
        response = requests.get(
            f'{self.URL}/api/category/list-all',
            headers={
                'authorization': f'AuthJWT {access_token}'
            })

        self.categories = get(response.json(), 'data')

    def get_category(self, category, wallet):
        print(f'Money lover: retrieving data for category {category} in wallet {wallet}')
        return find(self.categories,
                    lambda c: get(c, 'name').casefold() == get(category, 'name').casefold() and
                            get(c, 'type') == get(category, 'type') and
                            get(c, 'account') == get(self.get_wallet(wallet), '_id'))

    def set_wallets(self):
        print('Money lover: retrieving all existing wallets')
        response = requests.get(
            f'{self.URL}/api/wallet/list',
            headers={
                'authorization': f'AuthJWT {access_token}'
            })

        self.wallets = get(response.json(), 'data')
