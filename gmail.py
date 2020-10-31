
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options 
from pydash import map_, get, gt
from bs4 import BeautifulSoup
from PIL import Image
import requests
import os
import time
import base64
import urllib
import traceback


GMAIL_API_URL = 'https://gmail.googleapis.com/gmail/v1'
LOGIN_URL = 'https://developers.google.com/oauthplayground/'
SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

def get_oauth_token():
    global TOKEN
    print('Gmail: Starting selenium session')
    driver = WebDriver(
        command_executor='http://0.0.0.0:4444/wd/hub',
        desired_capabilities={'browserName': 'firefox'})
    wait = WebDriverWait(driver, 10)

    print('Gmail: Starting authentication process')
    driver.get(LOGIN_URL)
    time.sleep(3)
    driver.find_element_by_id('scopes').send_keys(SCOPE)
    driver.find_element_by_id('authorizeApisButton').click()
    time.sleep(3)
    print('Gmail: Setting credentials')
    driver.find_element_by_xpath('//input[@type="email"]').send_keys(os.getenv('GOOGLE_USER'))
    driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
    time.sleep(3)
    driver.save_screenshot('login.png')
    try
        captcha = driver.find_element_by_id('captchaimg')
        urllib.request.urlretrieve(captcha.get_attribute('src'), 'captcha.png')
    except:
        traceback.print_exc()
    
    driver.save_screenshot('login2.png')
    driver.find_element_by_xpath('//input[@type="password"]').send_keys(os.getenv('GOOGLE_PASSWORD'))
    driver.find_element_by_xpath('//*[@id="passwordNext"]').click()
    time.sleep(2)
    print('Gmail: Exchanging authorization code for access token')
    driver.find_element_by_css_selector('[data-primary-action-label="Allow"]>div>div:first-child button').click()
    time.sleep(5)
    driver.find_element_by_id('exchangeCode').click()
    wait.until(lambda d: d.find_element_by_id('access_token_field').get_attribute('value'))
    TOKEN = driver.find_element_by_id('access_token_field').get_attribute('value')
    print('Gmail: Finishing authentication process: finishing gmail session')
    driver.close()

def get_messages(sender, exclude = None):
    print('Gmail api: getting messages for {sender}'.format(sender=sender))
    headers = {'Authorization': 'Bearer {token}'.format(token=TOKEN)}
    query = 'from:{sender} newer_than:1d in:inbox transacción {exclude}'.format(sender=sender, exclude='-' + exclude if exclude else '')
    params = {'q': query}
    json = requests.get('{url}/users/me/messages'.format(url=GMAIL_API_URL), headers=headers, params=params).json()
    if gt(get(json, 'resultSizeEstimate'), 0):
        print('Gmail api: Gmail messages: ', get(json, 'messages'))
        return map_(get(json, 'messages'), 'id')
    print('Gmail api: No gmail messages found')

def get_message(msg_id):
    print('Gmail api: getting message with id {msg_id}'.format(msg_id=msg_id))
    headers = {'Authorization': 'Bearer {token}'.format(token=TOKEN)}
    json = requests.get('{url}/users/me/messages/{id}'.format(url=GMAIL_API_URL, id=msg_id), headers=headers).json()
    content = get(json, 'payload.body.data')
    html = base64.urlsafe_b64decode(content).decode('utf-8')
    message = BeautifulSoup(html, 'html.parser')
    return message
