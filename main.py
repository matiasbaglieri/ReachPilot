#!/usr/bin/env python3

from services.linkedin import LinkedinService
from services.email import EmailService
from services.user import UserService

def submenu():
    while True:
        print("\n--- Submenu ---")
        print("1. Submenu Option 1")
        print("2. Submenu Option 2")
        print("0. Back to Main Menu")
        choice = input("Select an option: ")
        if choice == "1":
            print("You selected Submenu Option 1")
        elif choice == "2":
            print("You selected Submenu Option 2")
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")

def main_menu():
    email = input("email: ")
    passwd = input("password: ")
    mailgun_api = input("mailgun api key: ")
    user_service = UserService()
    user = user_service.execute(email,passwd,mailgun_api)
    while True:
        print("\n=== Main Menu ===")
        print("1. Go to Submenu")
        print("2. Execute Linkedin Service")
        print("3. Execute Email Service")
        print("0. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            submenu()
        elif choice == "2":
            linkedin_service = LinkedinService()
            linkedin_service.execute(user)
        elif choice == "3":
            email_service = EmailService()
            email_service.execute(user)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()