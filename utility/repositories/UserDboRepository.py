import mysql.connector

class UserDboRepository:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def createUser(self, name, role, restrictionLink=None):
        query = """
            INSERT INTO t_user (name, role, restriction_link)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (name, role, restrictionLink))
        self.conn.commit()
        return self.cursor.lastrowid

    def getUser(self, userId):
        query = "SELECT * FROM t_user WHERE id = %s"
        self.cursor.execute(query, (userId,))
        return self.cursor.fetchone()

    def updateUser(self, userId, name, role, restrictionLink=None):
        query = """
            UPDATE t_user
            SET name = %s,
                role = %s,
                restriction_link = %s
            WHERE id = %s
        """
        self.cursor.execute(query, (name, role, restrictionLink, userId))
        self.conn.commit()

    def deleteUser(self, employee_id):
        query = "DELETE FROM t_user WHERE id = %s"
        self.cursor.execute(query, (employee_id,))
        self.conn.commit()

    def listUsers(self):
        query = "SELECT * FROM t_user"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
