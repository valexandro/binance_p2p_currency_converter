# Binance P2P Currency Converter
Контвертер фиатных валют через покупку и продажу USDT на бирже Binance.
Использует недокументированное Binance апи.

Помогает подобрать лучшие предложения для конвертации, в зависимости от выбранного способа перевода и размера транзакции, считает фактический курс обмена.   

## Технологии
- Python 3.7
- Django 2.2.16
- PostgreSQL
- HTMX

## Установка
Локально с БД SQLite

### Клонировать репозиторий
```
git clone git@github.com:valexandro/binance_p2p_currency_converter.git
```
### Создать и активировать виртуальное окружение, установить зависимости
```
python3.7 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
### Создать .env файл в папке /binance_p2p_converter со следующими параметрами
```
SECRET=... # секретный ключ Джанго. https://djecrety.ir/
```
### Выполнить миграции
```
python manage.py makemigrations
python manage.py migrate
```
### Заполнить базу данных валют
```
python manage.py load_data
```
### Запуск
```
python manage.py runserver
```
