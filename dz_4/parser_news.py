"""
Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
Для парсинга использовать XPath. Структура данных должна содержать:
- название источника;
- наименование новости;
- ссылку на новость;
дата публикации.
Сложить собранные новости в БД
"""

from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

client = MongoClient('127.0.0.1', 27017)
db = client['news_db']
news = db.news
news.drop()


def get_lenta_news():
    url = 'https://lenta.ru/'
    response = requests.get(url, headers=headers)

    dom = html.fromstring(response.text)
    items = dom.xpath('//div/a[contains(@class,"card-") and contains(@class,"_topnews")]')

    news_list = []
    for item in items:
        title = item.xpath('.//*[contains(@class,"_title")]/text()')[0]
        link = url + item.get('href')
        date = '.'.join([s for s in item.get('href').split('/') if s.isdigit()])
        source = 'lenta.ru'
        news_data = {
            'source': source,
            'title': title,
            'link': link,
            'date': date
        }
        news_list.append(news_data)

        # noinspection PyBroadException
        try:
            news.insert_one(news_data)
        except Exception:
            pass

    return news_list


if __name__ == '__main__':
    get_lenta_news()
    for doc in news.find({}):
        pprint(doc)