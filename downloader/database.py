import sqlite3

class DatabaseManager:
    def __init__(self, db_path: str = "downloads.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS downloads (
                id TEXT PRIMARY KEY,
                url TEXT,
                filename TEXT,
                total_size INTEGER,
                downloaded INTEGER,
                status TEXT
            )
        """)
        self.conn.commit()

    def save_task(self, task_id, url, filename, total, downloaded, status):
        query = """
            INSERT OR REPLACE INTO downloads (id, url, filename, total_size, downloaded, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(query, (task_id, url, filename, total, downloaded, status))
        self.conn.commit()

    def get_tasks(self):
        cursor = self.conn.execute("SELECT * FROM downloads")
        return [dict(row) for row in cursor.fetchall()]

    def remove_task(self, task_id):
        self.conn.execute("DELETE FROM downloads WHERE id = ?", (task_id,))
        self.conn.commit()