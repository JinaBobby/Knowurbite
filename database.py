import sqlite3

def create_database():
    conn = sqlite3.connect('knowurbite.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT,
            review TEXT,
            proof_image_path TEXT,
            risk_score TEXT,
            status TEXT,
            ingredients_text TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database 'knowurbite.db' created successfully.")