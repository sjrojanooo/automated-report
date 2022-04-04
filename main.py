from datetime import datetime # datetime to time the duration of the script; 
import time; # acts as a timeout function to give time between methods; 
from scrape_test import scrape_main; # importing my scraping and data manipulation py file;
from gmail_api import gmail_extract_load # gmail attachment handler to process attachment; 
from gmail_api import build_message; # builds and sends email with attachment; 


def main():

    # extracts fetch attachment and download it to the local directory; 
    gmail_extract_load(); 

    time.sleep(3)

    # transforms the data from the document; 
    scrape_main(); 

    time.sleep(3);
    
    # sends message, could be considered the load phase, since its sending out the scraped document(s)
    # back out to specific members of the payroll administration; 
    build_message();

 
    pass; 

if __name__ == "__main__":

    t1 = datetime.now()
    
    main(); 

    t2 = datetime.now()

    totalTime = t1 - t2; 

    print(f"Program took {totalTime} to run.")

    