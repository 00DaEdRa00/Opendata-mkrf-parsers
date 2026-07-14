import json
import csv
import os
import requests

API_URL = 'https://opendata.mkrf.ru/v2/culture_palaces_clubs/$?f={"data.general.locale.name":{"$contain":"Волог"}}&l=1000'
STARTED_URL = "https://opendata.mkrf.ru/opendata/7705851331-culture_palaces_clubs/"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

SCRIPT_DIR = os.path.dirname(__file__)
JSON_FILE = os.path.join(SCRIPT_DIR, "data.json")
CSV_FILE = os.path.join(SCRIPT_DIR, "data.csv")

COLUMNS = [
    "data.general.name",
    "data.general.locale.name",
    "data.general.locale.timezone",
    "data.general.address.street",
    "data.general.address.comment",
    "data.general.address.fullAddress",
    "data.general.address.mapPosition",
    "data.general.description",
    "data.general.contacts.website",
    "data.general.contacts.email",
    "data.general.contacts.phones",
    "data.general.image",
    "data.general.gallery",
    "data.general.category.type",
    "data.general.category.name",
    "data.general.organization.name",
    "data.general.organization.locale.name",
    "data.general.organization.locale.timezone",
    "data.general.organization.address.street",
    "data.general.organization.address.comment",
    "data.general.organization.address.fullAddress",
    "data.general.organization.address.mapPosition",
    "data.general.organization.inn",
    "data.general.organization.type",
    "data.general.organization.subordination.name",
    "data.general.organization.subordination.timezone",
    "data.general.organization.socialGroups",
    "data.general.organization.id",
    "data.general.tags",
    "data.general.videoHostings",
    "data.general.workingSchedule.0",
    "data.general.workingSchedule.1",
    "data.general.workingSchedule.2",
    "data.general.workingSchedule.3",
    "data.general.workingSchedule.4",
    "data.general.workingSchedule.5",
    "data.general.workingSchedule.6",
    "data.general.extraFields.artType",
    "data.general.extraFields.audienceType",
    "data.general.extraFields.language",
    "data.general.extraFields.professionalLevel",
    "data.general.extraFields.virtualTour",
    "data.general.extraFields.types",
    "data.general.seances",
    "data.general.id",
    "data.general.externalInfo",
    "data.general.externalIds.eipskId",
    "data.general.externalIds.culturarf",
    "data.general.externalIds.goscatalogId",
    "data.general.externalIds.statistic",
    "data.info.createDate",
    "data.info.updateDate",
]


def fetch_data():
    try:    
        session = requests.Session()
        session.headers.update(HEADERS)
        session.get(STARTED_URL)
    
        resp = session.get(API_URL)
        print(f"opendata.mkrf.ru/v2: {resp.status_code}")
    
        resp.raise_for_status()
        raw = resp.json()
    
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

    #with open(JSON_FILE, "w", encoding="cp1251") as f:
    #    json.dump(raw, f, indent=2, ensure_ascii=False)
    #print(f"JSON saved: {JSON_FILE}")

    return raw


def flatten(obj, prefix="data"):
    result = {}
    if isinstance(obj, dict): # Если передан словарь то
        for key, value in obj.items():
            new_key = f"{prefix}.{key}" #Собираем имя по ключу
            if isinstance(value, dict) or isinstance(value, list): #Если значение внутри - словарь или список, рекурсия
                result.update(flatten(value, new_key))
            else:
                result[new_key] = value
    elif isinstance(obj, list): # Если список - делаем строкой
        result[prefix] = json.dumps(obj, ensure_ascii=False)
    else: # На всякий
        result[prefix] = obj
    return result


def get_value(flat_dict, key):
    value = flat_dict.get(key) # Получаем значение по циклу
    if value is None:
        return ""
    if isinstance(value, dict) or isinstance(value, list): # Если есть словарь или список превращаем в строку
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def convert_to_csv(items):
    with open(CSV_FILE, "w", encoding="cp1251", errors="replace", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for item in items:
            content = item.get("data", item)
            flat = flatten(content, prefix="data")
            row = {col: get_value(flat, col) for col in COLUMNS}
            writer.writerow(row)
    print(f"CSV сохранен: {CSV_FILE} ({len(items)} строк)")


def main():
    raw = fetch_data()
    items = raw if isinstance(raw, list) else raw.get("data", [])
    convert_to_csv(items)


if __name__ == "__main__":
    main()
