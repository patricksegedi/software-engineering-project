import mysql.connector
from model.UserDbo import UserDbo

class UserDboRepository:
    def __init__(self, host, user, password, database, port):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def createUser(self, userDbo: UserDbo):
        query = """
            INSERT INTO t_user (name, role, email, phone_number, password, restriction_list)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (userDbo.name, userDbo.role, userDbo.email, userDbo.phone_number, userDbo.password, userDbo.restriction_list))
        self.conn.commit()
        return self.cursor.lastrowid

    def getUser(self, userId):
        query = "SELECT * FROM t_user WHERE id = %s"
        self.cursor.execute(query, (userId,))
        return self.cursor.fetchone()

    def updateUser(self, userId, name, role, email, phone_number, password, restriction_list=None):
        query = """
            UPDATE t_user
            SET name = %s,
                role = %s,
                restriction_list = %s,
                email = %s,
                phone_number = %s,
                password = %s
            WHERE id = %s
        """
        self.cursor.execute(
            query,
            (name, role, restriction_list, email, phone_number, password, userId)
        )
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
