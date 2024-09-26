# database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='tasks.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            reminder_time TEXT,
            completed INTEGER DEFAULT 0
        )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def add_task(self, title, description, due_date, reminder_time):
        query = '''
        INSERT INTO tasks (title, description, due_date, reminder_time)
        VALUES (?, ?, ?, ?)
        '''
        self.conn.execute(query, (title, description, due_date, reminder_time))
        self.conn.commit()

    def get_tasks(self):
        query = 'SELECT * FROM tasks'
        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def delete_task(self, task_id):
        query = 'DELETE FROM tasks WHERE id=?'
        self.conn.execute(query, (task_id,))
        self.conn.commit()

    def mark_completed(self, task_id):
        query = 'UPDATE tasks SET completed=1 WHERE id=?'
        self.conn.execute(query, (task_id,))
        self.conn.commit()

    def update_task(self, task_id, title, description, due_date, reminder_time):
        query = '''
        UPDATE tasks
        SET title=?, description=?, due_date=?, reminder_time=?
        WHERE id=?
        '''
        self.conn.execute(query, (title, description, due_date, reminder_time, task_id))
        self.conn.commit()
