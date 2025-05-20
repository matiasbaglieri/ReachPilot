from models.base import SessionLocal, Contact
from datetime import date
import os
import csv
import traceback


class ContactService:
    def add_contacts(self, user_id, csv_filename):
        """
        Imports contacts from a CSV file in the dumps folder and inserts them into the database.
        """
        session = SessionLocal()
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(parent_dir, 'dumps', csv_filename)
        print(f"CSV path: {csv_path}")
        if not os.path.exists(csv_path):
            print(f"File {csv_path} does not exist.")
            return
        inserted = 0
        try:
           with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                tag = input("Add a tag for the contacts: ")
    
                for row in reader:
                    print(f"Processing row: {row}")
                    email = row[0]
                    if not email or not email.strip():
                        continue  # Skip if email is empty
                   
                    linkedin_value = row[8]
                    if linkedin_value and linkedin_value.strip():
                        tags = tag + ",EMAIL,LINKEDIN"
                    else:
                        tags = tag +",EMAIL"
                    if (len(row[0].split(',')) >1):
                        email = row[0].split(',')[0]
                    if (len(row[0].split(' ::: ')) >1):
                        email = row[0].split(' ::: ')[0]
                    existing = session.query(Contact).filter_by(email=email, user_id=user_id).first()
                    if existing:
                        continue
                    if (len(row[1].split(' ')) >1):
                        first_name = row[1].split(' ')[0]
                        last_name = row[1].split(' ')[1]
                    else:
                        first_name = row[1].split(' ')[0]
                        last_name = ""
                    contact = Contact(
                        email=email,
                        first_name=first_name,
                        last_name=last_name + " " +row[2],
                        company_linkedin=row[3],
                        title=row[4],
                        city=row[5],
                        country=row[6],
                        website=row[7],
                        linkedin=linkedin_value,
                        user_id=user_id,
                        tags=tags,
                        status="ACTIVE"
                    )
                    session.add(contact)
                    inserted += 1
                    session.commit()
                print(f"Inserted {inserted} contacts from {csv_filename}")
        except Exception as e:
            session.rollback()
            print(f"Error importing contacts: {e}")
            traceback.print_exc()
        finally:
            session.close()