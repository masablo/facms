from datetime import datetime, timedelta
import config
import subprocess
import re
import time
import urllib.parse

import chromedriver_binary
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_options(options):
    # options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    options.add_argument('--start-maximized')
    options.add_argument('window-size=1600,1000')
    # options.add_argument('--kiosk')  # maximize window
    # options.add_argument('download.default_directory=./data/analytics/')
    # options.add_argument('--headless')
    return options


def get_pin():
    two_step_authentication = ['oathtool', '--totp', '--base32', config.PIN]
    pin = re.findall(r'\d+', subprocess.check_output(two_step_authentication).decode('utf-8'))
    return pin[0] if len(pin) > 0 else None


def change_download_folder(driver):
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {
        'cmd': 'Page.setDownloadBehavior',
        'params': {
            'behavior': 'allow',
            'downloadPath': './data/analytics/'
        }
    }
    driver.execute("send_command", params=params)


def login(driver):
    driver.get('https://www.google.com/accounts?hl=ja-JP')
    WebDriverWait(driver, MAX_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, identifierNext)))
    input_mail = driver.find_element_by_name('identifier')
    input_mail.send_keys(config.EMAIL)
    driver.find_element_by_xpath(identifierNext).click()
    WebDriverWait(driver, MAX_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, passwordNext)))
    input_password = driver.find_element_by_name('password')
    input_password.send_keys(config.PASSWORD)
    driver.find_element_by_xpath(passwordNext).click()
    WebDriverWait(driver, MAX_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, totpNext)))
    pin = get_pin()
    input_pin = driver.find_element_by_name('totpPin')
    input_pin.send_keys(pin)
    driver.find_element_by_xpath(totpNext).click()
    driver.implicitly_wait(10)


def initialize():
    chromeOptions = webdriver.ChromeOptions()
    options = get_options(chromeOptions)
    options.add_experimental_option("prefs", {"download.default_directory": './data/analytics/',
                                              "download.prompt_for_download": False,
                                              "download.directory_upgrade": True,
                                              "safebrowsing.enabled": True})
    # desired_caps = {"prefs": {
    #     "download": {
    #        "default_directory": './data/analytics/',
    #        "directory_upgrade": "true",
    #        "extensions_to_open": ""
    #     }
    # }}
    # driver = webdriver.Chrome(options=options, desired_capabilities=desired_caps)
    driver = webdriver.Chrome(options=options)
    change_download_folder(driver)
    login(driver)
    return driver


def download_file(driver):
    query = urllib.parse.urlencode({'params': '_u..nav%3Dga1-experimental',
                                    '_r.explorerCard..selmet': '["screenPageViews"]',
                                    '_r.explorerCard..seldim': '["unifiedScreenName"]',
                                    '_r.zv6ciphI1..seldim.0': 'unifiedScreenName',
                                    '_r..title': 'ページ タイトルとスクリーン名',
                                    '_u.dateOption': 'yesterday',
                                    '_u.comparisonOption': 'disabled'})
    # q = urllib.parse.quote(query)
    ANALYTICS_URL = 'https://analytics.google.com/analytics/web/?hl=ja#/p{}/reports/explorer?{}'.format(config.PROJECT_ID, query)
    driver.get(ANALYTICS_URL.replace('&', '%26'))
    WebDriverWait(driver, MAX_WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, md_form)))
    # WebDriverWait(driver, MAX_WAIT_TIME).until(EC.presence_of_all_elements_located((By.TAG_NAME, "script")))
    # WebDriverWait(driver, MAX_WAIT_TIME).until(EC.presence_of_all_elements_located)
    # WebDriverWait(driver, MAX_WAIT_TIME).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, iframe)))
    driver.find_element_by_xpath(share).click()
    WebDriverWait(driver, MAX_WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, right_panel)))
    driver.find_element_by_xpath(csv_share).click()
    WebDriverWait(driver, MAX_WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, export_button)))
    driver.find_element_by_xpath(export_button).click()
    time.sleep(5)
    driver.close()


if __name__ == '__main__':
    MAX_WAIT_TIME = 30
    identifierNext = '//*[@id="identifierNext"]'
    passwordNext = '//*[@id="passwordNext"]'
    totpNext = '//*[@id="totpNext"]'
    # loader = '//div[@class="ga-loader" and @data-loaded="true"]'
    # rect = '//rect[contains(@class, "hover-rect")]'
    # iframe = '//iframe[contains(@id, "apiproxy")]'
    md_form = '//mat-form-field[@appearance="standard"]'
    share = '//button[@aria-label="このレポートを共有"]'
    right_panel = '//right-panel'
    csv_share = '//button[contains(@class, "button-goto-export")]'
    export_button = '//button[contains(@class, "button-export-csv")]'

    driver = initialize()
    download_file(driver)
