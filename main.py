from datetime import datetime # datetime to time the duration of the script; 
import time; # set a timeout when running the application; 
from scrape_test import scrape_main; # importing my scraping and data manipulation py file
from gmail_api import gmail_main; # importing gmail api extract and load method; 


def main():

    # performs query, downloads attachment; 
    # Extract, and partly load phase for the html document; 
    gmail_main(); 

    # so the newest document in the html directory get read I added a sleep of 3 seconds; 
    time.sleep(3)

    # Transform and load phase - for the excel files; 
    scrape_main(); 
    
if __name__ == "__main__":

    t1 = datetime.now()
    
    main(); 

    t2 = datetime.now()

    totalTime = t1 - t2; 

    print(f"Program took {totalTime}")

    