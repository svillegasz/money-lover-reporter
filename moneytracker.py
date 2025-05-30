from pydash import get, find
from notion_client import Client
import os
import datetime

from constants import CATEGORY_TYPE

class MoneyTracker:
    def __init__(self):
        print('Money Tracker: Initializing MoneyTracker...')
        
        # Check environment variables
        notion_token = os.getenv('NOTION_TOKEN')
        print(f'Money Tracker: NOTION_TOKEN present: {bool(notion_token)}')
        
        self.notion = Client(auth=notion_token)
        
        self.notion_expenses_database_id = os.getenv('NOTION_EXPENSES_DB_ID')
        self.notion_income_database_id = os.getenv('NOTION_INCOME_DB_ID')
        self.notion_categories_database_id = os.getenv('NOTION_CATEGORIES_DB_ID')
        self.notion_accounts_database_id = os.getenv('NOTION_ACCOUNTS_DB_ID')
        
        print(f'Money Tracker: Database IDs configured:')
        print(f'  - Expenses DB: {bool(self.notion_expenses_database_id)}')
        print(f'  - Income DB: {bool(self.notion_income_database_id)}')
        print(f'  - Categories DB: {bool(self.notion_categories_database_id)}')
        print(f'  - Accounts DB: {bool(self.notion_accounts_database_id)}')
        
        self.set_categories()
        self.set_accounts()
        print('Money Tracker: Initialization complete')

    def add_transaction(self, account, amount, category, description):
        print(f'Money Tracker: Starting add_transaction')
        print(f'  - Account: {account}')
        print(f'  - Amount: {amount}')
        print(f'  - Category: {category}')
        print(f'  - Description: {description}')
        
        # Validate inputs
        if not account:
            print('Money Tracker: ERROR - Account is required')
            return None
        if not amount:
            print('Money Tracker: ERROR - Amount is required')
            return None
        if not category:
            print('Money Tracker: ERROR - Category is required')
            return None
        if not description:
            print('Money Tracker: ERROR - Description is required')
            return None
            
        print(f'Money Tracker: Category type: {category.get("type", "unknown")}')

        if category['type'] == CATEGORY_TYPE['expense']:
            print('Money Tracker: Processing as expense transaction')
            return self.add_expense(account, amount, category, description)
        else:
            print('Money Tracker: Processing as income transaction')
            return self.add_income(account, amount, description)

    def add_expense(self, account, amount, category, description):
        print(f'Money Tracker: Starting add_expense')
        
        # Validate account and category exist
        account_obj = self.get_account(account)
        category_obj = self.get_category(category)
        
        if not account_obj:
            print(f'Money Tracker: ERROR - Account "{account}" not found')
            return None
        if not category_obj:
            print(f'Money Tracker: ERROR - Category "{category.get("name", "unknown")}" not found')
            return None
            
        print(f'Money Tracker: Account ID: {account_obj.get("id")}')
        print(f'Money Tracker: Category ID: {category_obj.get("id")}')
        
        date_str = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        print(f'Money Tracker: Using date: {date_str}')
        
        try:
            result = self.notion.pages.create(
                parent={
                    "database_id": self.notion_expenses_database_id
                },
                properties={
                    "Expense": {
                        "title": [
                            {
                                "text": {
                                    "content": description
                                }
                            }
                        ]
                    },
                    "Amount": {
                        "number": float(amount)
                    },
                    "Category": {
                        "relation": [
                            {
                                "id": get(category_obj, 'id')
                            }
                        ]
                    },
                    "Account": {
                        "relation": [
                            {
                                "id": get(account_obj, 'id')
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": date_str
                        }
                    }
                }
            )
            print(f'Money Tracker: Expense created successfully with ID: {result.get("id")}')
            return result
        except Exception as e:
            print(f'Money Tracker: ERROR creating expense: {str(e)}')
            return None

    def add_income(self, account, amount, description):
        print(f'Money Tracker: Starting add_income')
        
        # Validate account exists
        account_obj = self.get_account(account)
        
        if not account_obj:
            print(f'Money Tracker: ERROR - Account "{account}" not found')
            return None
            
        print(f'Money Tracker: Account ID: {account_obj.get("id")}')
        
        date_str = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        print(f'Money Tracker: Using date: {date_str}')
        
        try:
            result = self.notion.pages.create(
                parent={
                    "database_id": self.notion_income_database_id
                },
                properties={
                    "Income": {
                        "title": [
                            {
                                "text": {
                                    "content": description
                                }
                            }
                        ]
                    },
                    "Amount": {
                        "number": float(amount)
                    },
                    "Accounts": {
                        "relation": [
                            {
                                "id": get(account_obj, 'id')
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": date_str
                        }
                    }
                }
            )
            print(f'Money Tracker: Income created successfully with ID: {result.get("id")}')
            return result
        except Exception as e:
            print(f'Money Tracker: ERROR creating income: {str(e)}')
            return None

    def get_account(self, name):
        print(f'Money Tracker: Looking for account: "{name}"')
        
        if not hasattr(self, 'accounts') or not self.accounts:
            print('Money Tracker: ERROR - No accounts loaded')
            return None
            
        account = find(self.accounts,
                      lambda account: get(account, 'name').casefold() == name.casefold())
        
        if account:
            print(f'Money Tracker: Found account: {account.get("name")} (ID: {account.get("id")})')
        else:
            print(f'Money Tracker: Account "{name}" not found')
            print(f'Money Tracker: Available accounts: {[acc.get("name") for acc in self.accounts]}')
            
        return account
    
    def get_category(self, category):
        category_name = get(category, 'name')
        print(f'Money Tracker: Looking for category: "{category_name}"')
        
        if not hasattr(self, 'categories') or not self.categories:
            print('Money Tracker: ERROR - No categories loaded')
            return None
            
        found_category = find(self.categories,
                             lambda c: get(c, 'name').casefold() == category_name.casefold())
        
        if found_category:
            print(f'Money Tracker: Found category: {found_category.get("name")} (ID: {found_category.get("id")})')
        else:
            print(f'Money Tracker: Category "{category_name}" not found')
            print(f'Money Tracker: Available categories: {[cat.get("name") for cat in self.categories]}')
            
        return found_category

    def set_categories(self):
        print('Money Tracker: Starting to retrieve categories...')
        
        if not self.notion_categories_database_id:
            print('Money Tracker: ERROR - Categories database ID not configured')
            self.categories = []
            return
            
        try:
            response = self.notion.databases.query(database_id=self.notion_categories_database_id)
            print(f'Money Tracker: Categories API response received with {len(response.get("results", []))} results')
            
            # Extract category names from the response
            self.categories = []
            for i, result in enumerate(response.get('results', [])):
                print(f'Money Tracker: Processing category {i+1}...')
                
                category_title = result.get('properties', {}).get('Category', {}).get('title', [])
                if category_title:
                    category_name = category_title[0].get('plain_text', '')
                    if category_name:
                        category_data = {
                            'name': category_name,
                            'type': CATEGORY_TYPE['expense'],
                            'id': result.get('id')
                        }
                        self.categories.append(category_data)
                        print(f'Money Tracker: Added category: {category_name} (ID: {result.get("id")})')
                    else:
                        print(f'Money Tracker: WARNING - Category {i+1} has empty name')
                else:
                    print(f'Money Tracker: WARNING - Category {i+1} has no title property')
            
            print(f'Money Tracker: Successfully loaded {len(self.categories)} categories')
            
        except Exception as e:
            print(f'Money Tracker: ERROR retrieving categories: {str(e)}')
            self.categories = []

    def set_accounts(self):
        print('Money Tracker: Starting to retrieve accounts...')
        
        if not self.notion_accounts_database_id:
            print('Money Tracker: ERROR - Accounts database ID not configured')
            self.accounts = []
            return
            
        try:
            response = self.notion.databases.query(database_id=self.notion_accounts_database_id)
            print(f'Money Tracker: Accounts API response received with {len(response.get("results", []))} results')

            self.accounts = []
            for i, result in enumerate(response.get('results', [])):
                print(f'Money Tracker: Processing account {i+1}...')
                
                account_title = result.get('properties', {}).get('Account', {}).get('title', [])
                if account_title:
                    account_name = account_title[0].get('plain_text', '')
                    if account_name:
                        account_data = {
                            'name': account_name,
                            'id': result.get('id')
                        }
                        self.accounts.append(account_data)
                        print(f'Money Tracker: Added account: {account_name} (ID: {result.get("id")})')
                    else:
                        print(f'Money Tracker: WARNING - Account {i+1} has empty name')
                else:
                    print(f'Money Tracker: WARNING - Account {i+1} has no title property')

            print(f'Money Tracker: Successfully loaded {len(self.accounts)} accounts')
            
        except Exception as e:
            print(f'Money Tracker: ERROR retrieving accounts: {str(e)}')
            self.accounts = []
