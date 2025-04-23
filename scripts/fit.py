import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
import yaml
import os
import joblib

# обучение модели
def fit_model():
    # 1. Прочитайте файл с гиперпараметрами
    with open('params.yaml', 'r') as fd:
        params = yaml.safe_load(fd)

    # 2. Загрузите данные с прошлого шага
    df = pd.read_csv('data/initial_data.csv')
    X = df.drop(columns=[params['target_col']])
    y = df[params['target_col']]

    cat_cols = df.select_dtypes(include='object').columns.tolist()
    num_cols = df.select_dtypes(include='float').columns.tolist()

    preprocessor = ColumnTransformer([
        ('cat', OneHotEncoder(handle_unknown='ignore', drop=params['one_hot_drop']), cat_cols),
        ('num', StandardScaler(), num_cols)
    ], verbose_feature_names_out=False)

    model = LogisticRegression(
        C=params['model']['C'],
        penalty=params['model']['penalty'],
        max_iter=1000
    )

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])

    # 7. Обучите модель
    pipeline.fit(X, y)

    # 8. Сохраните модель
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, 'models/fitted_model.pkl')

if __name__ == '__main__':
	fit_model()