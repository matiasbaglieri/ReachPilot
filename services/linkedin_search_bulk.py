from .linkedin import LinkedinService
from models.base import SessionLocal, CampaignLinkedin, Campaign, Contact,CampaignLinkedinSearch,CampaignLinkedinSearchItem
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
from bs4 import BeautifulSoup

"""
LinkedinSearchBulk extends LinkedinService with additional or specialized functionality
for handling LinkedIn search workflows.
"""
class LinkedinSearchBulk(LinkedinService):

    def execute(self, user):
        print(f"Executing LinkedinSearchBulk service with:")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        campaign_id = self.add_or_retrive_campaign_only(user['id'], status="IN_PROGRESS", action="LINKEDIN_SEARCH", date_execution=None)

        try:
            driver = self.login_linkedin(user['email'], user['password'])
            # inserted = 0
            # for ce in pending_linkedin:
            #     print(f"Found {len(pending_linkedin)} Inserted:{inserted} url: {ce.url}")
            #     inserted += 1
            
            data = self.add_or_retrive_campaign_linkedin(user['id'], campaign_id, "IN_PROGRESS")
            if data['status'] == "IN_PROGRESS":
                session = SessionLocal()
                try:
                    message = ""
                    if int(data['connection']) == 1:
                        message = input("write message to send: ")
                    items = session.query(CampaignLinkedinSearchItem).filter_by(
                        campaign_linkedin_search_id=data['id'],
                        status="PENDING"
                    ).all()
                    for item in items:
                        self.process_bulk(data['connection'], item, session, message, driver, user['id'])
                finally:
                    session.close()
            input("Enter to finish campaign ")
            self.update_campaign_linkedin_search(data['id'], "COMPLETED")   
            self.update_campaign(campaign_id, status="COMPLETED")
               
        except Exception as e:
            print(f"Error fetching pending CampaignLinkedin: {e}")
    
    def process_bulk(self, connection, item, session, message, driver, user_id):
        # Example: set status to "PROCESSED" and set email (replace with real logic)
        # If you have logic to extract or assign an email, do it here
        if int(connection) == 1:
            self.process_first_connection(item, session, message, driver,user_id)
        else:
            self.process_second_connection(item, session, driver)
        print(f"Processed item {item.id}: status={item.status}, email={item.email}")
    
    def process_first_connection(self, item, session, message,driver,user_id):
        message = message.replace("first_name", item.first_name.lower())
        driver.get(item.linkedin+"/overlay/contact-info/")
        time.sleep(5)
        contact_sections = driver.find_elements(By.CLASS_NAME, "pv-contact-info__contact-type")
        email = None
        for section in contact_sections:
            try:
                a_tag = section.find_element(By.TAG_NAME, "a")
                href = a_tag.get_attribute("href")
                if href and href.startswith("mailto:"):
                    email = href.replace("mailto:", "").strip()
                    break
            except Exception:
                continue
        #extract email 
        print("Email found:", email)  
        driver.get(item.linkedin)
        time.sleep(5)
        self.click_message(driver, message, item.linkedin)  
        item.status = "COMPLETED"      
        if email:
            item.email = email
            contact = session.query(Contact).filter_by(email=email, user_id=user_id).first()
            if not contact:
                contact = Contact(
                    first_name=item.first_name,
                    last_name=item.last_name,
                    email=email,
                    linkedin=item.linkedin,
                    user_id=user_id,
                    status="ACTIVE"
                )
                session.add(contact)
                print(f"Created new contact: {email}")
            else:
                print(f"Contact already exists: {email}")
   
        session.commit()
        print(f"Processed item {item.id}: status={item.status}, email={item.email}")
    
    def process_second_connection(self, item, session, driver):
        driver.get(item.linkedin)
        time.sleep(5)
        input("process_second_connection ")
        # item.status = "COMPLETED"
        # session.commit()
        print(f"Processed item {item.id}: status={item.status}, email={item.email}")
        
    def click_message(self,  driver, message, url):
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if "Message" in btn.text:
                btn.click()
                time.sleep(5)
                if url in driver.current_url:
                    self.click_message_in_browser(driver, message)
                    print("Current URL matches the profile URL.")
                else:
                    print("Current URL does NOT match the profile URL.")
                    input("click_message ")
                
                break
            
    def click_message_in_browser(self, driver, message):  
        try:
            message_box = driver.switch_to.active_element
        
            message_box.click()
            message_box.clear()
            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
            message_box.send_keys(Keys.RETURN)

            send_button = driver.find_element(By.CLASS_NAME, "msg-form__send-button")
            send_button.click()
            driver.execute_script("arguments[0].click();", send_button)
            
            time.sleep(3)
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()


            time.sleep(1)
            # Find and click the send button
        except Exception as e:
            print("Could not send message:", e)                