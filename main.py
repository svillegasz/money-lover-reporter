import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import time

# driver = webdriver.Firefox()
driver = webdriver.Remote(
   command_executor='http://0.0.0.0:4444/wd/hub',
   desired_capabilities={'browserName': 'chrome'})

wait = WebDriverWait(driver, 10)



driver.get('https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27')
time.sleep(3)
driver.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()
driver.find_element_by_xpath('//input[@type="email"]').send_keys(os.getenv('GOOGLE_USER'))
driver.find_element_by_xpath('//*[@id="identifierNext"]').click()
time.sleep(3)
driver.find_element_by_xpath('//input[@type="password"]').send_keys(os.getenv('GOOGLE_PASSWORD'))
driver.find_element_by_xpath('//*[@id="passwordNext"]').click()
time.sleep(2)


driver.get(os.getenv('GOOGLE_AUTH_URL'))
time.sleep(5)
driver.save_screenshot("ss1.png")
elem = driver.find_element_by_css_selector("li:first-child img")
elem.click()

time.sleep(5)
driver.save_screenshot("ss2.png")
driver.find_element_by_css_selector("body>div>div>a").click()
driver.find_element_by_css_selector("body>div>div>p:last-child>a").click()
time.sleep(5)
driver.save_screenshot("ss3.png")
driver.find_element_by_css_selector("[data-primary-action-label='Allow']>div>div:first-child button").click()
time.sleep(5)
driver.save_screenshot("ss4.png")
assert "Successfully set up Gmail push notifications." in driver.page_source

driver.close()
