import os
import sys
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_MOBILE = "9999999999"
ADMIN_NAME = "Administrator"


def init_database():
    """
    Initialize PostgreSQL database:
    - Create necessary tables
    - Apply strict validation constraints
    - Create default admin if not exists
    """
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set")
        print("➡️  Fix: Create a .env file with DATABASE_URL or set it in environment variables.")
        return False

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SET timezone = 'Asia/Kolkata';")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                userid SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL CHECK (email ~ '^[a-zA-Z0-9._%+-]+@gmail\\.com$'),
                mobile VARCHAR(10) UNIQUE NOT NULL CHECK (mobile ~ '^[0-9]{10}$'),
                passwordhash VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(20) DEFAULT 'User',
                createdat TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
            );
        """)

        cursor.execute("""
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
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modelperformance (
                id SERIAL PRIMARY KEY,
                modelname VARCHAR(50) NOT NULL,
                mae REAL,
                mse REAL,
                rmse REAL,
                r2 REAL,
                createdat TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'Asia/Kolkata')
            );
        """)

        cursor.execute("""
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
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_userid ON predictions(userid);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_modelperformance_modelname ON modelperformance(modelname);")

        print("✔ Tables verified or created successfully!")

        cursor.execute("SELECT userid FROM users WHERE email = %s", (ADMIN_EMAIL,))
        existing_admin = cursor.fetchone()

        if not existing_admin:
            password_hash = generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256')
            cursor.execute("""
                INSERT INTO users (name, email, mobile, passwordhash, role)
                VALUES (%s, %s, %s, %s, 'Admin')
            """, (ADMIN_NAME, ADMIN_EMAIL, ADMIN_MOBILE, password_hash))

            print("\n🎉 Admin user created successfully:")
            print(f"   Email     : {ADMIN_EMAIL}")
            print(f"   Password  : {ADMIN_PASSWORD}")
            print(f"   Mobile    : {ADMIN_MOBILE}\n")
        else:
            print("ℹ Admin user already exists — skipping insertion.")

        conn.close()
        print("🚀 Database initialization completed with no errors!")
        return True

    except psycopg2.Error as db_err:
        print(f"❌ PostgreSQL Database Error: {db_err}")
        return False

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    init_database()
