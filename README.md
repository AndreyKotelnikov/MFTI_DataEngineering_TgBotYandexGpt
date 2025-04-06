# MFTI DataEngineering TgBotYandexGpt

Ссылка на телеграмм бот: https://t.me/Andrey_YandexGPT_bot

Ссылка на дашборд в datalens: https://datalens.yandex/mt2i0f7pq5jw8

Ссылка на обновляемый через airflow файл excel: https://disk.yandex.ru/i/gu6JPQ9s_SW8Uw

В боте использовано подключение к БД, вместо выгрузки в локальный файл.

Инфраструктура развёртывания в облаке Яндекса:
- Виртуальная машина compute-vm-2-2-20-ssd (запуск телеграмм бота)
- Managed Service for PostgreSQL (БД для бота, DAG и дашборда в datalens)
- airflow + dagsbucket (запуск DAG по выгрузке данных из БД и загрузки на Яндекс диск)
- datalens.yandex.cloud (визуализация статистики действий пользователей в боте)
