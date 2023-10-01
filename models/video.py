import sqlite3

class VideoDatabse:
    def __init__(self, db_name='recordsessions.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sessionID TEXT NOT NULL UNIQUE,
                createdAt TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_file(self, sessionID, createdAt):
        self.cursor.execute('''
            INSERT INTO files (sessionID, createdAt)
            VALUES (?, ?)
        ''', (sessionID, createdAt))
        self.conn.commit()

    def query_file(self, sessionID):
        self.cursor.execute('SELECT * FROM files WHERE sessionID = ?', (sessionID,))
        return self.cursor.fetchone()

    def query_all_files(self):
        self.cursor.execute('SELECT * FROM files')
        return self.cursor.fetchall()

    def delete_file(self, sessionID):
        self.cursor.execute('DELETE FROM files WHERE sessionID = ?', (sessionID,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()