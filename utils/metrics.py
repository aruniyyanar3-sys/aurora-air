import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def calculate_mae(y_true, y_pred):
    """Calculate Mean Absolute Error."""
    return float(mean_absolute_error(y_true, y_pred))


def calculate_mse(y_true, y_pred):
    """Calculate Mean Squared Error."""
    return float(mean_squared_error(y_true, y_pred))


def calculate_rmse(y_true, y_pred):
    """Calculate Root Mean Squared Error."""
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def calculate_r2(y_true, y_pred):
    """Calculate R-squared (Coefficient of Determination)."""
    return float(r2_score(y_true, y_pred))


def calculate_all_metrics(y_true, y_pred):
    """
    Calculate all evaluation metrics.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
    
    Returns:
        Dictionary with MAE, MSE, RMSE, R2 values
    """
    return {
        'mae': calculate_mae(y_true, y_pred),
        'mse': calculate_mse(y_true, y_pred),
        'rmse': calculate_rmse(y_true, y_pred),
        'r2': calculate_r2(y_true, y_pred)
    }


def format_metrics_display(metrics):
    """
    Format metrics dictionary for display.
    
    Args:
        metrics: Dictionary with MAE, MSE, RMSE, R2
    
    Returns:
        Formatted string for display
    """
    return (
        f"MAE: {metrics['mae']:.4f}\n"
        f"MSE: {metrics['mse']:.4f}\n"
        f"RMSE: {metrics['rmse']:.4f}\n"
        f"R²: {metrics['r2']:.4f}"
    )
