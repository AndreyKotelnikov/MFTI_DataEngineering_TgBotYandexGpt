from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import requests

# Конфигурация DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    'postgres_to_yandexdisk_telegram',
    tags=['tgbot'],
    default_args=default_args,
    schedule_interval='*/3 * * * *',
    catchup=False
) as dag:

    # 1. PythonOperator для получения данных и сохранения в XLSX
    def fetch_and_save_to_xlsx():
        postgres_hook = PostgresHook(postgres_conn_id='ya_postgres_conn')
        sql = """
            SELECT uh.id, uh.date_time, u.id as user_id, u.telegram_id as tg_user_id,
                u.username, u.name, u.sex, uh.action, uh.message
            FROM public.user_history uh
            JOIN public.users u ON uh.user_id = u.id;
        """
        # Получаем данные в виде pandas DataFrame
        df = postgres_hook.get_pandas_df(sql)

        # Преобразуем столбец datetime к наивному формату (без часового пояса)
        if 'date_time' in df.columns:
            df['date_time'] = pd.to_datetime(df['date_time']).dt.tz_localize(None)

        df.to_excel('/tmp/bot_stat.xlsx', index=False)

    fetch_and_save_excel = PythonOperator(
        task_id='fetch_and_save_excel',
        python_callable=fetch_and_save_to_xlsx
    )

    # 3. Загружаем файл на Яндекс Диск
    def upload_to_yandex_disk():
        token = Variable.get("YANDEX_DISK_API_KEY")

        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload?path=%2Ftgbot%2Fbot_stat.xlsx&overwrite=true"
        headers = {'Authorization': f"OAuth {token}"}

        response = requests.get(upload_url, headers=headers)
        href = response.json().get('href')

        with open('/tmp/bot_stat.xlsx', 'rb') as f:
            response = requests.put(href, headers=headers, files={'file': f})

        if response.status_code != 201:
            raise Exception(f"Ошибка загрузки файла: {response.text}")

    upload_file = PythonOperator(
        task_id='upload_to_yandex_disk',
        python_callable=upload_to_yandex_disk
    )

    # 4. Отправляем уведомление в Telegram
    def send_telegram_message():
        token = Variable.get("TELEGRAM_TOKEN")
        chat_id = Variable.get("TELEGRAM_CHAT_ID")
        text = "✅ Airflow DAG: файл успешно загружен на Яндекс Диск."
        print(f'chat_id = {chat_id}')

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, data={"chat_id": chat_id, "text": text})

        if response.status_code != 200:
            raise Exception(f"Ошибка отправки сообщения: {response.text}")

    send_telegram_alert = PythonOperator(
        task_id='send_telegram_alert',
        python_callable=send_telegram_message
    )

    # Последовательность выполнения задач
    fetch_and_save_excel >> upload_file >> send_telegram_alert

