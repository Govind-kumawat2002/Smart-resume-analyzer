import sqlite3

def create_database():
    conn = sqlite3.connect('resume_classification.db')
    c = conn.cursor()
    
    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_text TEXT,
            predicted_category TEXT,
            skills TEXT,
            experience_score INTEGER,
            education_score INTEGER,
            feedback TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database initialized and table created!")


