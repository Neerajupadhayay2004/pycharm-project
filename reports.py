import sqlite3
from prettytable import PrettyTable
from datetime import datetime
from database import create_connection


def get_monthly_summary(user_id, month, year):
    """Generate monthly income/expense summary"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Get total income
            cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=? AND c.type='income' 
            AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?
            ''', (user_id, f"{month:02d}", str(year)))
            total_income = cursor.fetchone()[0]

            # Get total expenses
            cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=? AND c.type='expense' 
            AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?
            ''', (user_id, f"{month:02d}", str(year)))
            total_expenses = cursor.fetchone()[0]

            # Get income by category
            cursor.execute('''
            SELECT c.name, COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=? AND c.type='income' 
            AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?
            GROUP BY c.name
            ''', (user_id, f"{month:02d}", str(year)))
            income_by_category = cursor.fetchall()

            # Get expenses by category
            cursor.execute('''
            SELECT c.name, COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=? AND c.type='expense' 
            AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?
            GROUP BY c.name
            ''', (user_id, f"{month:02d}", str(year)))
            expenses_by_category = cursor.fetchall()

            # Calculate savings
            savings = total_income - total_expenses

            # Print summary
            print(f"\nMonthly Summary for {month}/{year}")
            print("=" * 40)
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expenses: ${total_expenses:.2f}")
            print(f"Savings: ${savings:.2f}")

            # Print income by category
            if income_by_category:
                print("\nIncome by Category:")
                table = PrettyTable()
                table.field_names = ["Category", "Amount"]
                for row in income_by_category:
                    table.add_row([row[0], f"${row[1]:.2f}"])
                print(table)

            # Print expenses by category
            if expenses_by_category:
                print("\nExpenses by Category:")
                table = PrettyTable()
                table.field_names = ["Category", "Amount"]
                for row in expenses_by_category:
                    table.add_row([row[0], f"${row[1]:.2f}"])
                print(table)

            return {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'savings': savings,
                'income_by_category': income_by_category,
                'expenses_by_category': expenses_by_category
            }
        except Error as e:
            print(f"Error generating monthly summary: {e}")
        finally:
            conn.close()
    return None


def get_yearly_summary(user_id, year):
    """Generate yearly income/expense summary"""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Get total income
            cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=? AND c.type='income' 
            AND strftime('%Y', t.date) = ?
            ''', (user_id, str(year)))
            total_income = cursor.fetchone()[0]

            # Get total expenses
            cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0)
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=? AND c.type='expense' 
            AND strftime('%Y', t.date) = ?
            ''', (user_id, str(year)))
            total_expenses = cursor.fetchone()[0]

            # Get monthly breakdown
            cursor.execute('''
            SELECT strftime('%m', t.date) as month, 
                   SUM(CASE WHEN c.type='income' THEN t.amount ELSE 0 END) as income,
                   SUM(CASE WHEN c.type='expense' THEN t.amount ELSE 0 END) as expense
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id=? AND strftime('%Y', t.date) = ?
            GROUP BY month
            ORDER BY month
            ''', (user_id, str(year)))
            monthly_breakdown = cursor.fetchall()

            # Calculate savings
            savings = total_income - total_expenses

            # Print summary
            print(f"\nYearly Summary for {year}")
            print("=" * 40)
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expenses: ${total_expenses:.2f}")
            print(f"Savings: ${savings:.2f}")

            # Print monthly breakdown
            if monthly_breakdown:
                print("\nMonthly Breakdown:")
                table = PrettyTable()
                table.field_names = ["Month", "Income", "Expenses", "Savings"]
                for row in monthly_breakdown:
                    month_name = datetime.strptime(row[0], "%m").strftime("%B")
                    monthly_savings = row[1] - row[2]
                    table.add_row([month_name, f"${row[1]:.2f}", f"${row[2]:.2f}", f"${monthly_savings:.2f}"])
                print(table)

            return {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'savings': savings,
                'monthly_breakdown': monthly_breakdown
            }
        except Error as e:
            print(f"Error generating yearly summary: {e}")
        finally:
            conn.close()
    return None