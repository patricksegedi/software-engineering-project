# test_user_repository.py
import unittest
from repositories.UserDboRepository import UserDboRepository
from dotenv import load_dotenv
import os
from model.UserDbo import UserDbo   # adjust import if needed

# 💡 Better: read from env vars or config in real projects
DB_HOST = "smarterspeaker-smarterspeaker.k.aivencloud.com"
DB_USER = "avnadmin"
DB_PASSWORD = "CHANGE_ME"
DB_DATABASE = "smarterspeaker"
DB_PORT="28796"



class test_user_repository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        load_dotenv()

        """Runs once before ALL tests."""
        cls.repo = UserDboRepository(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            port=os.getenv("DB_PORT")
        )

    @classmethod
    def tearDownClass(cls):
        """Runs once after ALL tests."""
        cls.repo.close()

    def test_connection_is_alive(self):
        """Test basic DB connection."""
        # mysql.connector connections have is_connected()
        self.assertTrue(self.repo.conn.is_connected(), "DB connection is not active")

        # execute a simple query
        self.repo.cursor.execute("SELECT 1")
        result = self.repo.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertIn(1, result.values() if isinstance(result, dict) else result)

    def test_create_and_get_user(self):
        """Test createUser and getUser."""
        # Create a dummy user object
        user = UserDbo(
            name="Test User",
            role="tester",
            email="testuser@example.com",
            phone_number="1234567890",
            password="secret",
            restriction_list=None
        )

        # Create user
        new_id = self.repo.createUser(user)
        self.assertIsNotNone(new_id)

        # Get user
        db_user = self.repo.getUser(new_id)
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user["name"], user.name)
        self.assertEqual(db_user["role"], user.role)
        self.assertEqual(db_user["email"], user.email)

        # cleanup
        self.repo.deleteUser(new_id)

    def test_update_user(self):
        """Test updateUser behavior."""
        # Create user first
        user = UserDbo(
            name="Old Name",
            role="old_role",
            email="old@example.com",
            phone_number="111",
            password="pw",
            restriction_list=None
        )
        user_id = self.repo.createUser(user)

        # Update user
        self.repo.updateUser(
            userId=user_id,
            name="New Name",
            role="new_role",
            email="new@example.com",
            phone_number="222",
            password="new_pw",
            restriction_list=0
        )

        # Fetch again
        updated = self.repo.getUser(user_id)
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "New Name")
        self.assertEqual(updated["role"], "new_role")
        self.assertEqual(updated["email"], "new@example.com")
        self.assertEqual(updated["phone_number"], "222")
        self.assertEqual(updated["restriction_list"], 0)

        # cleanup
        self.repo.deleteUser(user_id)

    def test_list_and_delete_user(self):
        """Test listUsers + deleteUser."""
        # Create user
        user = UserDbo(
            name="List Test",
            role="test_role",
            email="list@test.com",
            phone_number="333",
            password="pw",
            restriction_list=None
        )
        user_id = self.repo.createUser(user)

        # List users -> check our user is in there
        users = self.repo.listUsers()
        ids = [u["id"] for u in users]
        self.assertIn(user_id, ids)

        # Delete user
        self.repo.deleteUser(user_id)

        # Ensure it's gone
        deleted = self.repo.getUser(user_id)
        self.assertIsNone(deleted)


if __name__ == "__main__":
    unittest.main()
