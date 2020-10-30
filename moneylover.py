
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from pydash import last, nth
import time
import os

WALLET_IDS = {
    'DAVIVIENDA': 'wallet_dialog_1',
    'VISA': 'wallet_dialog_3'
}

CATEGORY_TYPE = {
    'expense': 'EXPENSE',
    'income': 'INCOME',
    'debt': 'DEBT/LOAN'
}

URL = 'https://web.moneylover.me/'

def login():
    global driver
    global wait
    print('Money lover: Starting selenium session')
    driver = webdriver.Remote(
        command_executor='http://0.0.0.0:4444/wd/hub',
        desired_capabilities={'browserName': 'firefox'})
    wait = WebDriverWait(driver, 10)
    print('Money lover: Starting login process')
    driver.get(URL)
    wait.until(lambda d: d.find_element_by_class_name('google'))
    driver.find_element_by_class_name('google').click()
    time.sleep(3)
    print('Money lover: Setting credentials in new tab')
    driver.switch_to_window(last(driver.window_handles))
    driver.find_element_by_xpath('//input[@type="email"]').send_keys(os.getenv('GOOGLE_USER'))
    driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
    time.sleep(3)
    driver.find_element_by_xpath('//input[@type="password"]').send_keys(os.getenv('GOOGLE_PASSWORD'))
    driver.find_element_by_xpath('//*[@id="passwordNext"]').click()
    time.sleep(10)
    print('Money lover: login process finished: moving to main tab')
    driver.switch_to_window(nth(driver.window_handles))
    wait.until(lambda d: d.find_element_by_id('master-container'))

def sign_out():
    print('Money Lover: Starting sign out process')
    wait.until(lambda d: d.find_element_by_class_name('item-navigation').is_displayed())
    driver.save_screenshot('ss.png')
    driver.find_element_by_class_name('item-navigation').click()
    wait.until(lambda d: d.find_element_by_class_name('screen_30').is_displayed())
    driver.find_element_by_class_name('screen_30').click()
    wait.until(lambda d: d.find_element_by_class_name('singout-text').is_displayed())
    driver.find_element_by_class_name('singout-text').click()
    wait.until(lambda d: d.find_element_by_class_name('page-not-found').is_displayed())
    print('Money lover: sign out process finished - finishing money lover session')
    driver.close()

def add_transaction(wallet, amount, category, description):
    print('Money lover: starting to add new transaction for wallet {wallet}'.format(wallet=wallet))
    driver.find_element_by_class_name('button-add-tran-toolbar').click()

    print('Money lover: selecting wallet {wallet}'.format(wallet=wallet))
    wait.until(lambda d: d.find_element_by_css_selector('.v-dialog--active .wallet').is_displayed())
    driver.find_element_by_css_selector('.v-dialog--active .wallet').click()
    wait.until(lambda d: d.find_element_by_id(WALLET_IDS.get(wallet)).is_displayed())
    driver.find_element_by_id(WALLET_IDS.get(wallet)).click()

    print('Money lover: selecting category {category}'.format(category=category))
    wait.until(lambda d: d.find_element_by_css_selector('.v-dialog--active .category').is_displayed())
    driver.find_element_by_css_selector('.v-dialog--active .category').click()
    time.sleep(5)
    wait.until(lambda d: d.find_element_by_css_selector('[href="#tab-3"]').is_displayed())
    wait.until(lambda d: d.find_element_by_css_selector('[href="#tab-1"]').is_displayed())
    if (category['type'] == CATEGORY_TYPE['income']): driver.find_element_by_css_selector('[href="#tab-3"]').click()
    if (category['type'] == CATEGORY_TYPE['debt']): driver.find_element_by_css_selector('[href="#tab-1"]').click()
    wait.until(lambda d: d.find_element_by_id('input-search-focus').is_displayed())
    driver.find_element_by_id('input-search-focus').send_keys(category['item'])
    time.sleep(1)
    wait.until(lambda d: d.find_element_by_class_name('screen_cate_1').is_displayed())
    driver.find_element_by_class_name('screen_cate_1').click()

    print('Money lover: setting amount {amount}'.format(amount=amount))
    wait.until(lambda d: d.find_element_by_css_selector('.v-dialog--active .amount input').is_displayed())
    driver.find_element_by_css_selector('.v-dialog--active .amount input').send_keys(amount)
    driver.find_element_by_css_selector('.v-dialog--active .note input').send_keys(description)

    print('Money lover: saving transaction')
    wait.until(lambda d: d.find_element_by_css_selector('.v-dialog--active .done').is_enabled())
    driver.find_element_by_css_selector('.v-dialog--active .done').click()
    print('Money lover: adding transaction process finished for wallet {wallet}'.format(wallet=wallet))
    time.sleep(5)
