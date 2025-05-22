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
LinkedinSearch extends LinkedinService with additional or specialized functionality
for handling LinkedIn search workflows.
"""
class LinkedinSearch(LinkedinService):

    def execute(self, user):
        print(f"Executing LinkedinSearch service with:")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        campaign_id = self.add_or_retrive_campaign_only(user['id'], status="PENDING", action="LINKEDIN_SEARCH", date_execution=None)

        try:
            driver = self.login_linkedin(user['email'], user['password'])
            # inserted = 0
            # for ce in pending_linkedin:
            #     print(f"Found {len(pending_linkedin)} Inserted:{inserted} url: {ce.url}")
            #     inserted += 1
            
            data = self.add_or_retrive_campaign_linkedin(user['id'], campaign_id, "PENDING")
            if data['status'] == "PENDING":
                for page in range(data['page'], 100):
                    self.update_campaign_linkedin_search(data['id'], "PENDING", page)   
                    driver.get(f"https://www.linkedin.com/search/results/people/?geoUrn={data['geo']}&keywords={data['query']}&network={data['network']}&page={page}&origin=FACETED_SEARCH&sid=!b%40")
                    time.sleep(5)
                    more_results = self.list_items(driver,user['id'], campaign_id, data['id'])
                    if not more_results:
                        break
           
            input("Enter to finish campaign ")
            self.update_campaign_linkedin_search(data['id'], "IN_PROGRESS")   
            self.update_campaign(campaign_id, status="IN_PROGRESS")
               
        except Exception as e:
            print(f"Error fetching pending CampaignLinkedin: {e}")
    
    def list_items(self, driver, user_id, campaign_id, campaign_linkedin_search_id):
        dropdown = driver.find_elements(By.CSS_SELECTOR, ".linked-area")
        more_results = False    
        session = SessionLocal()
        for d in dropdown:
            more_results = True
            # print(d.get_attribute("outerHTML")) 
            try:
                a_tag = d.find_element(By.TAG_NAME, "a")
                profile_url = a_tag.get_attribute("href")
                profile_url = profile_url.split("?")[0]
                span_tags = d.find_elements(By.TAG_NAME, "span")
                for span in span_tags:
                    name = span.text.strip()
                    if name:  # Only print non-empty names
                        name = name.split('\n')[0]
                        break
                first_name, last_name = "", ""
                name_parts = name.split()
                if len(name_parts) > 1:
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:])
                elif len(name_parts) == 1:
                    first_name = name_parts[0]
                print("First Name:", first_name)
                print("Last Name:", last_name)
                print("Profile URL:", profile_url)
                item = CampaignLinkedinSearchItem(
                    campaign_id=campaign_id,
                    user_id=user_id,
                    campaign_linkedin_search_id=campaign_linkedin_search_id,
                    first_name=first_name,
                    last_name=last_name,
                    linkedin=profile_url,
                    email=None,  
                    status="PENDING"
                )
                session.add(item)
                session.commit()
            except Exception as e:
                print("No <a> tag found in this element:", e)
        session.close()
        return more_results
      
        
    def menu_search(self):
        query = input("Enter the query for the search: ")
        print(f"1. First Grade")
        print(f"2. Second Grade & Third Grade")
        network = input("Enter a value: ")
        if network == "1":
            network_value = '%5B"F"%5D'
        else:
            network_value = '%5B"S"%2C"O"%5D'
        print(f"1. Location: USA")
        print(f"2. Location: UNITED KINGDOM")
        geo_location = input("Enter a value: ")
        if geo_location == "1":
            geo_query = '%5B"103644278"%5D'
            geo_value = 'UNITED STATES'
        else:
            geo_query = '%5B"101165590"%5D'
            geo_value = 'UNITED KINGDOM'
        return {
            'query': query, 
            'network': network_value, 
            'connection': network,
            'geo': geo_query,
            'geo_value': geo_value
            }