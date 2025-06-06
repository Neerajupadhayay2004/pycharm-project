import sys
import getpass
from datetime import datetime
from auth import register_user, login_user, change_password
from transactions import add_transaction, update_transaction, delete_transaction, list_categories, list_transactions
from reports import get_monthly_summary, get_yearly_summary
from budget import set_budget, get_budget_status


def main_menu():
    print("\nPersonal Finance Management System")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice


def user_menu(user_id):
    print("\nUser Menu")
    print("1. Add Transaction")
    print("2. Update Transaction")
    print("3. Delete Transaction")
    print("4. List Transactions")
    print("5. Monthly Summary")
    print("6. Yearly Summary")
    print("7. Set Budget")
    print("8. View Budget Status")
    print("9. Change Password")
    print("10. Logout")
    choice = input("Enter your choice: ")
    return choice


def get_transaction_details():
    list_categories()
    category_id = input("Enter category ID: ")
    amount = float(input("Enter amount: "))
    description = input("Enter description (optional): ")
    return category_id, amount, description if description else None


def main():
    current_user = None

    while True:
        if current_user is None:
            choice = main_menu()

            if choice == '1':
                username = input("Enter username: ")
                password = getpass.getpass("Enter password: ")
                register_user(username, password)

            elif choice == '2':
                username = input("Enter username: ")
                password = getpass.getpass("Enter password: ")
                current_user = login_user(username, password)

            elif choice == '3':
                print("Goodbye!")
                sys.exit()

            else:
                print("Invalid choice. Please try again.")

        else:
            choice = user_menu(current_user)

            if choice == '1':
                print("\nAdd New Transaction")
                category_id, amount, description = get_transaction_details()
                add_transaction(current_user, category_id, amount, description)

            elif choice == '2':
                print("\nUpdate Transaction")
                list_transactions(current_user)
                transaction_id = input("Enter transaction ID to update: ")
                print("Leave fields blank to keep current values")

                category_id = input(f"Enter new category ID (or leave blank): ")
                amount_input = input("Enter new amount (or leave blank): ")
                description = input("Enter new description (or leave blank): ")

                amount = float(amount_input) if amount_input else None
                category_id = int(category_id) if category_id else None
                description = description if description else None

                update_transaction(transaction_id, current_user, category_id, amount, description)

            elif choice == '3':
                print("\nDelete Transaction")
                list_transactions(current_user)
                transaction_id = input("Enter transaction ID to delete: ")
                delete_transaction(transaction_id, current_user)

            elif choice == '4':
                print("\nRecent Transactions")
                list_transactions(current_user)

            elif choice == '5':
                print("\nMonthly Summary")
                month = int(input("Enter month (1-12): "))
                year = int(input("Enter year: "))
                get_monthly_summary(current_user, month, year)

            elif choice == '6':
                print("\nYearly Summary")
                year = int(input("Enter year: "))
                get_yearly_summary(current_user, year)

            elif choice == '7':
                print("\nSet Budget")
                list_categories()
                category_id = input("Enter category ID: ")
                amount = float(input("Enter budget amount: "))
                month = int(input("Enter month (1-12): "))
                year = int(input("Enter year: "))
                set_budget(current_user, category_id, amount, month, year)

            elif choice == '8':
                print("\nBudget Status")
                month = int(input("Enter month (1-12): "))
                year = int(input("Enter year: "))
                get_budget_status(current_user, month, year)

            elif choice == '9':
                print("\nChange Password")
                old_password = getpass.getpass("Enter current password: ")
                new_password = getpass.getpass("Enter new password: ")
                confirm_password = getpass.getpass("Confirm new password: ")

                if new_password == confirm_password:
                    change_password(current_user, old_password, new_password)
                else:
                    print("Passwords don't match!")

            elif choice == '10':
                print("Logging out...")
                current_user = None

            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Initialize database if not exists
    from database import initialize_database

    initialize_database()

    main()