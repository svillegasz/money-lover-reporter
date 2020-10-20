import os
import time
import requests
import base64
from pydash import map_, get, gt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup

DAVIVIENDA_EMAIL = 'BANCO_DAVIVIENDA@davivienda.com'
SCOTIABANK_EMAIL = 'colpatriaInforma@colpatria.com'
PSE_EMAIL = 'serviciopse@achcolombia.com.co'
GMAIL_API_URL = 'https://gmail.googleapis.com/gmail/v1'

def get_oauth_token():
    global TOKEN
    # driver = webdriver.Firefox()
    driver = webdriver.Remote(
        command_executor='http://0.0.0.0:4444/wd/hub',
        desired_capabilities={'browserName': 'chrome'})
    wait = WebDriverWait(driver, 10)

    driver.get('https://developers.google.com/oauthplayground/')
    time.sleep(3)
    driver.find_element_by_id('scopes').send_keys('https://www.googleapis.com/auth/gmail.readonly')
    driver.find_element_by_id('authorizeApisButton').click()
    time.sleep(3)
    driver.find_element_by_xpath('//input[@type="email"]').send_keys(os.getenv('GOOGLE_USER'))
    driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
    time.sleep(3)
    driver.find_element_by_xpath('//input[@type="password"]').send_keys(os.getenv('GOOGLE_PASSWORD'))
    driver.find_element_by_xpath('//*[@id="passwordNext"]').click()
    time.sleep(2)
    driver.find_element_by_css_selector('[data-primary-action-label="Allow"]>div>div:first-child button').click()
    time.sleep(5)
    driver.find_element_by_id('exchangeCode').click()
    wait.until(lambda d: d.find_element_by_id('access_token_field').get_attribute('value'))
    TOKEN = driver.find_element_by_id('access_token_field').get_attribute('value')
    driver.close()

def decode_base64(data, altchars=b'+/'):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'='* (4 - missing_padding)
    return base64.b64decode(data, altchars)

def get_gmail_messages(sender, exclude = None):
    headers = {'Authorization': 'Bearer {token}'.format(token=TOKEN)}
    query = 'from:{sender} newer_than:2d in:inbox transacción {exclude}'.format(sender=sender, exclude='-' + exclude if exclude else '')
    params = {'q': query}
    json = requests.get('{url}/users/me/messages'.format(url=GMAIL_API_URL), headers=headers, params=params).json()
    if gt(get(json, 'resultSizeEstimate'), 0):
        return map_(get(json, 'messages'), 'id')

def get_gmail_message(msg_id):
    headers = {'Authorization': 'Bearer {token}'.format(token=TOKEN)}
    json = requests.get('{url}/users/me/messages/{id}'.format(url=GMAIL_API_URL, id=msg_id), headers=headers).json()
    content = get(json, 'payload.body.data')
    html = base64.urlsafe_b64decode(content).decode('utf-8')
    message = BeautifulSoup(html, 'html.parser')
    return message

def update_davivienda_wallet(messages):
    if not messages: return
    for msg_id in messages:
        message = get_gmail_message(msg_id)

def update_scotiabank_wallet(messages):
    if not messages: return
    for msg_id in messages:
        message = get_gmail_message(msg_id)
        comercio = message.table.find_all('p')[2].string # TO DO: parsear a categoria
        monto = message.table.find_all('p')[3].string # TO DO: convertir a número

def update_pse_wallet(messages):
    if not messages: return
    for msg_id in messages:
        message = get_gmail_message(msg_id)
        print(message.table.table.find_all('span')[-1]) # TO DO: parse span to values

if __name__ == '__main__':
    get_oauth_token()
    davivienda_messages = get_gmail_messages(DAVIVIENDA_EMAIL, exclude='PSE')
    update_davivienda_wallet(davivienda_messages)
    scotiabank_messages = get_gmail_messages(SCOTIABANK_EMAIL)
    update_scotiabank_wallet(scotiabank_messages)
    pse_messages = get_gmail_messages(PSE_EMAIL)
    update_pse_wallet(pse_messages)
