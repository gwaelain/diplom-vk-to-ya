def download_foto_vk():
    from tqdm import tqdm
    import time
    import requests
    import json
    token_vk = ''
    url_vk = 'http://api.vk.com/method/photos.get'
    params_vk = {
        'owner_id': input('Введите ID пользователя '),
        'access_token': token_vk,
        'v': '5.131',
        'album_id': 'profile',
        'count': input('Введите количество фотографий для скачивания: '),
        'extended': '1'
    }
    if params_vk['count'] == '':
        params_vk['count'] = '5'
    res = requests.get(url_vk, params=params_vk)

    token_ya = input('Введите токен c Полигона Яндекс.Диска: ')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': '{}'.format(token_ya)
              }
    dir = input('Введите название новой папки ')
    open_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    params_open_dir = {'path': f'disk:/{dir}/'}
    response_open_dir = requests.put(open_dir_url, headers=headers, params=params_open_dir)
    if response_open_dir.status_code == 201:
        print(f"Новая папка {dir} создана")
    likes_list = []
    json_list = []
    mylist = []
    for el in res.json()['response']['items']:
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        q = {}

        if el['likes']['count'] in likes_list:
            params_ya = {'url': "{}".format(el['sizes'][-1]['url']), 'path': f"disk:/{dir}/{el['likes']['count']},"
                                                                             f"{str(time.ctime(el['date'])).split()}.jpg"}
            q["file_name"] = f"{el['likes']['count']},{str(time.ctime(el['date']))}.jpg"

        else:
            params_ya = {'url': "{}".format(el['sizes'][-1]['url']), 'path': f"disk:/{dir}/{el['likes']['count']}.jpg"}
            q["file_name"] = f"{el['likes']['count']}.jpg"

        mylist.append(1)
        res = requests.post(upload_url, headers=headers, params=params_ya)
        q["size"] = el['sizes'][-1]['type']
        json_list.append(q)
        likes_list.append(el['likes']['count'])

    with open("r.json", "w+") as f:
        json.dump(json_list, f, indent=1)

    for i in tqdm(mylist):
        time.sleep(1)

    if res.status_code == 202:
        print('Скачивание успешно завершено!')

if __name__ == '__main__':
    result = download_foto_vk()