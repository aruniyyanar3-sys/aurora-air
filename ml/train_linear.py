import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from utils.metrics import calculate_all_metrics
from utils.db_connect import execute_query

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'linear_model.pkl')


def train_linear_regression(X, y, test_size=0.2, random_state=42):
    os.makedirs(MODELS_DIR, exist_ok=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = calculate_all_metrics(y_test, y_pred)

    joblib.dump(model, MODEL_PATH)
    print(f"Linear Regression model saved to {MODEL_PATH}")

    save_metrics_to_db('Linear Regression', metrics)

    return {
        'model': model,
        'metrics': metrics,
        'model_path': MODEL_PATH
    }


def save_metrics_to_db(model_name, metrics):
    try:
        execute_query("DELETE FROM modelperformance WHERE modelname = %s", (model_name,))
        execute_query(
            """INSERT INTO modelperformance (modelname, mae, mse, rmse, r2)
               VALUES (%s, %s, %s, %s, %s)""",
            (model_name, metrics['mae'], metrics['mse'],
             metrics['rmse'], metrics['r2'])
        )
        print(f"Metrics saved for {model_name}")
    except Exception as e:
        print(f"Error saving metrics: {e}")


def load_linear_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


def predict_with_linear(X):
    model = load_linear_model()
    if model is None:
        raise ValueError("Linear Regression model not found. Please train first.")
    return model.predict(X)
