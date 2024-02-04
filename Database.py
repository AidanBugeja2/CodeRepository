import sqlite3

def create_database():
    """
    Create a SQLite database file.
    """
    db_file = 'AidanBugeja.db'
    conn = sqlite3.connect(db_file)
    conn.close()

def create_table():
    """
    Create a 'Routers' table in the SQLite database.
    """
    db_file = 'AidanBugeja.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Routers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            ip_address TEXT UNIQUE NOT NULL,
            user TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Create a SQLite database file
create_database()

# Create a 'Routers' table in the SQLite database
create_table()
