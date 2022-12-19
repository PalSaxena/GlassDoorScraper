import pandas as pd
from utils import login_into_glassdoor, review_count, get_review_page, Create_driver, glassdoor_scraper
from config import glassdoor_login_url, username, password, path_to_chrome_driver

class glassdoor_scraper_class():

    def __init__(self, path_to_chrome_driver):
        self.url = glassdoor_login_url
        self.path_to_chrome_driver = path_to_chrome_driver
        self.driver = Create_driver(self.url, self.path_to_chrome_driver).get_driver()     
        
        # GET LOGED IN DRIVER(BROWSER) INSTANCE
        self.chrome_driver = login_into_glassdoor(self.driver, username, password)

    def scrap_by_company_name(self, company_name):
        # GET REVIEW PAGE OF THE COMPANY
        get_review_page(self.driver, company_name) 

        # GET THE NUMBER OF REVIEW PAGES AVAILABLE TO SCRAP
        pages = review_count(self.driver)

        # GET REVIEWS
        glassdoor_review = glassdoor_scraper(self.driver, pages)

        return glassdoor_review


if __name__ == "__main__":
    path_to_chrome_driver = "./chromedriver.exe"
    all_reviews = glassdoor_scraper_class(path_to_chrome_driver).scrap_by_company_name("Scanta")

    # SAVING DATA TO CSV
    print("||Saving the Scraped Data||")
    df_reviews_scanta = pd.DataFrame(all_reviews)
    df_reviews_scanta.to_csv("Reveiws_Scanta.csv", index=False)
    df_reviews_scanta
    
    # SAVING DATA TO JSON
    # print("||Saving the Scraped Data||")
    # with open('GlassDoorScraper1.json', 'w') as f:     
    #     json.dump(glassdoor_review, f, indent=4)