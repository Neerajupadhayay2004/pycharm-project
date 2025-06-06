import unittest
import sqlite3
import os
from auth import hash_password, register_user, login_user
from transactions import add_transaction, list_transactions
from database import create_connection


class TestFinanceApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test database
        cls.test_db = "test_finance.db"
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()

        # Create tables (simplified for testing)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
        ''')

        # Insert test data
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       ("testuser", hash_password("testpass")))

        cursor.execute("INSERT INTO categories (name, type) VALUES (?, ?)",
                       ("Test Income", "income"))

        cursor.execute("INSERT INTO categories (name, type) VALUES (?, ?)",
                       ("Test Expense", "expense"))

        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        # Remove test database
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_user_registration(self):
        # Test successful registration
        result = register_user("newuser", "newpass", db_file=self.test_db)
        self.assertTrue(result)

        # Test duplicate username
        result = register_user("newuser", "anotherpass", db_file=self.test_db)
        self.assertFalse(result)

    def test_user_login(self):
        # Test successful login
        user_id = login_user("testuser", "testpass", db_file=self.test_db)
        self.assertIsNotNone(user_id)

        # Test wrong password
        user_id = login_user("testuser", "wrongpass", db_file=self.test_db)
        self.assertIsNone(user_id)

        # Test nonexistent user
        user_id = login_user("nonexistent", "pass", db_file=self.test_db)
        self.assertIsNone(user_id)

    def test_transactions(self):
        # Add a transaction
        result = add_transaction(1, 1, 100.0, "Test transaction", db_file=self.test_db)
        self.assertTrue(result)

        # List transactions
        transactions = list_transactions(1, db_file=self.test_db)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][2], 100.0)  # Check amount


if __name__ == '__main__':
    unittest.main()