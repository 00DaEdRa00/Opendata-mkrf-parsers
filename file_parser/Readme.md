# MKRF Open Data Parser

Парсер для скачивания.datasetов с портала открытых данных Минкультуры России
(https://opendata.mkrf.ru)

## Зависимости
pip install requests


## Запуск

```bash
python parser.py
Конфигурация
Переменные в __main__:

Переменная	Описание	Пример
dataset_data_variant	Версия данных (номер схемы)	3
dataset_version_main	Версия датасета (latest, число или None)	'latest'
file_extension	Формат файла (xlsx, csv)	'xlsx'
Структура
Функция	Назначение
fetch_categories	Получение списка всех наборов данных
select_categories	Поиск набора по названию
fetch_odSchema	Получение схем версий
select_odSchema	Выбор версии схемы
fetch_all_bases	Список всех баз по схеме
select_base	Выбор конкретной версии базы
file_extension_parse	Проверка доступности формата
download_file	Скачивание файла
time_converter	Форматирование даты ISO → dd.mm.yyyy HH:MM:SS
