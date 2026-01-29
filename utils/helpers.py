import re
from datetime import datetime
import pytz

FEATURE_ORDER = [
    'Temperature', 'Humidity',
    'PM2_5', 'PM10',
    'CO', 'NO2',
    'SO2', 'O3'
]

IST = pytz.timezone('Asia/Kolkata')


def get_ist_now():
    """Get current datetime in IST timezone."""
    return datetime.now(IST)


def get_ist_timestamp():
    """Get formatted IST timestamp string."""
    return get_ist_now().strftime('%Y-%m-%d %H:%M:%S')


def validate_gmail(email):
    """
    Validate email is in Gmail format: username@gmail.com
    Returns tuple (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    if not re.match(pattern, email.strip().lower()):
        return False, "Email must be in format: username@gmail.com"
    
    return True, ""


def validate_mobile(mobile):
    """
    Validate mobile number is exactly 10 digits.
    Returns tuple (is_valid, error_message)
    """
    if not mobile:
        return False, "Mobile number is required"
    
    mobile = str(mobile).strip()
    if not mobile.isdigit():
        return False, "Mobile number must contain only digits"
    
    if len(mobile) != 10:
        return False, "Mobile number must be exactly 10 digits"
    
    return True, ""


def validate_password(password, confirm_password=None):
    """
    Validate password strength:
    - At least 8 characters
    - Contains uppercase, lowercase, digit, and special character
    Returns tuple (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    
    if confirm_password is not None and password != confirm_password:
        return False, "Passwords do not match"
    
    return True, ""


def validate_name(name):
    """
    Validate user name.
    Returns tuple (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"
    
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name must not exceed 100 characters"
    
    return True, ""


def validate_prediction_input(value, field_name):
    """
    Validate numeric input for prediction.
    Returns tuple (is_valid, converted_value, error_message)
    """
    if value is None or value == '':
        return False, None, f"{field_name} is required"
    
    try:
        float_val = float(value)
        return True, float_val, ""
    except (ValueError, TypeError):
        return False, None, f"{field_name} must be a valid number"


def get_aqi_category(aqi):
    """
    Get AQI category and color based on EPA standards.
    Returns tuple (category, color, health_message)
    """
    aqi = float(aqi)
    
    if aqi <= 50:
        return "Good", "#00e400", "Air quality is satisfactory. Enjoy outdoor activities."
    elif aqi <= 100:
        return "Moderate", "#ffff00", "Air quality is acceptable. Sensitive individuals should limit outdoor exertion."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#ff7e00", "Sensitive groups may experience health effects. Reduce prolonged outdoor exertion."
    elif aqi <= 200:
        return "Unhealthy", "#ff0000", "Everyone may experience health effects. Avoid prolonged outdoor exertion."
    elif aqi <= 300:
        return "Very Unhealthy", "#8f3f97", "Health alert: everyone may experience serious health effects. Stay indoors."
    else:
        return "Hazardous", "#7e0023", "Health warning: emergency conditions. Everyone should avoid all outdoor activities."


def sanitize_float(value, default=0.0):
    """
    Safely convert value to float for database insertion.
    Returns default if conversion fails.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def validate_csv_columns(columns):
    """
    Validate CSV file has required columns for training.
    Expected: 8 features + AQI
    Returns tuple (is_valid, error_message)
    """
    required_columns = FEATURE_ORDER + ['AQI']
    columns_lower = [col.strip().lower().replace(' ', '_') for col in columns]
    required_lower = [col.lower().replace(' ', '_') for col in required_columns]
    
    missing = []
    for req in required_lower:
        found = False
        for col in columns_lower:
            if req == col or req.replace('_', '') == col.replace('_', ''):
                found = True
                break
        if not found:
            missing.append(req)
    
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"
    
    return True, ""
