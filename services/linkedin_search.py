from .linkedin import LinkedinService
from models.base import SessionLocal, CampaignLinkedin, Campaign, Contact,CampaignLinkedinSearch
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
        print(f"Executing Linkedin service with:")
        print(f"Email: {user['email']}")
        print(f"Password: {user['password']}")
        campaign_id = self.add_or_retrive_campaign_only(user['id'], status="PENDING", action="LINKEDIN_SEARCH", date_execution=None)

        try:
            driver = self.login_linkedin(user['email'], user['password'])
            # inserted = 0
            # for ce in pending_linkedin:
            #     print(f"Found {len(pending_linkedin)} Inserted:{inserted} url: {ce.url}")
            #     inserted += 1
            
            data = self.add_or_retrive_campaign_linkedin(user['id'], campaign_id, status="PENDING", page=1)
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
        for d in dropdown:
            more_results = True
            # print(d.get_attribute("outerHTML")) 
            try:
                a_tag = d.find_element(By.TAG_NAME, "a")
                profile_url = a_tag.get_attribute("href")
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
            except Exception as e:
                print("No <a> tag found in this element:", e)
        return more_results
      
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