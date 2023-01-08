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
### Создать виртуальное окружение и установить зависимости
```
python3.7 -m venv venv
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
