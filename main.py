from datetime import datetime # datetime to time the duration of the script; 
from scrape_test import scrape_main; 

def main():

    scrape_main(); 
    
    pass; 

if __name__ == "__main__":

    t1 = datetime.now()
    
    main(); 

    t2 = datetime.now()

    totalTime = t1 - t2; 

    print(f"Program it took {totalTime}")

    