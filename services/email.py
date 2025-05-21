from models.base import SessionLocal, User, Campaign,Contact, CampaignEmail
from datetime import date
import os
import re,requests

class EmailService:
    def execute(self, user):
        print(f"Executing Email service with:")
        print(f"Email: {user['email']}")
        print(f"Mailgun API: {user['mailgun']}")
        campaign_id = self.add_or_retrive_campaign(user['id'], status="PENDING", action="EMAIL", date_execution=None)

        # Find all CampaignEmail where campaign_id is campaign_id and status is PENDING
        session = SessionLocal()
        try:
            pending_emails = session.query(CampaignEmail).filter_by(
                campaign_id=campaign_id,
                status="PENDING"
            ).all()
            print(f"Found {len(pending_emails)} CampaignEmail(s) with status PENDING for campaign {campaign_id}")
            if not pending_emails:
                # Update Campaign status to COMPLETED
                self.update_campaign(campaign_id, status="COMPLETED")
                return
            mailgun_from = input("Add a from to send the email: ")
            
            for ce in pending_emails:
                print(f"To: {ce.to}, Subject: {ce.subject}")
                self.send_email(
                    mailgun_from=mailgun_from,
                    mailgun_api=user['mailgun'],
                    to_email=ce.to,
                    subject=ce.subject,
                    body=ce.body,
                    campaign_email_id=ce.id
                )
            pending_emails = session.query(CampaignEmail).filter_by(
                campaign_id=campaign_id,
                status="PENDING"
            ).all()
            # After printing, check if there are any PENDING CampaignEmails left
            if not pending_emails:
                # Update Campaign status to COMPLETED
                self.update_campaign(campaign_id, status="COMPLETED")
               
        except Exception as e:
            print(f"Error fetching pending CampaignEmails: {e}")
        finally:
            session.close()
    def update_campaign(self, campaign_id, status):
        session = SessionLocal()
        try:
            campaign = session.query(Campaign).filter_by(id=campaign_id).first()
            if campaign:
                campaign.status = status
                session.commit()
                print(f"Campaign {campaign_id} status updated to {status}.")
        except Exception as e:
            session.rollback()
            print(f"Error updating campaign status: {e}")
        finally:
            session.close()
               
    def send_email(self, mailgun_from,mailgun_api, to_email, subject, body, campaign_email_id):
        """
        Send an email using Mailgun and update CampaignEmail status to COMPLETED if successful.
        """
        session = SessionLocal()
        try:
            match = re.search(r'@([A-Za-z0-9.-]+)$', mailgun_from)
            if match:
                MAILGUN_DOMAIN = match.group(1)
            else:
                print("Invalid mailgun_from email address.")
                return

            MAILGUN_API_KEY = mailgun_api

            response = requests.post(
                f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
                auth=("api", MAILGUN_API_KEY),
                data={
                    "from": f"{mailgun_from}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": body
                }
            )

            if response.status_code == 200:
                # Update CampaignEmail status to COMPLETED
                status = "COMPLETED"
                print(f"Email sent to {to_email} and status updated to COMPLETED.")
            else:
                status = "FAILED"
                print(f"Failed to send email to {to_email}: {response.text}")
            campaign_email = session.query(CampaignEmail).filter_by(id=campaign_email_id).first()
            if campaign_email:
                campaign_email.status = status
                session.commit()
        
        except Exception as e:
            session.rollback()
            print(f"Error sending email: {e}")
        finally:
            session.close()
       
    def add_or_retrive_campaign(self, user_id, status="PENDING", action="EMAIL", date_execution=None):
        session = SessionLocal()
        try:
            if date_execution is None:
                date_execution = date.today()
            campaign = session.query(Campaign).filter_by(
                user_id=user_id,
                status=status,
                action=action
            ).first()
            if campaign is None:
                campaign = Campaign(
                    user_id=user_id,
                    status=status,
                    action=action,
                    date_execution=date_execution
                )
                session.add(campaign)
                session.commit()
                print(f"Created new campaign with id: {campaign.id}")
            else:
                print(f"Found existing campaign with id: {campaign.id}")
                return campaign.id
            # List HTML files in dumps folder
            dumps_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dumps'))
            html_files = [f for f in os.listdir(dumps_dir) if f.endswith('.html')]
            if not html_files:
                print("No HTML files found in dumps folder.")
                return campaign.id

            print("\nAvailable HTML files for email body:")
            for idx, fname in enumerate(html_files):
                print(f"{idx + 1}. {fname}")
            selected = input("Select a file number for the email body: ")
            try:
                selected_idx = int(selected) - 1
                if selected_idx < 0 or selected_idx >= len(html_files):
                    print("Invalid selection.")
                    return campaign.id
            except ValueError:
                print("Invalid input.")
                return campaign.id

            html_file_path = os.path.join(dumps_dir, html_files[selected_idx])
            with open(html_file_path, 'r', encoding='utf-8') as f:
                body = f.read()

            subject = input("Enter the subject for the campaign email: ")
            tags = input("Enter the tags for segment contacts for the campaign: ")

            # Call add_campaign_contacts
            self.add_campaign_contacts(user_id, campaign.id, subject, body,"PENDING", tags)

            return campaign.id
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
            return None
        finally:
            session.close()

    def add_campaign_contacts(self, user_id, campaign_id, subject, body, status="PENDING",tags="INVESTORS"):
        """
        For a given user_id and campaign_id, insert all user's contacts into CampaignEmail.
        """
        session = SessionLocal()
        try:
            print(f"Running query: SELECT * FROM contacts WHERE user_id={user_id} AND tags LIKE '%{tags}%'")
            contacts = session.query(Contact).filter(Contact.user_id == user_id, Contact.tags.like(f'%{tags}%')).all()
            print(f"Found {len(contacts)} contacts with tags like '{tags}' for user_id {user_id}")
            inserted = 0
            for contact in contacts:
                # Check if already exists to avoid duplicates
                exists = session.query(CampaignEmail).filter_by(
                    campaign_id=campaign_id,
                    contact_id=contact.id
                ).first()
                if exists:
                    continue
                personalized_subject = subject.replace("{first_name}", contact.first_name or "") \
                                  .replace("{last_name}", contact.last_name or "") \
                                  .replace("{title}", contact.title or "") \
                                  .replace("{website}", contact.website or "")
                personalized_body = body.replace("{first_name}", contact.first_name or "") \
                            .replace("{last_name}", contact.last_name or "") \
                            .replace("{title}", contact.title or "") \
                            .replace("{website}", contact.website or "")

                campaign_email = CampaignEmail(
                    campaign_id=campaign_id,
                    contact_id=contact.id,
                    user_id=user_id,
                    date_from=date.today(),
                    status=status,
                    to=contact.email,
                    subject=personalized_subject,
                    body=personalized_body
                )
                print(f"Inserted: {inserted} Prepared CampaignEmail: campaign_id={campaign_email.campaign_id}, contact_id={campaign_email.contact_id}, user_id={campaign_email.user_id}, to={campaign_email.to}, subject={campaign_email.subject}")
                session.add(campaign_email)
                inserted += 1
                session.commit()
            print(f"Inserted {inserted} contacts into CampaignEmail for campaign {campaign_id}")
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
        finally:
            session.close()