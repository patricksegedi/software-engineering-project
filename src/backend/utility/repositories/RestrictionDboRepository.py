import mysql.connector
from model import RestrictionDbo

class RestrictionDboRepository:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def create(self, restriction: RestrictionDbo):
        query = """
            INSERT INTO t_restriction (restriction_number_list)
            VALUES (%s)
        """
        self.cursor.execute(query, (restriction.restriction_number_list,))
        self.conn.commit()
        restriction.id = self.cursor.lastrowid
        return restriction

    def get(self, restriction_id):
        query = "SELECT * FROM t_restriction WHERE id = %s"
        self.cursor.execute(query, (restriction_id,))
        row = self.cursor.fetchone()

        if not row:
            return None

        return RestrictionDbo(
            id=row["id"],
            restriction_number_list=row["restriction_number_list"]
        )

    def update(self, restriction: RestrictionDbo):
        query = """
            UPDATE t_restriction
            SET restriction_number_list = %s
            WHERE id = %s
        """
        self.cursor.execute(
            query,
            (restriction.restriction_number_list, restriction.id)
        )
        self.conn.commit()

    def delete(self, restriction_id):
        query = "DELETE FROM t_restriction WHERE id = %s"
        self.cursor.execute(query, (restriction_id,))
        self.conn.commit()

    def list_all(self):
        query = "SELECT * FROM t_restriction"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        return [
            RestrictionDbo(
                id=row["id"],
                restriction_number_list=row["restriction_number_list"]
            )
            for row in rows
        ]

    def close(self):
        self.cursor.close()
        self.conn.close()
