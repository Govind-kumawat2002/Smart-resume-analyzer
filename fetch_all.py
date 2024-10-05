import sqlite3
from sqlite3 import Error

def fetch_all_records():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('resume_classification.db')
        c = conn.cursor()

        # Execute the query to fetch all records
        c.execute('SELECT * FROM resumes')
        
        # Fetch all rows
        rows = c.fetchall()
        
        # Print all rows
        for row in rows:
            print(row)
    
    except Error as e:
        print(e)
    
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == '__main__':
    fetch_all_records()
