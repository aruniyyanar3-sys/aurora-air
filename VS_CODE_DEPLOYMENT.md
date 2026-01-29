# Aurora Air - VS Code Deployment Guide

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Python 3.9 or higher** - Download from [python.org](https://www.python.org/downloads/)
2. **PostgreSQL 14 or higher** - Download from [postgresql.org](https://www.postgresql.org/download/)
3. **VS Code** - Download from [code.visualstudio.com](https://code.visualstudio.com/)
4. **Git** (optional) - For version control

---

## Step 1: Download/Clone the Project

If you have the project as a ZIP file:
1. Extract the ZIP file to your desired location
2. Open VS Code
3. Go to `File > Open Folder` and select the extracted folder

If using Git:
```bash
git clone <repository-url>
cd AuroraAir
code .
```

---

## Step 2: Set Up PostgreSQL Database

### Option A: Using pgAdmin (Graphical Interface)

1. Open pgAdmin (installed with PostgreSQL)
2. Right-click on "Databases" → "Create" → "Database"
3. Enter database name: `aurora_air`
4. Click "Save"

### Option B: Using Command Line

Open terminal/command prompt:

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE aurora_air;

# Exit
\q
```

---

## Step 3: Configure Environment Variables

1. Create a file named `.env` in the project root folder
2. Add the following content (update with your PostgreSQL credentials):

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/aurora_air
SESSION_SECRET=your-secret-key-here-make-it-long-and-random
```

**Replace:**
- `postgres` with your PostgreSQL username
- `your_password` with your PostgreSQL password
- `5432` with your PostgreSQL port (default is 5432)
- `aurora_air` with your database name

---

## Step 4: Create Virtual Environment

Open VS Code Terminal (`Ctrl + ~` or `View > Terminal`):

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal line.

---

## Step 5: Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- psycopg2-binary (PostgreSQL driver)
- pandas, numpy (data processing)
- scikit-learn (ML algorithms)
- xgboost (advanced ML model)
- joblib (model persistence)
- pytz (timezone handling)

---

## Step 6: Initialize Database

Run the database initialization script:

```bash
python database/init_postgres.py
```

This will:
- Create all required tables (users, airdata, modelperformance, predictions)
- Create the default admin user

**Default Admin Credentials:**
- Email: `admin@gmail.com`
- Password: `Admin@123`
- Mobile: `9999999999`

---

## Step 7: Run the Application

Start the Flask development server:

```bash
python app.py
```

You should see output like:
```
Database initialized successfully!
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

---

## Step 8: Access the Application

Open your web browser and go to:

```
http://127.0.0.1:5000
```

or

```
http://localhost:5000
```

---

## Step 9: First-Time Setup

1. **Login as Admin:**
   - Email: `admin@gmail.com`
   - Password: `Admin@123`

2. **Upload Sample Dataset:**
   - Go to Admin Panel
   - Upload the sample CSV from `uploads/sample_air_quality_data.csv`

3. **Train Models:**
   - Click "Train All Models" in Admin Panel
   - Wait for training to complete

4. **Make Predictions:**
   - Go to "Predict AQI" page
   - Enter environmental parameters
   - Get your AQI prediction!

---

## Troubleshooting

### Issue: "MODULE_NOT_FOUND" error
**Solution:** Ensure virtual environment is activated and run `pip install -r requirements.txt`

### Issue: Database connection error
**Solution:** 
1. Verify PostgreSQL is running
2. Check DATABASE_URL in .env file
3. Ensure database exists

### Issue: Port 5000 already in use
**Solution:** Change the port in app.py:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Issue: Models not trained
**Solution:** Login as admin and click "Train All Models" after uploading dataset

---

## Project Structure

```
AuroraAir/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── database/
│   ├── schema.sql         # Database schema
│   └── init_postgres.py   # Database initialization
├── ml/
│   ├── train_linear.py    # Linear Regression training
│   ├── train_randomforest.py  # Random Forest training
│   ├── train_xgboost.py   # XGBoost training
│   └── compare_models.py  # Model comparison
├── models/                 # Saved ML models (auto-created)
├── utils/
│   ├── db_connect.py      # Database connection helper
│   ├── helpers.py         # Validation functions
│   ├── preprocess.py      # Data preprocessing
│   └── metrics.py         # ML metrics
├── templates/             # HTML templates
├── static/
│   ├── css/aurora.css     # Aurora theme styles
│   └── js/ui.js           # Frontend JavaScript
└── uploads/               # CSV uploads
```

---

## Stopping the Application

Press `Ctrl + C` in the terminal to stop the Flask server.

To deactivate the virtual environment:
```bash
deactivate
```

---

## Support

If you encounter any issues, check:
1. All environment variables are set correctly
2. PostgreSQL is running
3. Virtual environment is activated
4. All dependencies are installed

**All timestamps in the application are in Indian Standard Time (IST).**
