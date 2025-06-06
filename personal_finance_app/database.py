import sqlite3
from sqlite3 import Error


def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('finance.db')
        return conn
    except Error as e:
        print(e)

    return conn


def create_tables(conn):
    """Create all necessary tables"""
    try:
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')

        # Categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense'))
        )
        ''')

        # Transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')

        # Budgets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id),
            UNIQUE(user_id, category_id, month, year)
        )
        ''')

        # Insert default categories if they don't exist
        default_categories = [
            ('Salary', 'income'),
            ('Bonus', 'income'),
            ('Investment', 'income'),
            ('Food', 'expense'),
            ('Rent', 'expense'),
            ('Transportation', 'expense'),
            ('Entertainment', 'expense'),
            ('Utilities', 'expense'),
            ('Healthcare', 'expense'),
            ('Education', 'expense'),
            ('Other', 'expense')
        ]

        cursor.executemany('''
        INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)
        ''', default_categories)

        conn.commit()
    except Error as e:
        print(e)


def initialize_database():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")


if __name__ == '__main__':
    initialize_database()
