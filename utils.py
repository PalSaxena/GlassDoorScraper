from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


from config import glassdoor_login_url, path_to_chrome_driver, username, password, search_company_url

# CREATING CHROME DRIVER
class Create_driver():

    def __init__(self, glassdoor_login_url, path_to_chrome_driver):
        self.url = glassdoor_login_url
        self.chrome_driver_path = path_to_chrome_driver

    def get_driver(self):
        # CREATE URL STRING
        login_url = self.url

        # CREATE CHROME OPTIONS
        path_to_chromedriver = self.chrome_driver_path

        # CREATE BROWSER INSTANCE
        print("CREATING BROWSER INSTANCE.........")
        chrome_driver = webdriver.Chrome(path_to_chromedriver)
        chrome_driver.wait = WebDriverWait(chrome_driver, 10)
        chrome_driver.get(login_url)
        
        return chrome_driver


# SEARCHING FOR LOGIN FIELD
def login_into_glassdoor(chrome_driver, username, password):
    print("\nLogin Using Gmail")
    try:
        print("\nAttempting to login into GlassDoor...")
        user_field = chrome_driver.find_element(By.ID,"inlineUserEmail")
        time.sleep(1)
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB)
        user_field.send_keys(Keys.ENTER)
        time.sleep(1)
        pw_field = chrome_driver.find_element(By.ID,"inlineUserPassword")
        pw_field.send_keys(password)
        pw_field.send_keys(Keys.TAB)
        pw_field.send_keys(Keys.TAB)
        pw_field.send_keys(Keys.ENTER)
                       
        print("Login successfully") 
        
    except TimeoutException:
        print("TimeoutException! Email/password field or login button not found on glassdoor.com")

# GET REVIEW PAGE
def get_review_page(chrome_driver, company_name):
    company = chrome_driver.get(search_company_url+company_name)
    print("searching for ",company_name," company")
    time.sleep(2)
    try:
        print("Company found !!")
        
        # CLICK THE COMPANY WHICH APPEARS FIRST
        continue_company_search = chrome_driver.find_element(By.CSS_SELECTOR,"a.company-tile")
        continue_company_search.click()

        # SERCHING FOR REVIEW PAGE OF THE COMPANY
        print("searching for review page") 
        time.sleep(2)
        company_review = chrome_driver.find_element(By.CSS_SELECTOR, "a.eiCell.cell.reviews")
        company_review.click()   # company review BUTTON
        print("Wellcome to the review page!!!")
        
    except:
        print("FAILED TO LINK ON COMAPNY LINK")
    
    
    
# SEARCHING FOR NUMBER OF PAGES AVAILABLE
def review_count(chrome_driver):
    try:   
        # SEARCH FOR NUMBER OF REVIEWS STRING
        string = chrome_driver.find_element(By.CSS_SELECTOR, "div.paginationFooter")   
        r_string = string.text
        review_string = (r_string.split(' '))
        total_reviews = int(review_string[5].replace(',',''))   # total reviews available at company review page
        pages = round(total_reviews/10)   # total pages
        print("Total pages are: ", pages)
        
        return(pages)

    except:
        print('Error! string which contain the counts of review | NOT found | trying again.')


# SCRAPER CODE
def glassdoor_scraper(chrome_driver, pages):
    all_review_data = []
    page_source = chrome_driver.page_source
    soup = BeautifulSoup(page_source)
    review_link = soup.find('a', {'data-test' : 'ei-nav-reviews-link'})['href']
    review_link = "https://www.glassdoor.com" + review_link
    print("LINK : ", review_link)
    
    for i in range(1,pages+1):
        
        print("Page : ", i)
        page_link = "_P"+str(i)+".htm"        
        page_review_link = review_link.replace('.htm','') + page_link
        print("SCRAPPING FOR .....REVIEW PAGE LINK : ", page_review_link)
        chrome_driver.get(page_review_link)    
        
        page_review_source = chrome_driver.page_source
        pr_soup = BeautifulSoup(page_review_source)
        
        # SEARCHING FOR REVIEW_FEED
        print("---"*30)
        empReviews_Feeds = pr_soup.find_all('li', {'class' : 'noBorder empReview cf pb-0 mb-0'})
        print("REVIEW FOUND ON PAGE :", len(empReviews_Feeds))
        try:
            for empReviews in empReviews_Feeds:
                try:
                    #print("-------------\n")
                    emp_id = empReviews['id']
                    #print("REVIEWER ID :", emp_id)
                    review_title = empReviews.find('h2').text
                    review_link_ = empReviews.find('a')['href']
                    #print("REVIEW LINK : ", review_link_)
                    review_details = empReviews.find('span', {'class' : 'common__EiReviewDetailsStyle__newUiJobLine'}).text
                    review_time = review_details.split('-')[0]
                    reviewer_info = review_details.split('-')[1].replace('\xa0', '')
                    rating_ = empReviews.find('span',{'class':'ratingNumber mr-xsm'}).text
                    #print("REVIEW RATING :", rating_)
                    #print("REVIEW TIME :", review_time.strip())
                    #print("REVIEW TITLE :", review_title.strip())
                    #print("REVIEWER INFO :", reviewer_info.strip())
                    pros_ = empReviews.find('span', {'data-test' : 'pros'}).text
                    pros_ = pros_.replace('\xa0', '')
                    #print("PROS :", pros_)
                    cons_ = empReviews.find('span', {'data-test' : 'cons'}).text
                    cons_ = cons_
                    #print("CONS :", cons_)

                    data = {
                        'emp_id': emp_id,
                        'review_link' : review_link_,
                        'review_title' : review_title,
                        'review_rating' : rating_,
                        'emp_info' : reviewer_info ,
                        'review_time': review_time.strip(),
                        'pros': pros_,
                        'cons': cons_
                    }
                    all_review_data.append(data)
                    
                except Exception as e:
                    print(e)
                    continue
                    
            time.sleep(2)
            #print("---"*30)
        except:
            pass  
    return all_review_data