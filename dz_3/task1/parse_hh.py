"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию
   которая будет добавлять только новые вакансии в вашу базу.
"""

import requests
from bs4 import BeautifulSoup as bS
import re
from pymongo import MongoClient, errors

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
vacancy = db.vacancy

site = 'hh.ru'
url = f'https://{site}/search/vacancy/'
text = input('Какую вакансию будем искать?: ')
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
num_page = 0

# проходимся по пагинации страницы сайта
while True:
    text = 'python' if not text else text
    params = {
        'items_on_page': '20',
        'text': text,
        'page': num_page
    }
    response = requests.get(url, params=params, headers=headers)
    dom = bS(response.text, 'html.parser')

    # собираем все вакансии на странице
    vacancies_on_page = dom.find_all('div', {'class': 'vacancy-serp-item'})
    if not vacancies_on_page:
        text = input(f'По запросу {text} ничего не найдено, попробуйте поискать другую вакансию: ')
        continue

    # проходимся по каждой вакансии, вытаскиваем нужные данные и записываем их в словарь
    for item in vacancies_on_page:
        vacancy_title = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        title = vacancy_title.getText().replace(u'\xa0', u' '),  # название вакансии
        link = vacancy_title.get('href'),  # ссылка на вакансию

        # проверка наличия зарплаты
        # noinspection PyBroadException
        try:
            vacancy_compensation = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
            vacancy_compensation = vacancy_compensation.replace(u'\xa0', u'').replace(u'\u202f', u'').strip('.')
        except Exception:
            vacancy_compensation = None

        compensation = {
            'min': None,
            'max': None,
            'currency': None
        }
        if vacancy_compensation:
            # compensation = re.sub('-', '', compensation) # не удаляет -
            # compensation = re.sub('&ndash;', '', compensation) # не удаляет -
            _compensation = re.split(r'\s+',
                                     vacancy_compensation)  # ['от', 'мин', ''] или ['до', 'мах', ''] или ['мин', '-', 'мах', '']
            compensation['currency'] = _compensation[-1]  # валюта

            if _compensation[0] == 'от':
                compensation['min'] = int(_compensation[1])
            elif _compensation[0] == 'до':
                compensation['max'] = int(_compensation[1])
            else:
                compensation['min'] = int(_compensation[0])
                compensation['max'] = int(_compensation[2])

        # данные по работодателю
        vacancy_employer = item.find('div', {'class': 'vacancy-serp-item__meta-info-company'})
        employer = vacancy_employer.getText().replace(u'\xa0', u'')
        # noinspection PyBroadException
        try:
            employer_hrf = vacancy_employer.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).get('href')
            employer_vacancies_list = 'https://' + site + employer_hrf
        except Exception:
            employer_vacancies_list = None

        # data = {
        #     'name': title,
        #     'link': link,
        #     'compensation': compensation,
        #     'source': site,
        #     'employer': employer,
        #     'employer link': employer_vacancies_list,
        # }

        # pprint(data)
        # Запись данных в MongoDB
        try:
            vacancy.insert_one({
                'name': title,
                'link': link,
                'compensation': compensation,
                'source': site,
                'employer': employer,
                'employer link': employer_vacancies_list,
            })
        except errors.DuplicateKeyError:
            pass

    print(num_page,len(vacancies_on_page))

    # если страница последняя
    if not dom.find('a', {'data-qa': 'pager-next'}):
        break
    num_page += 1
