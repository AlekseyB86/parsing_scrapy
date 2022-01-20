import json, requests
from pprint import pprint

# username = 'AlekseyB86'
username = input("Введите login пользователя: ")

url = f'https://api.github.com/users/{username}/repos'

response = requests.get(url)
j_data = response.json()
if j_data:
    with open(f'repos_github_{username}.json', 'w', encoding='utf-8') as f:
        # вариант записи выборочных данных
        # j_data = [{
        #     'id': jd['id'],
        #     'full_name': jd['full_name'],
        #     'name': jd['name'],
        #     'html_url': jd['html_url'],
        #     'language': jd['language']
        # } for jd in j_data]
        # запись всего json в файл
        json.dump(j_data, f, ensure_ascii=False, indent=4)
    print(f'Список репозиториев пользователя {username} записаны в repos_github.json')
else:
    print(f'Пользователь {username} не найден')
