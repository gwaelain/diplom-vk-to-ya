import requests
import json
import time

VK_API_URL = 'https://api.vk.com/method/'
YA_API_URL = 'https://cloud-api.yandex.net/v1/disk/resources/'


class VKuser:
    def __init__(self, token, version='5.131'):
        self.params = {'access_token': token, 'v': version}
        self.id = None
        self.name = ''
        self.fname = ''
        self.path = ''
        self.photo_count = 0
        self.photos = {}

    def get_info(self, user=None):
        resp = requests.get(VK_API_URL + 'users.get', params=self.params | {'user_id': user}).json()['response']
        if len(resp) > 0:
            self.id = resp[0]['id']
            self.name = resp[0]['first_name']
            self.fname = resp[0]['last_name']
            self.path = self.name + '_' + self.fname + '_(id' + str(self.id) + ')_VK_profile_photos/'
            return True
        else:
            return False

    def get_profile_photos(self, count=5):
        _params = {'owner_id': self.id, 'album_id': 'profile', 'rev': 0, 'extended': 1, 'photo_size': 1, 'count': count}
        resp = requests.get(VK_API_URL + 'photos.get', params=self.params | _params)
        if resp.status_code == 200:
            self.photo_count = resp.json()['response']['count']
            self.photos = resp.json()['response']['items']
        return resp.status_code


class YaDiskUploader:
    def __init__(self, token):
        self.headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth ' + token}

    def make_dir(self, file_path):
        return requests.put(YA_API_URL, headers=self.headers, params={'path': file_path}).status_code

    def upload(self, file_path, file_url):
        requests.delete(YA_API_URL, headers=self.headers, params={'path': file_path, 'permanently': 'true'})
        resp = requests.post(YA_API_URL + 'upload', headers=self.headers, params={'path': file_path, 'url': file_url})
        if resp.status_code == 202:
            return requests.get(YA_API_URL + 'download', headers=self.headers, params={'path': file_path}).status_code
        else:
            return resp.status_code


with open('token.txt') as file:
    y_token = file.readline().strip()
    v_token = file.readline().strip()

person = VKuser(v_token)
if not person.get_info(input('Введите пользователя ВКонтакте (id/screen_name): ')):
    print("Пользователь не найден!")
    exit(404)
foto_count = input('Введите количество фотографий для скачивания (5): ')
if foto_count == '':
    foto_count = 5

print(person.name, person.fname)
code = person.get_profile_photos(count=foto_count)
if code != 200:
    print('Ошибка получения данных -', code)
    exit(code)
print('Всего фотографий в профайле -', person.photo_count)
print('Фотографий для скачивания -', len(person.photos))
fotos = []
for foto in person.photos:
    f_date = time.gmtime(foto['date'])
    fotos.append({'likes': foto['likes']['count'],
                  'name': str(foto['likes']['count']) + '.jpg',
                  'date': str(f_date.tm_mday) + '_' + str(f_date.tm_mon) + '_' + str(f_date.tm_year),
                  'time': str(f_date.tm_hour) + ':' + str(f_date.tm_min) + ':' + str(f_date.tm_sec),
                  'url': foto['sizes'][-1]['url'],
                  'height': foto['sizes'][-1]['height'],
                  'width': foto['sizes'][-1]['width']
                  })

fotos.sort(key=lambda a: a['likes'])
for i in range(len(fotos)-1):
    if fotos[i]['likes'] == fotos[i+1]['likes']:
        if fotos[i]['date'] == fotos[i+1]['date']:
            fotos[i]['name'] = str(fotos[i]['likes']) + '-' + fotos[i]['date'] + '_' + fotos[i]['time'] + '.jpg'
            fotos[i+1]['name'] = str(fotos[i+1]['likes']) + '-' + fotos[i+1]['date'] + '_' + fotos[i+1]['time'] + '.jpg'
        else:
            fotos[i]['name'] = str(fotos[i]['likes']) + '-' + fotos[i]['date'] + '.jpg'
            fotos[i+1]['name'] = str(fotos[i+1]['likes']) + '-' + fotos[i+1]['date'] + '.jpg'

ya_disk = YaDiskUploader(y_token)
code = ya_disk.make_dir(person.path)
if code != 201 and code != 409:
    print('Ошибка создания папки -', code)
    exit(code)
result = []
i = 0
for foto in fotos:
    i += 1
    print(i, 'фото - Загружаем на YaDisk.', end='')
    code = ya_disk.upload(person.path + foto['name'], foto['url'])
    if code == 200:
        result.append({"file_name": foto['name'], "size": str(foto['height']) + 'x' + str(foto['width'])})
        print(' Ok')
    else:
        print(' Ошибка -', code)
print('Загружено', len(result), 'фото')

with open('result.json', 'w') as file:
    json.dump(result, file, indent=2))