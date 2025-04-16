from airflow.providers.telegram.hooks.telegram import TelegramHook

def send_telegram_failure_message(context):
    hook = TelegramHook(token='8137098783:AAEcRJLe3hnKbVXC98TvP-inllalR4sSzyg', chat_id='-376739198')
    run_id = context['run_id']
    task_instance_key_str = context['task_instance_key_str']
    
    message = f'Исполнение run_id={run_id} завершилось с ошибкой: {task_instance_key_str}' # определение текста сообщения
    hook.send_message({
        'chat_id': '-376739198',
        'text': message
    }) # отправление сообщения 

def send_telegram_success_message(context):
    hook = TelegramHook(
        telegram_conn_id='test',  # Настройте соединение в Airflow
        token='8137098783:AAEcRJLe3hnKbVXC98TvP-inllalR4sSzyg',
        chat_id='-376739198'
    )
    dag_id = context['dag'].dag_id
    run_id = context['run_id']
    message = f"DAG '{dag_id}' успешно завершён! Run ID: {run_id}"
    hook.send_message({
        'chat_id': '-376739198',
        'text': message
    })
 
 