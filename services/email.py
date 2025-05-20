from models.base import SessionLocal, User, Campaign,Contact, CampaignEmail
from datetime import date
import os

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
            for ce in pending_emails:
                print(f"To: {ce.to}, Subject: {ce.subject}")
        except Exception as e:
            print(f"Error fetching pending CampaignEmails: {e}")
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
            contacts = session.query(Contact).filter(Contact.user_id == user_id, Contact.tags.like('%{tags}%')).all()
            inserted = 0
            for contact in contacts:
                # Check if already exists to avoid duplicates
                exists = session.query(CampaignEmail).filter_by(
                    campaign_id=campaign_id,
                    contact_id=contact.id,
                    user_id=user_id
                ).first()
                if exists:
                    continue
                campaign_email = CampaignEmail(
                    campaign_id=campaign_id,
                    contact_id=contact.id,
                    user_id=user_id,
                    date_from=date.today(),
                    status=status,
                    to=contact.email,
                    subject=subject,
                    body=body
                )
                session.add(campaign_email)
                inserted += 1
                session.commit()
            print(f"Inserted {inserted} contacts into CampaignEmail for campaign {campaign_id}")
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
        finally:
            session.close()