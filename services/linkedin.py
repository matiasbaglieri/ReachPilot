from models.base import SessionLocal, User,CampaignLinkedin, Campaign,Contact, CampaignEmail
from datetime import date
import os
import re,requests

class LinkedinService:
    def execute(self, user):
        print(f"Executing Linkedin service with:")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        campaign_id = self.add_or_retrive_campaign(user['id'], status="PENDING", action="LINKEDIN_CONNECT", date_execution=None)

        # Find all CampaignEmail where campaign_id is campaign_id and status is PENDING
        session = SessionLocal()
        try:
            pending_linkedin = session.query(CampaignLinkedin).filter_by(
                campaign_id=campaign_id,
                status="PENDING",
                action="LINKEDIN_CONNECT"
            ).all()
            print(f"Found {len(pending_linkedin)} CampaignLinkedin(s) with status PENDING for campaign {campaign_id} action: LINKEDIN_CONNECT")
            if not pending_linkedin:
                # Update Campaign status to COMPLETED
                self.update_campaign(campaign_id, status="COMPLETED")
                return
            inserted = 0
            for ce in pending_linkedin:
                print(f"Found {len(pending_linkedin)} Inserted:{inserted} To: {ce.to}, Subject: {ce.subject}")
                mailgun_from = input("Add a from to send the email: ")
                
                inserted += 1
            pending_linkedin = session.query(CampaignLinkedin).filter_by(
                campaign_id=campaign_id,
                status="PENDING",
                action="LINKEDIN_CONNECT"
            ).all()
            # After printing, check if there are any PENDING CampaignLinkedin left
            if not pending_linkedin:
                # Update Campaign status to COMPLETED
                self.update_campaign(campaign_id, status="COMPLETED")
               
        except Exception as e:
            print(f"Error fetching pending CampaignLinkedin: {e}")
        finally:
            session.close()
    
    """
    Updates the status of a campaign given its ID.
    Commits the change to the database and prints the result.
    """
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

    """
    Finds an existing campaign for the user with the given status and action, or creates a new one.
    - Calls add_campaign_contacts to create CampaignLinkedin entries for all matching contacts.
    - Returns the campaign ID.
    """   
    def add_or_retrive_campaign(self, user_id, status="PENDING", action="LINKEDIN_CONNECT", date_execution=None):
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
            # Call add_campaign_contacts
            tags = input("Enter the tags for segment contacts for the campaign: ")

            self.add_campaign_linkedin(user_id, campaign.id, "PENDING",action, tags)

            return campaign.id
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
            return None
        finally:
            session.close()
    """
    For a given user_id and campaign_id, inserts all user's contacts (filtered by tags) into CampaignLinkedin.
    - Avoids duplicates by checking for existing CampaignLinkedin entries.
    - Prints the number of contacts found and inserted.
    """
    def add_campaign_linkedin(self, user_id, campaign_id, status="PENDING",action="LINKEDIN_CONNECT",tags="INVESTORS"):
        """
        For a given user_id and campaign_id, insert all user's contacts into CampaignLinkedin.
        """
        session = SessionLocal()
        try:
            print(f"Running query: SELECT * FROM contacts WHERE user_id={user_id} AND tags LIKE '%{tags}%,%LINKEDIN%'")
            contacts = session.query(Contact).filter(Contact.user_id == user_id, Contact.tags.like(f'%{tags}%,%LINKEDIN%')).all()
            print(f"Found {len(contacts)} contacts with tags like '{tags}' for user_id {user_id}")
            inserted = 0
            for contact in contacts:
                # Check if already exists to avoid duplicates
                exists = session.query(CampaignLinkedin).filter_by(
                    campaign_id=campaign_id,
                    contact_id=contact.id
                ).first()
                if exists:
                    continue
              
                campaign_email = CampaignLinkedin(
                    campaign_id=campaign_id,
                    contact_id=contact.id,
                    user_id=user_id,
                    date_from=date.today(),
                    status=status,
                    action=action,
                    url=contact.linkedin
                )
                print(f"Found:{len(contacts)} Inserted: {inserted} Prepared CampaignLinkedin: campaign_id={campaign_email.campaign_id}, contact_id={campaign_email.contact_id}, user_id={campaign_email.user_id}, action={action}")
                session.add(campaign_email)
                inserted += 1
                session.commit()
            print(f"Inserted {inserted} contacts into CampaignLinkedin for campaign {campaign_id}")
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
        finally:
            session.close()