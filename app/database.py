import sqlite3

DB_PATH = "roleradar.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Applications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            job_url TEXT,
            salary_range TEXT,
            status TEXT CHECK(status IN ('APPLIED', 'OA_RECEIVED', 'INTERVIEWING', 'OFFER', 'REJECTED')) DEFAULT 'APPLIED',
            applied_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully without external packages!")