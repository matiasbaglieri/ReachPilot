import os
from services.linkedin import LinkedinService
from services.email import EmailService
from services.user import UserService
from services.contact import ContactService
from services.linkedin_connect import LinkedinConnect
from services.linkedin_search import LinkedinSearch
def submenu(user):
    while True:
        print("\n--- Submenu ---")
        print("1. Connect Contacts from db in Linkedin")
        print("2. Search in linkedin and create a bulk list")
        print("0. Back to Main Menu")
        choice = input("Select an option: ")
        if choice == "1":
            linkedin_connect_service = LinkedinConnect()
            linkedin_connect_service.execute(user)
        elif choice == "2":
            linkedin_search_service = LinkedinSearch()
            linkedin_search_service.execute(user)
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")

def find_contacts(user):
    dumps_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dumps'))
    csv_files = [f for f in os.listdir(dumps_dir) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in dumps directory.")
        return
    print("\nAvailable CSV files for contacts:")
    for idx, fname in enumerate(csv_files):
        print(f"{idx + 1}. {fname}")
    selected = input("Select a file number to import contacts: ")
    try:
        selected_idx = int(selected) - 1
        if selected_idx < 0 or selected_idx >= len(csv_files):
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return
    filename = csv_files[selected_idx]
    print(f"Selected file: {filename}, id user {user['id']}")
    contact_service = ContactService()
    contact_service.add_contacts(user['id'], filename)

def main_menu():
    email = input("email: ")
    passwd = input("password: ")
    mailgun_api = input("mailgun api key: ")
    user_service = UserService()
    user = user_service.execute(email, passwd, mailgun_api)
    if not user:
        print("User creation or retrieval failed. Please check your input or database connection.")
        return
    while True:
        print("\n=== Main Menu ===")
        print("1. Go to Linkedin")
        print("2. Execute Email Service")
        print("3. Find Contacts (Import from CSV)")
        print("0. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            submenu(user)
        elif choice == "2":
            email_service = EmailService()
            email_service.execute(user)
        elif choice == "3":
            find_contacts(user)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()