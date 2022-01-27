"""
Необходимо собрать информацию о вакансиях на вводимую должность
(используем input или через аргументы получаем должность)с сайтов HH(обязательно) и/или Superjob(по желанию).
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
- Наименование вакансии.
- Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
- Ссылку на саму вакансию.
- Сайт, откуда собрана вакансия (можно указать статично для hh - hh.ru, для superjob - superjob.ru)
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов.
Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.t
"""
import json

import requests
from bs4 import BeautifulSoup as bS
import pandas
import re

site = 'hh.ru'
url = f'https://{site}/search/vacancy/'

text = 'python'
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
num_page = 0
params = {
    'items_on_page': '20',
    'text': text,
    'page': num_page
}
vacancies = []

while True:
    params['page'] = num_page
    response = requests.get(url, params=params, headers=headers)
    dom = bS(response.text, 'html.parser')

    vacancies_on_page = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies_on_page:
        vacancy_title = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        vacancy_data = {
            'vacancy_title': vacancy_title.getText().replace(u'\xa0', u' '),
            'vacancy_link': vacancy_title.get('href'),
            'site': site
        }

        # noinspection PyBroadException
        try:
            vacancy_compensation = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
            vacancy_compensation = vacancy_compensation.replace(u'\xa0', u'').replace(u'\u202f', u'').strip('.')
        except Exception:
            vacancy_compensation = None

        vacancy_data['compensation_min'] = None
        vacancy_data['compensation_max'] = None
        vacancy_data['currency'] = None
        if vacancy_compensation:
            # compensation = re.sub('-', '', compensation) # not working
            # compensation = re.sub('&ndash;', '', compensation) # not working
            _compensation = re.split(r'\s+', vacancy_compensation)
            vacancy_data['currency'] = _compensation[-1]

            if _compensation[0] == 'от':
                vacancy_data['compensation_min'] = _compensation[1]
            elif _compensation[0] == 'до':
                vacancy_data['compensation_max'] = _compensation[1]
            else:
                vacancy_data['compensation_min'] = _compensation[0]
                vacancy_data['compensation_max'] = _compensation[2]

        vacancy_employer = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'})
        vacancy_data['employer'] = vacancy_employer.getText().replace(u'\xa0', u'')
        # noinspection PyBroadException
        try:
            employer_hrf = vacancy_employer.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).get('href')
            vacancy_data['employer_vacancies_list'] = 'https://' + site + employer_hrf
        except Exception:
            vacancy_data['employer_vacancies_list'] = None

        vacancies.append(vacancy_data)

    # print(num_page, len(vacancies))

    if not dom.find('a', {'data-qa': 'pager-next'}):
        break
    num_page += 1

data_frame = pandas.DataFrame(vacancies)
data_frame.to_csv('vacancies.csv', encoding="utf-8-sig")

with open('vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(vacancies, f, indent=4)
