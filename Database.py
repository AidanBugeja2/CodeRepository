import sqlite3
class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Routers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                ip_address TEXT UNIQUE NOT NULL,
                user TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()
