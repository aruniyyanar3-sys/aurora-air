# PostgreSQL Setup Guide for Aurora Air

This guide provides detailed instructions for installing and configuring PostgreSQL for the Aurora Air application.

---

## Windows Installation

### Step 1: Download PostgreSQL

1. Visit [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Click "Download the installer"
3. Choose PostgreSQL version 14 or higher (recommended: latest version)
4. Select Windows x86-64

### Step 2: Run the Installer

1. Run the downloaded `.exe` file
2. Click "Next" to proceed through the wizard
3. **Installation Directory:** Keep default or choose your preferred location
4. **Select Components:**
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4 (graphical management tool)
   - ✅ Command Line Tools
5. **Data Directory:** Keep default
6. **Password:** Set a strong password for the `postgres` superuser (REMEMBER THIS!)
7. **Port:** Keep default `5432` (unless already in use)
8. **Locale:** Default
9. Click "Next" and "Finish"

### Step 3: Verify Installation

1. Open Command Prompt
2. Run:
```bash
psql --version
```
You should see something like: `psql (PostgreSQL) 14.x`

### Step 4: Add to PATH (if needed)

If `psql` command is not found:
1. Search "Environment Variables" in Windows
2. Click "Environment Variables"
3. Under "System variables", find "Path" and click "Edit"
4. Click "New" and add: `C:\Program Files\PostgreSQL\14\bin`
5. Click "OK" to save

---

## macOS Installation

### Option A: Using Homebrew (Recommended)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Verify installation
psql --version
```

### Option B: Using Postgres.app

1. Download from [postgresapp.com](https://postgresapp.com/)
2. Move to Applications folder
3. Open Postgres.app
4. Click "Initialize" to create a new server

---

## Linux (Ubuntu/Debian) Installation

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

---

## Creating the Aurora Air Database

### Using Command Line

```bash
# Login to PostgreSQL (Windows)
psql -U postgres

# Login to PostgreSQL (Linux/macOS)
sudo -u postgres psql

# Create the database
CREATE DATABASE aurora_air;

# Create a dedicated user (optional but recommended)
CREATE USER aurora_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE aurora_air TO aurora_user;

# Exit
\q
```

### Using pgAdmin

1. Open pgAdmin 4
2. Connect to your PostgreSQL server
3. Right-click "Databases" → "Create" → "Database"
4. Enter:
   - Database: `aurora_air`
   - Owner: `postgres` (or your user)
5. Click "Save"

---

## Database Connection String

The DATABASE_URL format for Aurora Air:

```
postgresql://username:password@host:port/database_name
```

### Examples:

**Local Development (Windows/Mac/Linux):**
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/aurora_air
```

**With dedicated user:**
```
DATABASE_URL=postgresql://aurora_user:your_secure_password@localhost:5432/aurora_air
```

**Remote Server:**
```
DATABASE_URL=postgresql://username:password@your-server-ip:5432/aurora_air
```

---

## Database Schema

Aurora Air uses 4 main tables:

### 1. Users Table
Stores user authentication data
- UserID (Primary Key)
- Name, Email (Gmail only), Mobile (10 digits)
- PasswordHash (bcrypt)
- Role (User/Admin)
- CreatedAt (IST timezone)

### 2. AirData Table
Stores training data
- 8 environmental features (Temperature, Humidity, PM2.5, PM10, CO, NO2, SO2, O3)
- AQI (target variable)
- CreatedAt (IST timezone)

### 3. ModelPerformance Table
Stores ML model metrics
- ModelName (Linear Regression, Random Forest, XGBoost)
- MAE, MSE, RMSE, R² scores
- CreatedAt (IST timezone)

### 4. Predictions Table
Logs all predictions
- UserID (Foreign Key)
- ModelUsed
- 8 input features
- PredictedAQI, Category
- CreatedAt (IST timezone)

---

## Initializing the Database

After creating the database, run the initialization script:

```bash
# Navigate to project directory
cd AuroraAir

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Set environment variable
export DATABASE_URL=postgresql://postgres:password@localhost:5432/aurora_air

# Run initialization
python database/init_postgres.py
```

This creates:
- All required tables
- Default admin user (admin@gmail.com / Admin@123)

---

## Common PostgreSQL Commands

```sql
-- Connect to database
\c aurora_air

-- List all tables
\dt

-- Describe a table
\d users

-- View table contents
SELECT * FROM users;
SELECT * FROM airdata LIMIT 10;

-- Count records
SELECT COUNT(*) FROM predictions;

-- Exit psql
\q
```

---

## Timezone Configuration (IST)

Aurora Air automatically uses Indian Standard Time (IST) for all timestamps.

The database schema includes:
```sql
SET timezone = 'Asia/Kolkata';
```

All timestamps are stored with IST timezone using:
```sql
TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
```

---

## Backup and Restore

### Backup Database
```bash
pg_dump -U postgres -d aurora_air > aurora_air_backup.sql
```

### Restore Database
```bash
psql -U postgres -d aurora_air < aurora_air_backup.sql
```

---

## Troubleshooting

### Issue: "FATAL: password authentication failed"
**Solution:** 
1. Verify password is correct
2. Check pg_hba.conf for authentication method

### Issue: "could not connect to server"
**Solution:**
1. Ensure PostgreSQL service is running:
   - Windows: `services.msc` → PostgreSQL → Start
   - Linux: `sudo systemctl start postgresql`
   - macOS: `brew services start postgresql`

### Issue: "database does not exist"
**Solution:** Create the database first:
```sql
CREATE DATABASE aurora_air;
```

### Issue: "role does not exist"
**Solution:** Create the role:
```sql
CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'your_password';
```

---

## Security Best Practices

1. **Use strong passwords** for database users
2. **Never expose** PostgreSQL port (5432) to the internet
3. **Use environment variables** for credentials (never hardcode)
4. **Regular backups** of your database
5. **Keep PostgreSQL updated** for security patches

---

## Replit vs Local PostgreSQL

| Feature | Replit | Local (VS Code) |
|---------|--------|-----------------|
| Database | Managed (Neon) | Self-hosted |
| Connection | DATABASE_URL auto-set | Manual .env setup |
| Backups | Automatic | Manual |
| Port | Internal | 5432 (default) |
| SSL | Required | Optional |

When migrating from Replit to local:
1. Export data from Replit PostgreSQL
2. Import into local PostgreSQL
3. Update DATABASE_URL in .env

---

## Support

For PostgreSQL-specific issues:
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgAdmin Documentation](https://www.pgadmin.org/docs/)

For Aurora Air issues:
- Check `VS_CODE_DEPLOYMENT.md` for application setup
- Verify database connection with `python database/init_postgres.py`
