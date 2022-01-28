"""

"""

from pprint import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']

num = 500000

for item in db.vacancy.find({'compensation.currency': 'руб',
                             '$or': [{'compensation.min': {'$gt': num}},
                                     {'compensation.max': {'$gt': num}}]}):
    pprint(item)
