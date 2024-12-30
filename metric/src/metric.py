import pika
import json
import os
import csv
from datetime import datetime

# Инициализируем CSV файл, если он не существует
logs_dir = './logs'
os.makedirs(logs_dir, exist_ok=True)
metric_log_path = os.path.join(logs_dir, 'metric_log.csv')
labels_log_path = os.path.join(logs_dir, 'labels_log.txt')

# Создание файлов
open(metric_log_path, 'a').close()
open(labels_log_path, 'a').close()

# Словарь для хранения данных
metrics_data = {}

try:
    # Подключение к RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
   
    # Создание очередей
    channel.queue_declare(queue='y_true')
    channel.queue_declare(queue='y_pred')
 
    # Callback для y_true
    def callback_y_true(ch, method, properties, body):
        message = json.loads(body)
        message_id = message['id']
        y_true = message['body']
        
        # Логирование в labels_log.txt
        with open(labels_log_path, 'a') as log:
            log.write(f'Из очереди y_true получено значение {y_true} с ID {message_id}\n')
        
        # Обновление данных
        if message_id not in metrics_data:
            metrics_data[message_id] = {}
        metrics_data[message_id]['y_true'] = y_true
        
        # Проверка наличия предсказания
        if 'y_pred' in metrics_data[message_id]:
            calculate_and_log_error(message_id)
 
    # Callback для y_pred
    def callback_y_pred(ch, method, properties, body):
        message = json.loads(body)
        message_id = message['id']
        y_pred = message['body']
        
        # Логирование в labels_log.txt
        with open(labels_log_path, 'a') as log:
            log.write(f'Из очереди y_pred получено значение {y_pred} с ID {message_id}\n')
        
        # Обновление данных
        if message_id not in metrics_data:
            metrics_data[message_id] = {}
        metrics_data[message_id]['y_pred'] = y_pred
        
        # Проверка наличия истинного значения
        if 'y_true' in metrics_data[message_id]:
            calculate_and_log_error(message_id)
    
    # Функция расчета и логирования ошибок
    def calculate_and_log_error(message_id):
        y_true = float(metrics_data[message_id]['y_true'])
        y_pred = float(metrics_data[message_id]['y_pred'])
        
        # Расчет абсолютной ошибки
        absolute_error = abs(y_true - y_pred)
        
        # Логирование в CSV
        with open(metric_log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([message_id, y_true, y_pred, absolute_error])
        
        print(f'Зарегистрирована ошибка для ID {message_id}: {absolute_error}')
        
        # Удаление обработанных данных
        del metrics_data[message_id]
 
    # Потребление сообщений
    channel.basic_consume(queue='y_true', on_message_callback=callback_y_true, auto_ack=True)
    channel.basic_consume(queue='y_pred', on_message_callback=callback_y_pred, auto_ack=True)
 
    # Запуск потребления сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except Exception as e:
    print(f'Не удалось подключиться к очереди: {e}')