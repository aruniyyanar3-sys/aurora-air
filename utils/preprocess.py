import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import joblib

from utils.helpers import FEATURE_ORDER, sanitize_float

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, 'preprocessor.pkl')


def build_preprocessor():
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    return pipeline


def fit_preprocessor(X):
    os.makedirs(MODELS_DIR, exist_ok=True)
    preprocessor = build_preprocessor()
    preprocessor.fit(X)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    print(f"Preprocessor saved to {PREPROCESSOR_PATH}")
    return preprocessor


def load_preprocessor():
    if os.path.exists(PREPROCESSOR_PATH):
        return joblib.load(PREPROCESSOR_PATH)
    return None


def preprocess_data(data, fit=False):
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    for col in FEATURE_ORDER:
        col_lower = col.lower().replace(' ', '_')
        matching_col = None
        for c in df.columns:
            if c.lower().replace(' ', '_') == col_lower:
                matching_col = c
                break
        if matching_col and matching_col != col:
            df.rename(columns={matching_col: col}, inplace=True)

    for col in FEATURE_ORDER:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = df[col].apply(sanitize_float)

    df = df[FEATURE_ORDER]

    if fit:
        preprocessor = fit_preprocessor(df.values)
    else:
        preprocessor = load_preprocessor()
        if preprocessor is None:
            raise ValueError("No preprocessor found. Please train models first.")

    return preprocessor.transform(df.values)


def prepare_training_data(df):
    column_mapping = {}
    for col in df.columns:
        col_clean = col.strip().lower().replace(' ', '_')
        for feature in FEATURE_ORDER + ['AQI']:
            if col_clean == feature.lower().replace(' ', '_'):
                column_mapping[col] = feature
                break

    df = df.rename(columns=column_mapping)

    for col in FEATURE_ORDER:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'AQI' not in df.columns:
        raise ValueError("Missing required column: AQI")

    df['AQI'] = pd.to_numeric(df['AQI'], errors='coerce')
    df = df.dropna(subset=FEATURE_ORDER + ['AQI'])

    if len(df) == 0:
        raise ValueError("No valid data rows after cleaning")

    X = df[FEATURE_ORDER].values
    y = df['AQI'].values

    return X, y
