import resource
import psycopg2
import os


class Database(object):
    """ """

    def __init__(self, dbconn=None):
        if dbconn is None:
            default_dbconn = (
                "dbname='ckan_default' user='ckan_default' "
                "host='localhost' port='5432' password='pwd_default' sslmode='disable'"
            )
            dbconn = os.getenv("POSTGRES_URI", default_dbconn)
        self.conn = psycopg2.connect(dbconn)
        self.cursor = self.conn.cursor()

    def get_cursor(self):
        return self.cursor

    def close(self):
        self.conn.close()

    def fetchall_by_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def resource_grade_update(self, resource_id, grade):
        if not resource_id or not grade:
            return False
        q = f"""UPDATE "resource"
            SET grade = '{grade}'
            WHERE id = '{resource_id}'
        """
        try:
            self.cursor.execute(f"""{q} RETURNING id, grade""")
            self.conn.commit()
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(e, end="\r")
            self.conn.rollback()
        return None
