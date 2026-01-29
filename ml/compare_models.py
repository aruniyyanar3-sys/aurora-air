import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connect import execute_query
from utils.helpers import FEATURE_ORDER


def get_all_model_metrics():
    """
    Retrieve all model performance metrics from database.
    
    Returns:
        List of dictionaries with model metrics
    """
    try:
        result = execute_query(
            """SELECT modelname, mae, mse, rmse, r2, createdat
               FROM modelperformance
               ORDER BY createdat DESC""",
            fetch=True
        )
        return result if result else []
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return []


def get_latest_metrics_per_model():
    """
    Get the most recent metrics for each model type.
    
    Returns:
        Dictionary with model names as keys and metrics as values
    """
    try:
        result = execute_query(
            """SELECT DISTINCT ON (modelname) 
                  modelname, mae, mse, rmse, r2, createdat
               FROM modelperformance
               ORDER BY modelname, createdat DESC""",
            fetch=True
        )
        
        if result:
            return {row['modelname']: dict(row) for row in result}
        return {}
    except Exception as e:
        print(f"Error fetching latest metrics: {e}")
        return {}


def compare_models():
    """
    Compare all trained models and return structured comparison data.
    
    Returns:
        Dictionary with comparison data for charts
    """
    metrics = get_latest_metrics_per_model()
    
    if not metrics:
        return None
    
    model_names = list(metrics.keys())
    
    comparison = {
        'models': model_names,
        'mae': [metrics[m]['mae'] for m in model_names],
        'mse': [metrics[m]['mse'] for m in model_names],
        'rmse': [metrics[m]['rmse'] for m in model_names],
        'r2': [metrics[m]['r2'] for m in model_names]
    }
    
    return comparison


def get_best_model():
    """
    Determine best model based on R² score.
    
    Returns:
        Tuple (model_name, metrics) or (None, None)
    """
    metrics = get_latest_metrics_per_model()
    
    if not metrics:
        return None, None
    
    best_model = max(metrics.items(), key=lambda x: x[1]['r2'])
    return best_model[0], best_model[1]


def get_feature_names():
    """Return the standard feature order."""
    return FEATURE_ORDER
