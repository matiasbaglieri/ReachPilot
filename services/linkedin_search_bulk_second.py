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
LinkedinSearchBulkSecond extends LinkedinService with additional or specialized functionality
for handling LinkedIn search workflows.
"""
class LinkedinSearchBulkSecond(LinkedinService):

    def execute(self, user):
        print(f"Executing LinkedinSearchBulk service with:")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        campaign_id = self.add_or_retrive_campaign_only(user['id'], status="IN_PROGRESS", action="LINKEDIN_SEARCH_2", date_execution=None)

        try:
            driver = self.login_linkedin(user['email'], user['password'])
            
            data = self.add_or_retrive_campaign_linkedin(user['id'], campaign_id, "IN_PROGRESS")
            if data['status'] == "IN_PROGRESS":
                session = SessionLocal()
                try:
                    items = session.query(CampaignLinkedinSearchItem).filter_by(
                        campaign_linkedin_search_id=data['id'],
                        status="PENDING"
                    ).all()
                    for item in items:
                        self.process_second_connection(item, session, driver)
                finally:
                    session.close()
            input("Enter to finish campaign ")
            self.update_campaign_linkedin_search(data['id'], "COMPLETED")   
            self.update_campaign(campaign_id, status="COMPLETED")
               
        except Exception as e:
            print(f"Error fetching pending CampaignLinkedin: {e}")
    
    def process_second_connection(self, item, session, driver):
        driver.get(item.linkedin)
        time.sleep(5)
        self.process_second_connection_click_connect(item, driver, session)
        print(f"Processed item {item.id}: status={item.status}")
    
    def process_second_connection_click_connect(self, ce, driver, session):
        try:
            current_url = driver.current_url
            if ce.linkedin not in current_url:
                print(f"URL mismatch. Current: {current_url}, Expected to contain: {ce.linkedin}")
                ce.status = "COMPLETED"
                session.commit()
                return

            buttons = driver.find_elements(By.TAG_NAME, "button")
            connect_button = None
            is_connect_present = True
            is_send_message_present = False
            for btn in buttons:
                print(f"Found Message button: '{btn.text}'")
                if "Connect" in btn.text or "Conectar" in btn.text:
                    connect_button = btn
                if "Message" in btn.text or "Enviar mensaje" in btn.text:
                    is_send_message_present = True
                    if is_connect_present and connect_button is not None and connect_button:
                        connect_button.click()
                        time.sleep(5)
                        self.connect_modal(ce, driver, session)
                        print("Clicked the Connect button.")
                        break
                    else:
                        is_connect_present = False  
                if is_send_message_present and connect_button is not None and connect_button:
                    connect_button.click()
                    time.sleep(5)
                    self.connect_modal(ce, driver, session)
                    print("Clicked the Connect button.")
                    break
                else:
                    is_send_message_present = False
                    
                if "More" in btn.text or "Más" in btn.text:
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
                                    self.process_second_connection_connect_modal(ce, driver, session)
                                    print("Clicked the Connect button.")
                                    break
                        if is_connected:
                            ce.status = "COMPLETED"
                            session.commit()
                        
                    except Exception as e:
                        print(f"Could not find or click Connect in dropdown: {e}")
                        traceback.print_exc()
                if "Pending" in btn.text:
                    print("Already connected or pending.")
                    ce.status = "COMPLETED"
                    session.commit()
                    break
        except Exception as e:
            print(f"Error in process_second_connection_click_connect: {e}")
            traceback.print_exc()
            ce.status = "COMPLETED"
            session.commit()
    
    def process_second_connection_connect_modal(self, ce, driver, session):
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
                    ce.status = "COMPLETED"
                    session.commit()
                    break
        except Exception as e:
            print(f"Could not find modal or its buttons: {e}")    
        
        