from models.base import SessionLocal, CampaignLinkedin, Campaign,Contact,CampaignLinkedinSearch
from datetime import date
from selenium import webdriver
from chromedriver_py import binary_path # This will get you the path variable
from selenium.webdriver.chrome.service import Service
# Wait for the page to load and find the input fields
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

import os

class LinkedinService:
    
    def click_connect(self, ce, driver, session):
        buttons = driver.find_elements(By.TAG_NAME, "button")
        connect_button = None
        is_connect_present = True
        for btn in buttons:
            print(f"Found Message button: '{btn.text}'")
            if "Connect" in btn.text:
                connect_button = btn
            if "Message" in btn.text:
                if is_connect_present and connect_button is not None and connect_button:
                    connect_button.click()
                    time.sleep(5)
                    self.connect_modal(ce, driver, session)
                    print("Clicked the Connect button.")
                    break
                else:
                    is_connect_present = False   
            if "More" in btn.text:
                btn.click()
                time.sleep(1)
                print("Clicked the More button.")
                try:
                    # Wait for the dropdown to appear
                    dropdown = driver.find_elements(By.CSS_SELECTOR, ".artdeco-dropdown__content")
                    is_connected = False
                    for d in dropdown:
                        connect_buttons = d.find_elements(By.XPATH, ".//*[@role='button']")
                        for btn in connect_buttons:
                            btn_text = btn.text
                            aria_label = btn.get_attribute("aria-label") or ""
                            print(f"Dropdown button text: '{btn_text}', aria-label: '{aria_label}'")
                            if "Connect" in btn_text or "Connect" in aria_label:
                                if "Connection" in btn_text or "Connection" in aria_label:
                                    break
                                is_connected = True
                                btn.click()
                                print("Clicked the Connect button in dropdown.")
                                time.sleep(2)
                                self.connect_modal(ce, driver, session)
                                print("Clicked the Connect button.")
                                break
                    if is_connected:
                        ce.status = "CONNECTED"
                        session.commit()
                    
                except Exception as e:
                    print(f"Could not find or click Connect in dropdown: {e}")
                    traceback.print_exc()
            if "Pending" in btn.text:
                print("Already connected or pending.")
                ce.status = "CONNECTED"
                session.commit()
                break
            
    def connect_modal(self, ce, driver, session):
        try:
            # Wait for the modal to appear
            modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "artdeco-modal"))
            )
            # Find all buttons inside the modal
            modal_buttons = modal.find_elements(By.TAG_NAME, "button")
            for btn in modal_buttons:
                print(f"Modal button text: '{btn.text}'")
                if "Send without a note" in btn.text:
                    btn.click()
                    time.sleep(5)
                    ce.status = "CONNECTED"
                    session.commit()
                    break
        except Exception as e:
            print(f"Could not find modal or its buttons: {e}")
                
    """
    Logs into LinkedIn using the provided email and password.
    Uses chromedriver from the root project directory.
    """
    def login_linkedin(self, email, password):
        """
        Logs into LinkedIn using the provided email and password.
        Uses chromedriver from /usr/local/bin/chromedriver.
        """
        
        chromedriver_path = '/usr/local/bin/chromedriver'
        svc = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=svc)
        try:
            driver.get("https://www.linkedin.com/login")
            print("Opened LinkedIn login page with Selenium.")
            time.sleep(5)  # Wait for the page to load (use WebDriverWait for production)
            email_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")

            email_input.clear()
            email_input.send_keys(email)
            password_input.clear()
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)  # Wait for the page to load (use WebDriverWait for production)
            # Check for LinkedIn challenge page
            current_url = driver.current_url
            if "https://www.linkedin.com/checkpoint/challenge" in current_url:
                print("LinkedIn challenge detected! Please resolve the challenge manually.")
                input("Press Enter after completing the challenge in the browser...")

            # You can add more Selenium automation here as needed
        except Exception as e:
            print(f"Selenium error: {e}")
        return driver
            
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
    Finds an existing campaign for the user with the given status and action, or creates a new one.
    - Calls add_campaign_contacts to create CampaignLinkedin entries for all matching contacts.
    - Returns the campaign ID.
    """   
    def add_or_retrive_campaign_only(self, user_id, status="PENDING", action="LINKEDIN_CONNECT", date_execution=None):
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

    def update_campaign_linkedin_search(self, id, status=None, page=None):
        session = SessionLocal()
        try:
            campaign_linkedin_search = session.query(CampaignLinkedinSearch).filter_by(id=id).first()
            if not campaign_linkedin_search:
                print(f"No CampaignLinkedinSearch found with id: {id}")
                return False
            if status is not None:
                campaign_linkedin_search.status = status
            if page is not None:
                campaign_linkedin_search.page = page
            session.commit()
            print(f"Updated CampaignLinkedinSearch id {id}: status={status}, page={page}")
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating CampaignLinkedinSearch: {e}")
            return False
        finally:
            session.close()
    """
    Finds an existing campaign linkedin search for the user with the given status  or creates a new one.
    - Returns the campaign linkedin search object.
    """   
    def add_or_retrive_campaign_linkedin(self, user_id,campaign_id, status="PENDING"):
        session = SessionLocal()
        try:
            campaign_linkedin_search = session.query(CampaignLinkedinSearch).filter_by(
                user_id=user_id,
                campaign_id=campaign_id
            ).first()
            if campaign_linkedin_search is None:
                data = self.menu_search()
                campaign_linkedin_search = CampaignLinkedinSearch(
                    user_id=user_id,
                    campaign_id=campaign_id,
                    status=status,
                    query = data['query'],
                    network = data['network'],
                    connection = data['connection'],
                    geo =  data['geo'],
                    geo_value = data['geo_value'],
                    page = 1
                )
                session.add(campaign_linkedin_search)
                session.commit()
                print(f"Created new campaign linkedin search with id: {campaign_linkedin_search.id}")
            else:
                print(f"Found existing campaign linkedin search with id: {campaign_linkedin_search.id}")

            return {
                    "user_id": campaign_linkedin_search.user_id,
                    "campaign_id": campaign_linkedin_search.campaign_id,
                    "status": campaign_linkedin_search.status,
                    "query": campaign_linkedin_search.query,
                    "network": campaign_linkedin_search.network,
                    "connection": campaign_linkedin_search.connection,
                    "geo": campaign_linkedin_search.geo,
                    "geo_value": campaign_linkedin_search.geo_value,
                    "page": campaign_linkedin_search.page,
                    "id": campaign_linkedin_search.id
                }
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
            return None
        finally:
            session.close()  
            

    def update_campaign_linkedin_search(self, id, status=None, page=None):
        session = SessionLocal()
        try:
            campaign_linkedin_search = session.query(CampaignLinkedinSearch).filter_by(id=id).first()
            if not campaign_linkedin_search:
                print(f"No CampaignLinkedinSearch found with id: {id}")
                return False
            if status is not None:
                campaign_linkedin_search.status = status
            if page is not None:
                campaign_linkedin_search.page = page
            session.commit()
            print(f"Updated CampaignLinkedinSearch id {id}: status={status}, page={page}")
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating CampaignLinkedinSearch: {e}")
            return False
        finally:
            session.close()
    """
    Finds an existing campaign linkedin search for the user with the given status  or creates a new one.
    - Returns the campaign linkedin search object.
    """   
    def add_or_retrive_campaign_linkedin(self, user_id,campaign_id, status="PENDING"):
        session = SessionLocal()
        try:
            campaign_linkedin_search = session.query(CampaignLinkedinSearch).filter_by(
                user_id=user_id,
                campaign_id=campaign_id
            ).first()
            if campaign_linkedin_search is None:
                data = self.menu_search()
                campaign_linkedin_search = CampaignLinkedinSearch(
                    user_id=user_id,
                    campaign_id=campaign_id,
                    status=status,
                    query = data['query'],
                    network = data['network'],
                    connection = data['connection'],
                    geo =  data['geo'],
                    geo_value = data['geo_value'],
                    page = 1
                )
                session.add(campaign_linkedin_search)
                session.commit()
                print(f"Created new campaign linkedin search with id: {campaign_linkedin_search.id}")
            else:
                print(f"Found existing campaign linkedin search with id: {campaign_linkedin_search.id}")

            return {
                    "user_id": campaign_linkedin_search.user_id,
                    "campaign_id": campaign_linkedin_search.campaign_id,
                    "status": campaign_linkedin_search.status,
                    "query": campaign_linkedin_search.query,
                    "network": campaign_linkedin_search.network,
                    "connection": campaign_linkedin_search.connection,
                    "geo": campaign_linkedin_search.geo,
                    "geo_value": campaign_linkedin_search.geo_value,
                    "page": campaign_linkedin_search.page,
                    "id": campaign_linkedin_search.id
                }
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
            return None
        finally:
            session.close()  