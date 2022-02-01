"""
Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
(необходимо анализировать оба поля зарплаты). То есть цифра вводится одна, а запрос проверяет оба поля
"""

from pprint import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']

num = 500000
currency = 'руб'

for item in db.vacancy.find({'compensation.currency': currency,
                             '$or': [{'compensation.min': {'$gt': num}},
                                     {'compensation.max': {'$gt': num}}]}):
    pprint(item)
