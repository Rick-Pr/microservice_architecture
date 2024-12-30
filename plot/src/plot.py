import pandas as pd
import matplotlib.pyplot as plt
import time
import os
import numpy as np
from scipy import stats

# Создаём бесконечный цикл для чтения и визуализации метрик
while True:
    try:
        # Путь к файлу с метриками
        metric_log_path = './logs/metric_log.csv'
        
        # Проверяем, существует ли файл и не пустой ли он
        if os.path.exists(metric_log_path) and os.path.getsize(metric_log_path) > 0:
            # Читаем CSV файл
            df = pd.read_csv(metric_log_path, dtype={
                'id': float, 
                'y_true': float, 
                'y_pred': float, 
                'absolute_error': float
            })
            
            # Проверяем, есть ли данные для построения графика
            if not df.empty and len(df) > 1:
                # Создаём фигуру
                plt.figure(figsize=(10, 6))
                
                # Строим гистограмму абсолютных ошибок
                plt.hist(df['absolute_error'], bins=20, edgecolor='black', alpha=0.7)
                
                # Добавляем линию плотности распределения (KDE)
                kde = stats.gaussian_kde(df['absolute_error'])
                x_range = np.linspace(df['absolute_error'].min(), df['absolute_error'].max(), 100)
                plt.plot(x_range, kde(x_range) * len(df) * (df['absolute_error'].max() - df['absolute_error'].min()) / 20, 
                         color='red', label='Распределение плотности ошибок')
                
                # Настраиваем график
                plt.title(f'Распределение абсолютных ошибок (всего наблюдений: {len(df)})')
                plt.xlabel('Абсолютная ошибка')
                plt.ylabel('Частота')
                plt.legend()
                
                # Сохраняем график
                plt.savefig('./logs/error_distribution.png')
                plt.close()
                
                print(f'Создан график распределения абсолютных ошибок на основе {len(df)} наблюдений')
        
        # Ждём перед следующей итерацией
        time.sleep(5)
    
    except Exception as e:
        print(f'Ошибка при построении графика: {e}')
        time.sleep(5)