"""
2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны.
"""
import json

import vk_api
import os
from dotenv import load_dotenv

load_dotenv('.env')
token = os.getenv('token')  # Сервисный ключ доступа

session = vk_api.VkApi(token=token)  # Авторизация
vk = session.get_api()

user_id = int(input("Введите id пользователя(цифры): "))

# проверка пользователя
# noinspection PyBroadException
try:
    data = vk.groups.get(user_id=user_id, extended=1)  # получение данных о группах пользователя
    # запись данных в файл
    if data:
        with open(f'groups_{user_id}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Данные успешно записаны в файл")
    else:
        print(f"Пользователь {user_id} не состоит в группах")
except Exception:
    print(f"Пользователь {user_id} не существует либо забанен")
