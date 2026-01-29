import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pandas as pd
import numpy as np

from utils.db_connect import get_db_connection, execute_query
from utils.helpers import (
    validate_gmail, validate_mobile, validate_password, validate_name,
    validate_prediction_input, get_aqi_category, sanitize_float,
    FEATURE_ORDER, get_ist_timestamp, validate_csv_columns
)
from utils.preprocess import preprocess_data, prepare_training_data, load_preprocessor
from utils.metrics import calculate_all_metrics

from ml.train_linear import train_linear_regression, load_linear_model, predict_with_linear
from ml.train_randomforest import train_random_forest, load_rf_model, predict_with_rf, get_feature_importance as get_rf_importance
from ml.train_xgboost import train_xgboost, load_xgb_model, predict_with_xgb, get_feature_importance as get_xgb_importance
from ml.compare_models import compare_models, get_best_model, get_latest_metrics_per_model

from database.init_postgres import init_database

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'aurora-air-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'models'), exist_ok=True)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'Admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def get_dashboard_stats():
    try:
        predictions_count = execute_query(
            "SELECT COUNT(*) as count FROM predictions",
            fetchone=True
        )
        models_count = execute_query(
            "SELECT COUNT(DISTINCT modelname) as count FROM modelperformance",
            fetchone=True
        )
        data_count = execute_query(
            "SELECT COUNT(*) as count FROM airdata",
            fetchone=True
        )
        users_count = execute_query(
            "SELECT COUNT(*) as count FROM users",
            fetchone=True
        )
        
        return {
            'total_predictions': predictions_count['count'] if predictions_count else 0,
            'models_trained': models_count['count'] if models_count else 0,
            'data_records': data_count['count'] if data_count else 0,
            'total_users': users_count['count'] if users_count else 0
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {'total_predictions': 0, 'models_trained': 0, 'data_records': 0, 'total_users': 0}


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        valid, msg = validate_name(name)
        if not valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        valid, msg = validate_gmail(email)
        if not valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        valid, msg = validate_mobile(mobile)
        if not valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        valid, msg = validate_password(password, confirm_password)
        if not valid:
            flash(msg, 'error')
            return render_template('register.html')
        
        try:
            existing = execute_query(
                "SELECT userid FROM users WHERE email = %s OR mobile = %s",
                (email, mobile),
                fetchone=True
            )
            if existing:
                flash('Email or mobile number already registered.', 'error')
                return render_template('register.html')
            
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            execute_query(
                """INSERT INTO users (name, email, mobile, passwordhash, role)
                   VALUES (%s, %s, %s, %s, 'User')""",
                (name, email, mobile, password_hash)
            )
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Registration failed. Please try again.', 'error')
            print(f"Registration error: {e}")
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')
        
        try:
            user = execute_query(
                "SELECT userid, name, email, passwordhash, role FROM users WHERE email = %s",
                (email,),
                fetchone=True
            )
            
            if user and check_password_hash(user['passwordhash'], password):
                session['user_id'] = user['userid']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                session['role'] = user['role']
                
                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            flash('Login failed. Please try again.', 'error')
            print(f"Login error: {e}")
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    stats = get_dashboard_stats()
    
    try:
        recent_predictions = execute_query(
            """SELECT p.*, u.email as user_email 
               FROM predictions p 
               LEFT JOIN users u ON p.userid = u.userid
               WHERE p.userid = %s
               ORDER BY p.createdat DESC 
               LIMIT 5""",
            (session['user_id'],),
            fetch=True
        )
        
        for pred in recent_predictions or []:
            _, color, _ = get_aqi_category(pred['predictedaqi'])
            pred['color'] = color
            
    except Exception as e:
        recent_predictions = []
        print(f"Error fetching predictions: {e}")
    
    best_model_name, best_model_metrics = get_best_model()
    best_model = None
    if best_model_name:
        best_model = {
            'name': best_model_name,
            'metrics': best_model_metrics
        }
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_predictions=recent_predictions or [],
                         best_model=best_model)


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    prediction = None
    
    if request.method == 'POST':
        model_choice = request.form.get('model', 'XGBoost')
        
        features = {}
        errors = []
        
        for feature in FEATURE_ORDER:
            field_name = feature.lower().replace(' ', '_')
            value = request.form.get(field_name, '')
            valid, converted, msg = validate_prediction_input(value, feature)
            
            if not valid:
                errors.append(msg)
            else:
                features[feature] = converted
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('predict.html', prediction=None)
        
        try:
            preprocessor = load_preprocessor()
            if preprocessor is None:
                flash('Models not trained yet. Please ask admin to train models first.', 'warning')
                return render_template('predict.html', prediction=None)
            
            X = preprocess_data(features)
            
            if model_choice == 'Linear Regression':
                aqi_pred = predict_with_linear(X)[0]
            elif model_choice == 'Random Forest':
                aqi_pred = predict_with_rf(X)[0]
            else:
                aqi_pred = predict_with_xgb(X)[0]
            
            category, color, message = get_aqi_category(aqi_pred)
            
            execute_query(
                """INSERT INTO predictions 
                   (userid, modelused, temperature, humidity, pm2_5, pm10, co, no2, so2, o3, predictedaqi, category)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (session['user_id'], model_choice, 
                 features['Temperature'], features['Humidity'],
                 features['PM2_5'], features['PM10'],
                 features['CO'], features['NO2'],
                 features['SO2'], features['O3'],
                 float(aqi_pred), category)
            )
            
            prediction = {
                'aqi': float(aqi_pred),
                'category': category,
                'color': color,
                'message': message,
                'model': model_choice,
                'timestamp': get_ist_timestamp()
            }
            
            flash('Prediction successful!', 'success')
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('Prediction failed. Please try again.', 'error')
            print(f"Prediction error: {e}")
    
    return render_template('predict.html', prediction=prediction)


@app.route('/compare')
@login_required
def compare():
    comparison_data = compare_models()
    metrics = []
    best_model = None
    
    if comparison_data:
        try:
            result = execute_query(
                """SELECT DISTINCT ON (modelname) 
                      modelname, mae, mse, rmse, r2, createdat
                   FROM modelperformance
                   ORDER BY modelname, createdat DESC""",
                fetch=True
            )
            metrics = result if result else []
            
            if metrics:
                best_model = max(metrics, key=lambda x: x['r2'])['modelname']
        except Exception as e:
            print(f"Error fetching metrics: {e}")
    
    return render_template('compare.html',
                         comparison_data=json.dumps(comparison_data) if comparison_data else None,
                         metrics=metrics,
                         best_model=best_model)


@app.route('/insights')
@login_required
def insights():
    has_data = False
    feature_names = json.dumps(FEATURE_ORDER)
    xgb_importance = json.dumps([])
    rf_importance = json.dumps([])
    correlation_matrix = json.dumps([])
    data_stats = []
    aqi_distribution = json.dumps({})
    
    try:
        data_count = execute_query(
            "SELECT COUNT(*) as count FROM airdata",
            fetchone=True
        )
        
        if data_count and data_count['count'] > 0:
            has_data = True
            
            xgb_imp = get_xgb_importance()
            if xgb_imp:
                xgb_importance = json.dumps(xgb_imp)
            
            rf_imp = get_rf_importance()
            if rf_imp:
                rf_importance = json.dumps(rf_imp)
            
            data = execute_query(
                f"""SELECT temperature, humidity, pm2_5, pm10, co, no2, so2, o3, aqi
                    FROM airdata""",
                fetch=True
            )
            
            if data:
                df = pd.DataFrame(data)
                df.columns = [col.lower() for col in df.columns]
                
                feature_cols = ['temperature', 'humidity', 'pm2_5', 'pm10', 'co', 'no2', 'so2', 'o3']
                
                for col in feature_cols:
                    if col in df.columns:
                        stats = {
                            'feature': col.upper().replace('_', '.'),
                            'mean': float(df[col].mean()),
                            'std': float(df[col].std()),
                            'min': float(df[col].min()),
                            'max': float(df[col].max())
                        }
                        data_stats.append(stats)
                
                if all(col in df.columns for col in feature_cols):
                    corr = df[feature_cols].corr().values.tolist()
                    correlation_matrix = json.dumps(corr)
                
                if 'aqi' in df.columns:
                    dist = {}
                    for aqi in df['aqi']:
                        cat, _, _ = get_aqi_category(aqi)
                        dist[cat] = dist.get(cat, 0) + 1
                    aqi_distribution = json.dumps(dist)
                    
    except Exception as e:
        print(f"Error fetching insights: {e}")
    
    return render_template('insights.html',
                         has_data=has_data,
                         feature_names=feature_names,
                         xgb_importance=xgb_importance,
                         rf_importance=rf_importance,
                         correlation_matrix=correlation_matrix,
                         data_stats=data_stats,
                         aqi_distribution=aqi_distribution)


@app.route('/admin')
@admin_required
def admin():
    stats = get_dashboard_stats()
    
    try:
        predictions_log = execute_query(
            """SELECT p.*, u.email as user_email 
               FROM predictions p 
               LEFT JOIN users u ON p.userid = u.userid
               ORDER BY p.createdat DESC 
               LIMIT 50""",
            fetch=True
        )
        
        for pred in predictions_log or []:
            _, color, _ = get_aqi_category(pred['predictedaqi'])
            pred['color'] = color
            
        users_list = execute_query(
            "SELECT userid, name, email, mobile, role, createdat FROM users ORDER BY createdat DESC",
            fetch=True
        )
        
    except Exception as e:
        predictions_log = []
        users_list = []
        print(f"Error in admin: {e}")
    
    return render_template('admin.html',
                         stats=stats,
                         predictions_log=predictions_log or [],
                         users_list=users_list or [])


@app.route('/upload_dataset', methods=['POST'])
@admin_required
def upload_dataset():
    if 'file' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('admin'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin'))
    
    if not file.filename.endswith('.csv'):
        flash('Only CSV files are allowed.', 'error')
        return redirect(url_for('admin'))
    
    try:
        df = pd.read_csv(file)
        
        valid, msg = validate_csv_columns(df.columns.tolist())
        if not valid:
            flash(msg, 'error')
            return redirect(url_for('admin'))
        
        column_mapping = {}
        for col in df.columns:
            col_clean = col.strip().lower().replace(' ', '_')
            for feature in FEATURE_ORDER + ['AQI']:
                if col_clean == feature.lower().replace(' ', '_'):
                    column_mapping[col] = feature
                    break
        
        df = df.rename(columns=column_mapping)
        
        for col in FEATURE_ORDER + ['AQI']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=FEATURE_ORDER + ['AQI'])
        
        if len(df) == 0:
            flash('No valid data rows after cleaning.', 'error')
            return redirect(url_for('admin'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute(
                """INSERT INTO airdata (temperature, humidity, pm2_5, pm10, co, no2, so2, o3, aqi)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (float(row['Temperature']), float(row['Humidity']),
                 float(row['PM2_5']), float(row['PM10']),
                 float(row['CO']), float(row['NO2']),
                 float(row['SO2']), float(row['O3']),
                 float(row['AQI']))
            )
        
        conn.commit()
        conn.close()
        
        flash(f'Successfully uploaded {len(df)} records.', 'success')
        
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
        print(f"Upload error: {e}")
    
    return redirect(url_for('admin'))


@app.route('/train_all_models', methods=['POST'])
@admin_required
def train_all_models():
    try:
        data = execute_query(
            """SELECT temperature, humidity, pm2_5, pm10, co, no2, so2, o3, aqi
               FROM airdata""",
            fetch=True
        )
        
        if not data or len(data) < 10:
            flash('Not enough data to train models. Please upload at least 10 records.', 'error')
            return redirect(url_for('admin'))
        
        df = pd.DataFrame(data)
        df.columns = [col.capitalize() if col != 'pm2_5' and col != 'pm10' else col.upper().replace('_', '_') 
                      for col in df.columns]
        
        column_mapping = {
            'Temperature': 'Temperature',
            'Humidity': 'Humidity',
            'Pm2_5': 'PM2_5',
            'PM2_5': 'PM2_5',
            'Pm10': 'PM10',
            'PM10': 'PM10',
            'Co': 'CO',
            'CO': 'CO',
            'No2': 'NO2',
            'NO2': 'NO2',
            'So2': 'SO2',
            'SO2': 'SO2',
            'O3': 'O3',
            'Aqi': 'AQI',
            'AQI': 'AQI'
        }
        
        df = df.rename(columns=column_mapping)
        
        X_processed, y = prepare_training_data(df)
        
        linear_result = train_linear_regression(X_processed, y)
        flash(f'Linear Regression trained. R²: {linear_result["metrics"]["r2"]:.4f}', 'success')
        
        rf_result = train_random_forest(X_processed, y)
        flash(f'Random Forest trained. R²: {rf_result["metrics"]["r2"]:.4f}', 'success')
        
        xgb_result = train_xgboost(X_processed, y)
        flash(f'XGBoost trained. R²: {xgb_result["metrics"]["r2"]:.4f}', 'success')
        
    except Exception as e:
        flash(f'Training failed: {str(e)}', 'error')
        print(f"Training error: {e}")
    
    return redirect(url_for('admin'))


@app.before_request
def before_request():
    pass


@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


with app.app_context():
    try:
        init_database()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization warning: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
