"""
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и
сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172#
"""
import time
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient


chrome_options = Options()
chrome_options.add_argument("start-maximized")

login, password = input("Введите логин и пароль почты mail.ru через пробел: ").split()

with webdriver.Chrome(executable_path='./chromedriver', options=chrome_options) as driver:
    driver.implicitly_wait(10)

    driver.get('https://mail.ru')
    driver.find_element(By.NAME, 'login').send_keys(login)
    driver.find_element(By.XPATH, '//button[@data-testid="enter-password"]').click()
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.XPATH, '//button[@data-testid="login-to-mail"]').click()

    last_email = None
    emails_link = set()
    while True:
        # Входящие письма
        emails_inc = driver.find_elements(By.XPATH, '//a[contains(@class, "llc llc_normal")]')
        if last_email == emails_inc[-1]:
            break
        else:
            last_email = emails_inc[-1]

        for email in emails_inc:
            emails_link.add(email.get_attribute('href'))

        actions = ActionChains(driver)
        actions.move_to_element(emails_inc[-1])
        actions.perform()
        time.sleep(1)

    # от кого, дата отправки, тема письма, текст письма полный
    emails_list = []
    for link in emails_link:
        driver.get(link)

        email_info = {'sender': driver.find_element(By.CLASS_NAME, 'letter-contact').get_attribute('title'),
                      'date': driver.find_element(By.CLASS_NAME, 'letter__date').text,
                      'title': driver.find_element(By.CLASS_NAME, 'thread-subject').text,
                      'body_text': driver.find_element(By.CLASS_NAME, 'letter__body').text.replace(u'\u200c', '')}

        emails_list.append(email_info)

# перенос данных в БД
client = MongoClient('127.0.0.1', 27017)
db = client['email_db']
emails = db.emails
emails.drop()

# noinspection PyBroadException
try:
    for email in emails_list:
        emails.insert_one(email)
except Exception:
    pass

for doc in emails.find({}):
    pprint(doc)
