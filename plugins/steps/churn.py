import sqlalchemy
from sqlalchemy import MetaData, Table, Column, String, Integer, Float, DateTime, UniqueConstraint
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
 
def create_table():
    """
    Создает таблицу в базе данных, если она не существует. Имя таблицы передается как аргумент.
    """
    hook = PostgresHook('destination_db')
    engine = hook.get_sqlalchemy_engine()
 
    metadata = MetaData()

    table_name = 'alt_users_churn'
 
    # Описание таблицы
    alt_users_churn = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('customer_id', String, nullable=False),
        Column('begin_date', DateTime),
        Column('end_date', DateTime),
        Column('type', String),
        Column('paperless_billing', String),
        Column('payment_method', String),
        Column('monthly_charges', Float),
        Column('total_charges', Float),
        Column('internet_service', String),
        Column('online_security', String),
        Column('online_backup', String),
        Column('device_protection', String),
        Column('tech_support', String),
        Column('streaming_tv', String),
        Column('streaming_movies', String),
        Column('gender', String),
        Column('senior_citizen', Integer),
        Column('partner', String),
        Column('dependents', String),
        Column('multiple_lines', String),
        Column('target', Integer),
        UniqueConstraint('customer_id', name=f'{table_name}_unique_customer_id')  # Уникальное ограничение
    )
 
    if not sqlalchemy.inspect(engine).has_table(table_name):
        metadata.create_all(engine)
        print(f"Таблица '{table_name}' успешно создана.")
    else:
        print(f"Таблица '{table_name}' уже существует.")
 
def extract(**kwargs):
    """
    Извлекает данные из исходных таблиц и отправляет их в xcom.
    """
    ti = kwargs['ti']
    hook = PostgresHook('source_db')
    conn = hook.get_conn()
    sql = f"""
    SELECT
        c.customer_id, c.begin_date, c.end_date, c.type, c.paperless_billing, c.payment_method, c.monthly_charges, c.total_charges,
        i.internet_service, i.online_security, i.online_backup, i.device_protection, i.tech_support, i.streaming_tv, i.streaming_movies,
        p.gender, p.senior_citizen, p.partner, p.dependents,
        ph.multiple_lines
    FROM contracts AS c
    LEFT JOIN internet AS i ON i.customer_id = c.customer_id
    LEFT JOIN personal AS p ON p.customer_id = c.customer_id
    LEFT JOIN phone AS ph ON ph.customer_id = c.customer_id
    """
    data = pd.read_sql(sql, conn)
    conn.close()
 
    ti.xcom_push(key='extracted_data', value=data)
 
def transform(**kwargs):
    """
    Преобразует данные, создавая целевую переменную 'target'.
    """
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract', key='extracted_data')
 
    data['target'] = (data['end_date'] != 'No').astype(int)
    data['end_date'].replace({'No': None}, inplace=True)
 
    ti.xcom_push(key='transformed_data', value=data)
 
def load(**kwargs):
    """
    Загружает данные в таблицу.
    """
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform', key='transformed_data')
 
    hook = PostgresHook('destination_db')
    rows = data.to_dict(orient='records')
 
    hook.insert_rows(
        table='alt_users_churn',
        rows=[tuple(row.values()) for row in rows],
        target_fields=list(data.columns),
        replace=True,
        replace_index="customer_id"
    )
    print("Данные успешно загружены в таблицу alt_users_churn.")