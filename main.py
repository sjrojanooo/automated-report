from datetime import datetime;
from bs4 import BeautifulSoup;
from collections import defaultdict; 
from io import StringIO;
import pandas as pd; 


def main():

    box_labels_df = read_json("./data/box-labels/box_labels.json"); 

    rows = soup_table_rows("./data/html-doc/cooler-report.htm"); 

    cooler_dict = create_dictionary(rows); 

    final_df = create_final_frame(create_frame(cooler_dict["lot_id"], ["vendor","lot_id"]),
                create_frame(cooler_dict["ranch"], ["vendor", "ranch"]),
                create_frame(cooler_dict["item_label"], ["vendor","item_label"]),
                create_frame(cooler_dict["item_name"], ["vendor","item_name"]),
                create_frame(cooler_dict["quantity"], ["vendor","quantity"])); 

    print(final_df)


# current box labels in use; 
def read_json(filePath: str):

    jsonDf = pd.read_json(filePath); 

    return jsonDf; 

# creates beautiful soup instance and return all rows; 
def soup_table_rows(filePath: str): 

    soup = StringIO();

    soup = BeautifulSoup(open(filePath,"r+"), "lxml"); 

    return soup.find_all("tr"); 

# creates a dictionary after html table scrap is complete; 
# the report has a ragged structure to it, and since its automatically generated there are 
# no class types for tables or rows. 
def create_dictionary(rows: object):

    report_dict = defaultdict(list);

    vendor_list = []; 

    count = 0; 
    
    for data in rows:

        vendor = "";

        vendor_list.append(data.find("td").text.strip());

        vendor = vendor_list.pop();

        for idx ,element in enumerate(data):
            if idx ==5:
                report_dict["lot_id"].append([vendor,element.text.strip()]);
            elif idx == 9:
                report_dict["ranch"].append([vendor,element.text.strip().title()]);
            elif idx == 13:
                report_dict["item_label"].append([vendor,element.text.strip()]);
            elif idx == 17:
                report_dict["item_name"].append([vendor,element.text.strip().title()]);
            elif idx == 21:
                report_dict["quantity"].append([vendor,element.text.strip()]);

    return report_dict; 

# normalized ragged dictionary and return a dataframe with the corresponding index value for each 
# 
# item in the report; 
def create_frame(report_dict: object, columns: list):

    dataframe = pd.DataFrame(report_dict, columns=columns); 

    dataframe["vendor"] = dataframe["vendor"].str.replace(r"(HM\d+)","HM",regex=True)\
                                    .str.replace(r"(HMR)","REPACK",regex=True)

    dataframe = dataframe[dataframe["vendor"].isin(["HM","REPACK"])]\
                    .reset_index()\
                        .drop(columns=["index", "vendor"]);

    return dataframe


def create_final_frame(lot_list: list, ranch_name: list, item_label: list,item_name: list, quantity: list):

    final_dataframe = pd.DataFrame({
        "lot_id": lot_list["lot_id"],
        "ranch": ranch_name["ranch"],
        "item_label": item_label["item_label"],
        "item_name":item_name["item_name"],
        "quantity": quantity["quantity"]
    }); 

    final_dataframe = final_dataframe.loc[final_dataframe["quantity"] != ""]


    return final_dataframe

def strip_label_column(dataFrame: object, column: str):

    dataFrame = dataFrame[column].str.replace(r" ","", regex=True)\
                    .str.replace(r"#","", regex=True)
    pass 

if __name__ == "__main__":

    t1 = datetime.now()
    
    main(); 

    t2 = datetime.now()

    totalTime = t1 - t2; 

    print(f"Program it took {totalTime}")

    