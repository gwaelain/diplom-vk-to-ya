import requests
from datetime import datetime
import json
from tqdm import tqdm
from pprint import pprint


def find_max_pic(sizes):
    max_size = 0
    data_max = 0
    for pic in sizes:
        if pic['height'] * pic['width'] >= max_size:
            data_max = pic
        else:
            max_size = pic['height'] * pic['width']
    return data_max['url'], data_max['type']

class VkUser:
    URL = 'https://api.vk.com/method/'
    def __init__(self, tokenVK, version='5.131'):
        self.params = {
            'access_token': tokenVK,
            'v': version
                      }
        self.id = input('Введите id пользователя vk: ')
        self.json, self.export_dict = self.sort_info()

    def get_id_by_name (self):
        get_id_URL = self.URL + 'utils.resolveScreenName'
        get_id_params = {
            'screen_name': 'begemot_korovin'
                         }
        user_id = requests.get(get_id_URL, params={**self.params, **get_id_params}).json()['response']['object_id']
        pprint(user_id)

    def get_photo_info(self):
        get_photos_by_name_URL = self.URL + 'photos.get'
        get_photos_by_name_params = \
            {
            'owner_id': self.id,
            'album_id': 'profile',
            'feed_type': 'photo',
            'photo_sizes': '1',
            'extended': '1',
            }
        res = requests.get(get_photos_by_name_URL, params={**self.params, **get_photos_by_name_params}).json()['response']
        return res['count'], res['items']

    def get_photo_params(self):
        photo_count, photo_items = self.get_photo_info()
        result = {}
        for i in range(photo_count):
            likes_count = photo_items[i]['likes']['count']
            url_download, picture_size = find_max_pic(photo_items[i]['sizes'])
            time_warp = datetime.utcfromtimestamp(int(photo_items[i]['date'])).strftime('%Y-%m-%d')
            new_value = result.get(likes_count, [])
            new_value.append({
                'likes_count': likes_count,
                              'add_name': time_warp,
                              'url_picture': url_download,
                              'size': picture_size
                             })
            result[likes_count] = new_value
        return result

    def sort_info(self):
        json_list = []
        sorted_dict = {}
        picture_dict = self.get_photo_params()
        counter = 0
        for elem in picture_dict.keys():
            for value in picture_dict[elem]:
                if len(picture_dict[elem]) == 1:
                    file_name = f'{value["likes_count"]}.jpeg'
                else:
                    file_name = f'{value["likes_count"]} {value["add_name"]}.jpeg'
                json_list.append({'file name': file_name, 'size': value["size"]})
                if value["likes_count"] == 0:
                    sorted_dict[file_name] = picture_dict[elem][counter]['url_picture']
                    counter += 1
                else:
                    sorted_dict[file_name] = picture_dict[elem][0]['url_picture']
        return json_list, sorted_dict


class YandexDisk:
    def __init__(self, folder_name, token, num=5):
        self.token = token
        self.added_pics_num = num
        self.url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        self.headers = {'Authorization': self.token}
        self.folder = self.create_folder(folder_name)

    def create_folder(self, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': folder_name}
        if requests.get(url, headers=self.headers, params=params).status_code != 200:
            requests.put(url, headers=self.headers, params=params)
            print(f'\nПапка {folder_name} успешно создана в корневом каталоге Яндекс.Диска\n')
        else:
            print(f'\nПапка {folder_name} уже существует. Файлы с одинаковыми именами не будут скопированы\n')
        return folder_name

    def get_link(self, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': folder_name}
        resource = requests.get(url, headers=self.headers, params=params).json()['_embedded']['items']
        in_folder_list = []
        for elem in resource:
            in_folder_list.append(elem['name'])
        return in_folder_list

    def create_copy(self, dict_files):
        files_in_folder = self.get_link(self.folder)
        copy_counter = 0
        for key, i in zip(dict_files.keys(), tqdm(range(self.added_pics_num))):
            if copy_counter < self.added_pics_num:
                if key not in files_in_folder:
                    params = {
                        'path': f'{self.folder}/{key}',
                              'url': dict_files[key],
                              'overwrite': 'false'
                              }
                    requests.post(self.url, headers=self.headers, params=params)
                    copy_counter += 1
                else:
                    print(f'Файл {key} уже существует')
            else:
                break
        print(f'\nЗапрос завершен, новых файлов скопировано: {copy_counter}'
              f'\nВсего файлов в исходном альбоме VK: {len(dict_files)}')


if __name__ == '__main__':
    tokenVK = ''
    vk_client = VkUser(tokenVK, '5.131')

    with open('vk_client.json', 'w') as outfile:
        json.dump(vk_client.json, outfile)

    ya = YandexDisk('vk_pictures',input('Введите токен с Полигона Яндекс.Диска: '),5)
    ya.create_copy(vk_client.export_dict)