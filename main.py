from datetime import datetime # datetime to time the duration of the script; 
import time; # acts as a timeout function to give time between methods; 
from scrape_test import scrape_main; # importing my scraping and data manipulation py file
from gmail_api import gmail_extract_load # gmail attachment handler to process attachment; 
from gmail_api import walk_data_excel_dir; 
from gmail_api import build_message; 


def main():

    gmail_extract_load(); 

    # so the newest document in the html directory get read I added a sleep of 5 seconds; 
    time.sleep(3)

    scrape_main(); 
    time.sleep(3);
    build_message();

 
    pass; 

if __name__ == "__main__":

    t1 = datetime.now()
    
    main(); 

    t2 = datetime.now()

    totalTime = t1 - t2; 

    print(f"Program it took {totalTime}")

    