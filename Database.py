import sqlite3
def create_database():
    db_file = 'AidanBugeja.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    conn.commit()
    conn.close()

def create_table(self):
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Routers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            ip_address TEXT UNIQUE NOT NULL,
            user TEXT NOT NULL,                password TEXT NOT NULL
            )
        ''')
    self.conn.commit()

create_database()
create_table()
