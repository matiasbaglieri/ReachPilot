from .linkedin import LinkedinService
from models.base import SessionLocal, CampaignLinkedin, Campaign, Contact
from datetime import date
from selenium import webdriver
from chromedriver_py import binary_path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
import os

"""
LinkedinConnect extends LinkedinService with additional or specialized functionality
for handling LinkedIn connection workflows.
"""
class LinkedinConnect(LinkedinService):

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
            driver = self.login_linkedin(user['email'], user['password'])
            inserted = 0
            for ce in pending_linkedin:
                print(f"Found {len(pending_linkedin)} Inserted:{inserted} url: {ce.url}")
                driver.get(ce.url)
                time.sleep(5)
                self.click_connect(ce,driver,session)
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
            