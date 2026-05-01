import psycopg2
import os

from models.document import DocumentModel
from models.folder import FolderModel

class PostgresHelper:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_PG_NAME"),
            user=os.getenv("DB_PG_USER"),
            password=os.getenv("DB_PG_PASSWORD"),
            host=os.getenv("DB_PG_HOST"),
            port=os.getenv("DB_PG_PORT")
        )
        self.cur = self.conn.cursor()

    def insert_document(self, document: DocumentModel):
        
        self.cur.execute(
            "INSERT INTO documents (filename, filepath, modifieddate, createddate, size, uids) VALUES (%s, %s, %s, %s, %s, %s);",
            (document.filename, document.filepath, document.modifieddate, document.createddate, document.size, document.uids)
        )
        self.conn.commit()

    def get_document(self, fileName, filePath):
        self.cur.execute("SELECT * FROM documents WHERE filename = %s AND filepath = %s;",
                          (fileName, filePath))
        row = self.cur.fetchone()
        if row:
            return DocumentModel(*row)
        return None

    def delete_document(self, document_id):
        try:
            self.cur.execute("DELETE FROM documents WHERE id = %s;", (document_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting document with id {document_id}: {e}")
            self.conn.rollback()
            return False
        
    def add_selected_folder(self, folder_path, source_type="local"):
        try:
            self.cur.execute(
                "INSERT INTO selected_folders (folder_path, source_type) VALUES (%s, %s) ON CONFLICT (folder_path) DO NOTHING;",
                (folder_path, source_type)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding selected folder: {e}")
            self.conn.rollback()
            return False

    def get_selected_folder(self, folder_path):
        try:
            self.cur.execute("SELECT * FROM selected_folders WHERE folder_path = %s;", (folder_path,))
            row = self.cur.fetchone()
            if row:
                return FolderModel(*row)
            return None
        except Exception as e:
            print(f"Error getting selected folder: {e}")
            return None

    def get_all_selected_folders(self):
        try:
            self.cur.execute("SELECT * FROM selected_folders ORDER BY selected_date DESC;")
            rows = self.cur.fetchall()
            return [FolderModel(*row) for row in rows]
        except Exception as e:
            print(f"Error getting selected folders: {e}")
            return []

    def delete_selected_folder(self, folder_path):
        try:
            self.cur.execute("DELETE FROM selected_folders WHERE folder_path = %s;", (folder_path,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting selected folder: {e}")
            self.conn.rollback()
            return False

    def close(self):
        self.cur.close()
        self.conn.close()