# scripts/evaluate.py
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
import yaml
import os
import json
import joblib

def evaluate_model():
    # Прочитайте файл с гиперпараметрами params.yaml
    with open('params.yaml', 'r') as fd:
        params = yaml.safe_load(fd)
    
    # Загрузите обученную модель из файла models/fitted_model.pkl
    with open('models/fitted_model.pkl', 'rb') as fd:
        pipeline = joblib.load(fd)
    
    # Загрузите данные из файла data/initial_data.csv
    data = pd.read_csv('data/initial_data.csv')
    
    # Извлеките целевую переменную из данных
    y = data[params['target_col']]
    
    # Извлеките признаки из данных
    X = data.drop(columns=params['target_col'])
    
    # Выполните перекрестную проверку, используя StratifiedKFold и cross_validate
    cv_strategy = StratifiedKFold(n_splits=params['n_splits'])
    cv_res = cross_validate(
        pipeline,
        X,
        y,
        cv=cv_strategy,
        n_jobs=params['n_jobs'],
        scoring=params['metrics']
    )
    
    # Округлите средние значения результатов перекрестной проверки до 3 десятичных знаков
    for key, value in cv_res.items():
        cv_res[key] = round(value.mean(), 3)
    
    # Сохраните результаты перекрестной проверки в виде файла JSON с именем cv_results/cv_res.json
    os.makedirs('cv_results', exist_ok=True)
    with open('cv_results/cv_res.json', 'w') as fd:
        json.dump(cv_res, fd, indent=4)

# Определите точку входа скрипта с помощью if __name__ == '__main__': и вызовите функцию evaluate_model
if __name__ == '__main__':
    evaluate_model()