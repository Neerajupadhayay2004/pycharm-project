import sqlite3
from prettytable import PrettyTable
from datetime import datetime
from database import create_connection


def set_budget(user_id, category_id, amount, month, year):
    """Set or update a budget for a category"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Check if category exists and is an expense category
            cursor.execute('SELECT id FROM categories WHERE id=? AND type="expense"', (category_id,))
            if not cursor.fetchone():
                print("Invalid category ID or category is not an expense type.")
                return False

            # Insert or replace budget
            cursor.execute('''
            INSERT OR REPLACE INTO budgets (user_id, category_id, amount, month, year)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category_id, amount, month, year))
            conn.commit()
            print("Budget set successfully!")
            return True
        except Error as e:
            print(f"Error setting budget: {e}")
        finally:
            conn.close()
    return False


def get_budget_status(user_id, month, year):
    """Get budget status for the month"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Get all budgets for the month
            cursor.execute('''
            SELECT b.category_id, c.name, b.amount
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.user_id=? AND b.month=? AND b.year=?
            ''', (user_id, month, year))
            budgets = cursor.fetchall()

            if not budgets:
                print("No budgets set for this month.")
                return None

            # Get actual expenses for each budget category
            budget_status = []
            for budget in budgets:
                category_id, category_name, budget_amount = budget

                cursor.execute('''
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE user_id=? AND category_id=?
                AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
                ''', (user_id, category_id, f"{month:02d}", str(year)))
                actual_expense = cursor.fetchone()[0]

                remaining = budget_amount - actual_expense
                percentage = (actual_expense / budget_amount) * 100 if budget_amount > 0 else 0

                budget_status.append({
                    'category_id': category_id,
                    'category_name': category_name,
                    'budget': budget_amount,
                    'spent': actual_expense,
                    'remaining': remaining,
                    'percentage': percentage
                })

            # Print budget status
            print(f"\nBudget Status for {month}/{year}")
            print("=" * 40)

            table = PrettyTable()
            table.field_names = ["Category", "Budget", "Spent", "Remaining", "Percentage"]

            for status in budget_status:
                percentage_str = f"{status['percentage']:.1f}%"
                if status['percentage'] > 100:
                    percentage_str = f"\033[91m{percentage_str}\033[0m"  # Red color for exceeded
                elif status['percentage'] > 80:
                    percentage_str = f"\033[93m{percentage_str}\033[0m"  # Yellow color for warning

                table.add_row([
                    status['category_name'],
                    f"${status['budget']:.2f}",
                    f"${status['spent']:.2f}",
                    f"${status['remaining']:.2f}",
                    percentage_str
                ])

            print(table)

            # Check for exceeded budgets
            exceeded = [s for s in budget_status if s['remaining'] < 0]
            if exceeded:
                print("\n\033[91mWarning: Budget exceeded for categories:\033[0m")
                for category in exceeded:
                    print(f"- {category['category_name']} (over by ${-category['remaining']:.2f})")

            return budget_status
        except Error as e:
            print(f"Error getting budget status: {e}")
        finally:
            conn.close()
    return None