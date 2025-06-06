import sqlite3
from datetime import datetime
from prettytable import PrettyTable
from database import create_connection


def add_transaction(user_id, category_id, amount, description=None):
    """Add a new transaction"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT INTO transactions (user_id, category_id, amount, description, date)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category_id, amount, description, date))
            conn.commit()
            print("Transaction added successfully!")
            return True
        except Error as e:
            print(f"Error adding transaction: {e}")
        finally:
            conn.close()
    return False


def update_transaction(transaction_id, user_id, category_id=None, amount=None, description=None):
    """Update an existing transaction"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # First verify the transaction belongs to the user
            cursor.execute('SELECT id FROM transactions WHERE id=? AND user_id=?', (transaction_id, user_id))
            if not cursor.fetchone():
                print("Transaction not found or doesn't belong to you.")
                return False

            # Build the update query based on provided fields
            updates = []
            params = []

            if category_id is not None:
                updates.append("category_id = ?")
                params.append(category_id)

            if amount is not None:
                updates.append("amount = ?")
                params.append(amount)

            if description is not None:
                updates.append("description = ?")
                params.append(description)

            if not updates:
                print("No fields to update.")
                return False

            params.append(transaction_id)
            params.append(user_id)

            query = f'''
            UPDATE transactions 
            SET {', '.join(updates)} 
            WHERE id=? AND user_id=?
            '''

            cursor.execute(query, params)
            conn.commit()
            print("Transaction updated successfully!")
            return True
        except Error as e:
            print(f"Error updating transaction: {e}")
        finally:
            conn.close()
    return False


def delete_transaction(transaction_id, user_id):
    """Delete a transaction"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Verify the transaction belongs to the user
            cursor.execute('SELECT id FROM transactions WHERE id=? AND user_id=?', (transaction_id, user_id))
            if not cursor.fetchone():
                print("Transaction not found or doesn't belong to you.")
                return False

            cursor.execute('DELETE FROM transactions WHERE id=? AND user_id=?', (transaction_id, user_id))
            conn.commit()
            print("Transaction deleted successfully!")
            return True
        except Error as e:
            print(f"Error deleting transaction: {e}")
        finally:
            conn.close()
    return False


def list_categories():
    """List all available categories"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, type FROM categories ORDER BY type, name')
            categories = cursor.fetchall()

            if not categories:
                print("No categories found.")
                return None

            table = PrettyTable()
            table.field_names = ["ID", "Category", "Type"]
            for cat in categories:
                table.add_row(cat)

            print(table)
            return categories
        except Error as e:
            print(f"Error listing categories: {e}")
        finally:
            conn.close()
    return None


def list_transactions(user_id, limit=10):
    """List recent transactions for a user"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT t.id, c.name, t.amount, t.description, t.date 
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=?
            ORDER BY t.date DESC
            LIMIT ?
            ''', (user_id, limit))
            transactions = cursor.fetchall()

            if not transactions:
                print("No transactions found.")
                return None

            table = PrettyTable()
            table.field_names = ["ID", "Category", "Amount", "Description", "Date"]
            for t in transactions:
                table.add_row(t)

            print(table)
            return transactions
        except Error as e:
            print(f"Error listing transactions: {e}")
        finally:
            conn.close()
    return None