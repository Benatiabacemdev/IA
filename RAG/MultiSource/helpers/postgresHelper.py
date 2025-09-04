import psycopg2
import os

from models.document import DocumentModel

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
        
    def close(self):
        self.cur.close()
        self.conn.close()