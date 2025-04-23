import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
import joblib
import json
import yaml
import os

# оценка качества модели
def evaluate_model():
    # 1. Прочитайте файл с гиперпараметрами
    with open('params.yaml', 'r') as fd:
        params = yaml.safe_load(fd)

    # 2. Загрузите данные
    df = pd.read_csv('data/initial_data.csv')
    X = df.drop(columns=[params['target_col']])
    y = df[params['target_col']]

    # 3. Загрузите модель через файловый дескриптор
    with open('models/fitted_model.pkl', 'rb') as fd:
        model = joblib.load(fd)

    # 4. Проведите кросс-валидацию
    cv = StratifiedKFold(n_splits=params['n_splits'])
    scoring = params['metrics']
    n_jobs = params.get('n_jobs', None)

    results = cross_validate(
        model, X, y,
        cv=cv,
        scoring=scoring,
        return_train_score=False,
        n_jobs=n_jobs
    )

    # 5. Сохраняем все метрики, включая fit_time и score_time
    avg_scores = {
        f"{k}": round(v.mean(), 4)
        for k, v in results.items()
    }

    # 6. Сохраняем результаты в JSON-файл
    os.makedirs("cv_results", exist_ok=True)
    with open("cv_results/cv_res.json", "w") as f:
        json.dump(avg_scores, f, indent=2)

    print(avg_scores)

if __name__ == '__main__':
    evaluate_model()
