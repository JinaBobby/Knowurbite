import sqlite3

def update_database():
    conn = sqlite3.connect('knowurbite.db')
    c = conn.cursor()
    
    # Check if the columns already exist to avoid errors
    c.execute("PRAGMA table_info(submissions)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'audio_path' not in columns:
        print("Adding audio_path column to submissions table...")
        c.execute("ALTER TABLE submissions ADD COLUMN audio_path TEXT")
    
    if 'ingredients_text' not in columns:
        print("Adding ingredients_text column to submissions table...")
        c.execute("ALTER TABLE submissions ADD COLUMN ingredients_text TEXT")
    
    conn.commit()
    conn.close()
    print("Database update completed successfully.")

if __name__ == '__main__':
    update_database()