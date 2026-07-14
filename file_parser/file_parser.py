from datetime import datetime
import requests
import json

started_url = "https://opendata.mkrf.ru/opendata/7705851331-culture_palaces_clubs/"

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

api_url = "https://opendata.mkrf.ru/v2/"

def fetch_categories(api_url, started_url, headers):

    try:
        session = requests.Session()
        session.headers.update(headers)
        session.get(started_url)

        # Json со всеми возможными базами
        req = session.get(api_url)
        print('opendata.mkrf.ru/v2:',req.status_code, '\n')
        return session, req.json()
    except Exception as e:
        print("Возникла ошибка",e)
        return None, None

    #with open('datasets.json', 'w', encoding='utf-8') as f:
    #    json.dump(req.json(), f, indent=2, ensure_ascii=False)


def select_categories(json_data, search_base=None):
    print("Ответ от API:", json_data['status'], "\nВсего наборов:", json_data['count'])
    if search_base:
        for item in json_data['data']:
            if item["title"] == search_base:
                print()
                print("Выбранный набор:", item["title"], '\nАктуально на момент:', time_converter(item['actualTo']), '\nПоследнее изменение:', time_converter(item['lastNativeModified']),
                      '\nКатегории:', item['categories'], '\nid (dataset):', item['_id'])
                return item['_id']
    else:
        print("В search_base ничего не передано! \nВозможные варианты:\n")
        for item in json_data['data']:
            print(item['title'])
        return None

def fetch_odSchema(session, dataset_id):
    params = {
        'f': json.dumps({"dataset": f"{dataset_id}"}),
        'o[version]': -1,
    }
    try:
        req = session.get('https://opendata.mkrf.ru/v2/$schemas', params=params)
        return session, req.json()
    except Exception as e:
        print("Возникла ошибка", e)
        return None, None

    #with open('selected_base.json', 'w', encoding='utf-8') as f:
    #    json.dump(resp.json(), f, indent=2, ensure_ascii=False)

def select_odSchema(json_data, version=None):
    print("\nОтвет от API:", json_data['status'], " Варианты баз:", json_data['count']) #ответы переписать в try catch во время запроса

    if isinstance(version, int):
        if 1 <= version <= len(json_data['data']):
            item = json_data['data'][version - 1]
            print(f"Выбранная версия схемы {item['name']}")
            return item['_id'], item['name'][-1]
        else:
            print('\nВерсии не обнаружено. '
                  'Вводить следует по цифре версии e.x. 1\n'
                  'Вы можете ознакомиться с полным списком версий ниже:')
            for item in json_data['data']:
                print('\nid:', item['_id'], '\nНазвание версии', item['name'], '\nСоздан:',
                      time_converter(item["created"]))
            return None


def fetch_all_bases(session, id_version_base):
    params = {
        'f': json.dumps({"odSchema": f"{id_version_base}"}),
        'sel': 'odSchema version snapshotTime lastNativeModified isArchived downloadFormats',
        'o': json.dumps({"lastNativeModified": -1}),
    }

    try:
        resp = session.get('https://opendata.mkrf.ru/v2/$versions', params=params)
        return session, resp.json()
    except Exception as e:
        print("Возникла ошибка", e)
        return None, None
    #with open('all_bases.json', 'w', encoding='utf-8') as f:
    #     json.dump(resp.json(), f, ensure_ascii=False, indent=2)

def select_base(json_data, version=None):
    print('\nКоличество баз:', json_data['count'])
    if version is None:
        print('\nВерсия не указана. \nВывод всех версий:')
        for item in json_data['data']:
            print("\nВерсия:", item['version'], '\n_id:', item['_id'], '\ndataset:', item['dataset'], '\nodSchema:',
                  item['odSchema'],
                  '\nВремя выгрузки', time_converter(item['snapshotTime']),'\nФорматы доступные для скачивания:',
                  item['downloadFormats'], '\n')
        return None

    elif version == 'latest':
        item = json_data['data'][0]
        print("\nВерсия:", item['version'], '\n_id:', item['_id'], '\ndataset:', item['dataset'], '\nodSchema:',
              item['odSchema'],
              '\nВремя выгрузки', time_converter(item['snapshotTime']), '\nФорматы доступные для скачивания:',
              item['downloadFormats'], '\n')
        version = item['version']
        return version, item['downloadFormats']

    elif isinstance(version, int):
        for item in json_data['data']:
            if version == item["version"]:
                print("\nВерсия:", item['version'], '\n_id:', item['_id'], '\ndataset:', item['dataset'], '\nodSchema:',
                      item['odSchema'],
                      '\nВремя выгрузки', time_converter(item['snapshotTime']), '\nФорматы доступные для скачивания:',
                      item['downloadFormats'], '\n')
                return version, item['downloadFormats']

        print("Версия не найдена, список доступных:")
        print(*[item['version'] for item in json_data['data']], sep='\n')
        return None

def file_extension_parse(json_data, version, json_extensions, extension='xlsx', depth=0):
    if depth < 10:
        print('По умолчанию будет выбрана xlsx. Если такого формата нет, будет предложена старая версия.')
        if extension == 'xlsx':
            if extension in json_extensions:
                print('Выбран формат по умолчанию')
                return '.xlsx', version
            else:
                print('В этой версии xlsx не найден, поиск в старой версии...')
                versions = [item['version'] for item in json_data['data']]
                idx = versions.index(version)
                if idx + 1 >= len(versions):
                    print("Более старых версий нет")
                    return None, version
                prev_version = versions[idx + 1]
                version, json_extensions = select_base(json_data, prev_version)
                return file_extension_parse(json_data, version, json_extensions, 'xlsx', depth + 1)
        else:
            if extension in json_extensions:
                print(f"Формат {extension} найден")
                return '.' + extension, version
            else:
                print("Такого расширения файла не существует")
                return None, version
    else:
        print("Превышен лимит поиска версий")
        return None, version

def download_file(started_url, session, dataset_version, dataset_variant, extension):
    try:
        url = started_url + f'data-{dataset_version}-structure-{dataset_variant}{extension}'
        print(f'Загрузка датасета с {url}')
        resp = session.get(url, stream=True)
    except requests.RequestException as e:
        print(f"Ошибка скачивания: {e}")
        return

    total = int(resp.headers.get('content-length', 0))
    downloaded = 0

    with open(f'dataset-{dataset_version}-structure-{dataset_variant}{extension}', 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded * 100 // total
                print(f'\rЗагрузка: {pct}% ({downloaded // 1024}/{total // 1024} KB)', end='')
    print()  # перевод строки после завершения

def time_converter(time):
    try:
        t = time
        time = datetime.fromisoformat(t.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M:%S')
        return time
    except (ValueError, AttributeError):
        return time

def main(dataset_data_variant, dataset_version_main, file_extension):
    session, json_data = fetch_categories(api_url, started_url, headers)
    if session is None:
        print("Не удалось подключиться к API")
        return

    dataset_id = select_categories(json_data, 'Учреждения культурно-досугового типа')
    if dataset_id is None:
        print("Датасет не найден")
        return

    session, json_data = fetch_odSchema(session, dataset_id)
    if session is None:
        print("Не удалось получить схемы")
        return

    result = select_odSchema(json_data, dataset_data_variant)
    if result is None:
        print("Версия схемы не найдена")
        return
    id_version_base, dataset_variant = result

    session, json_data = fetch_all_bases(session, id_version_base)
    if session is None:
        print("Не удалось получить список баз")
        return

    version, json_extensions = select_base(json_data, dataset_version_main)
    if version is None:
        print("Версия базы не найдена")
        return

    extension, version = file_extension_parse(json_data, version, json_extensions, file_extension)
    if extension is None:
        print("Файл не найден")
        return

    download_file(started_url, session, version, dataset_variant, extension)

if __name__ == '__main__':
    dataset_data_variant = 3 # Версия данных датасета
    dataset_version_main = 'latest' # Также поддерживает числа, или может быть пустым для показа всех версий
    file_extension = 'xlsx' # По умолчанию 'xlsx'

    main(dataset_data_variant, dataset_version_main, file_extension)



'''
https://opendata.mkrf.ru/opendata/7705851331-culture_palaces_clubs/data-2292-structure-3.xlsx - конечная ссылка на файл
Разбор ссылки
7705851331 — это ОГРН Министерства культуры РФ
culture_palaces_clubs — учреждения культуры
2292 врерсия датасета
3 - версия данных
.xlsx - конечное расширение из json
'''
