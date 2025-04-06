from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 1)
}

def read_file(**kwargs):
    """
    Функция считывает содержимое файла text.txt и сохраняет его в XCom.
    """
    file_path = '/opt/airflow/dags/text.txt'

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Сохраняем содержимое в XCom
    kwargs['ti'].xcom_push(key='text_content', value=content)
    print("Содержимое файла прочитано.")

def append_greeting(**kwargs):
    """
    Функция получает исходный текст из XCom, добавляет к нему строку с приветствием и текущей датой/временем,
    а затем сохраняет результат и дату для формирования имени файла в XCom.
    """
    ti = kwargs['ti']
    text = ti.xcom_pull(key='text_content', task_ids='read_file_task')
    now = datetime.now()
    # Форматируем дату и время для вывода и для имени файла
    date_str = now.strftime('%Y-%m-%d %H:%M:%S')
    file_date_str = now.strftime('%Y%m%d_%H%M%S')
    greeting = f"\nПривет! Текущая дата и время: {date_str}"
    new_text = text + greeting
    # Добавляем текущий путь к файлу для сохранения
    new_text += f"\n\n(Этот файл был запущен в директории {os.getcwd()}.)"

    # Сохраняем изменённый текст и строку с датой для имени файла в XCom
    ti.xcom_push(key='new_text', value=new_text)
    ti.xcom_push(key='file_date_str', value=file_date_str)
    print("К тексту добавлено приветствие и текущая дата/время.")

def write_file(**kwargs):
    """
    Функция получает обработанный текст и строку с датой из XCom,
    затем сохраняет результат в новый файл с именем result_<дата и время>.txt.
    """
    ti = kwargs['ti']
    new_text = ti.xcom_pull(key='new_text', task_ids='append_greeting_task')
    file_date_str = ti.xcom_pull(key='file_date_str', task_ids='append_greeting_task')
    output_filename = f"/opt/airflow/dags/result_{file_date_str}.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f"Новый файл сохранён: {output_filename}")

with DAG(
    dag_id='file_processing_dag',
    tags=['ETL', 'test'],  # Теги для удобства поиска DAG
    default_args=default_args,
    # schedule_interval='*/5 * * * *',  # Запуск каждые 5 минут
    schedule_interval=None,  # Отключаем автоматический запуск
    catchup=False,
    description='DAG для чтения файла, добавления приветствия с датой и сохранения нового файла'
) as dag:

    read_file_task = PythonOperator(
        task_id='read_file_task',
        python_callable=read_file,
        # Передача контекста позволяет использовать kwargs['ti'] для XCom
        provide_context=True
    )

    append_greeting_task = PythonOperator(
        task_id='append_greeting_task',
        python_callable=append_greeting,
        provide_context=True
    )

    write_file_task = PythonOperator(
        task_id='write_file_task',
        python_callable=write_file,
        provide_context=True
    )

    # Определяем последовательность задач
    read_file_task >> append_greeting_task >> write_file_task
