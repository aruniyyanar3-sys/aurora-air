-- Aurora Air Database Schema
-- PostgreSQL with IST (Indian Standard Time) timezone configuration

-- Set timezone for all timestamps
SET timezone = 'Asia/Kolkata';

-- Users Table: Stores user authentication and profile data
CREATE TABLE IF NOT EXISTS users (
    userid SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    mobile VARCHAR(10) UNIQUE NOT NULL,
    passwordhash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'User',
    createdat TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
);

-- AirData Table: Stores environmental records for ML training
CREATE TABLE IF NOT EXISTS airdata (
    id SERIAL PRIMARY KEY,
    temperature REAL,
    humidity REAL,
    pm2_5 REAL,
    pm10 REAL,
    co REAL,
    no2 REAL,
    so2 REAL,
    o3 REAL,
    aqi REAL,
    createdat TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
);

-- ModelPerformance Table: Stores ML model evaluation metrics
CREATE TABLE IF NOT EXISTS modelperformance (
    id SERIAL PRIMARY KEY,
    modelname VARCHAR(50) NOT NULL,
    mae REAL,
    mse REAL,
    rmse REAL,
    r2 REAL,
    createdat TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
);

-- Predictions Table: Logs all user predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES users(userid) ON DELETE SET NULL,
    modelused VARCHAR(50),
    temperature REAL,
    humidity REAL,
    pm2_5 REAL,
    pm10 REAL,
    co REAL,
    no2 REAL,
    so2 REAL,
    o3 REAL,
    predictedaqi REAL,
    category VARCHAR(50),
    createdat TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_predictions_userid ON predictions(userid);
CREATE INDEX IF NOT EXISTS idx_modelperformance_modelname ON modelperformance(modelname);
