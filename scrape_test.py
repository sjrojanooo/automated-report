from bs4 import BeautifulSoup; # to parse the htm documents table;
from collections import defaultdict; # to create a dictrionary 
import pandas as pd; # since its a small data set I decided to use pandas for the data manipulation; 

def scrape_main(): 

    # holds box labels that are update on in our inventory; 
    box_labels_df = read_json("./data/box-labels/box_labels.json"); 

    # creates a dictionary based of of the parsed information from the htm document; 
    rows, report_date = soup_table_rows_and_date("./data/html-doc/cooler-report.htm")

    # converting the report date to the day name; 
    report_day_name = get_report_day_name(report_date)

    # creating ragged dictionary; 
    cooler_dict = create_dictionary(rows); 

    # creating the final data frame of the product reported from cooler system; 
    final_df = create_final_frame(
                create_frame(cooler_dict["lot_id"], ["vendor","lot_id"]),
                create_frame(cooler_dict["ranch"], ["vendor", "ranch"]),
                create_frame(cooler_dict["item_label"], ["vendor","item_label"]),
                create_frame(cooler_dict["item_name"], ["vendor","item_name"]),
                create_frame(cooler_dict["quantity"], ["vendor","quantity"])
                ); 

    # getting the area list obtained 
    area_list = get_unique_list_of_area(final_df);

    # creating all necessary dataframe 
    dataFrame = conditional_frame(final_df, box_labels_df, area_list);

    # creating excel files - day name is also appended to them; 
    # files will be written out to the gmail-python/data/excel-doc path point; 
    condition_excel_files(dataFrame, area_list,report_day_name)

# current box labels in use; 
def read_json(filePath: str):

    jsonDf = pd.read_json(filePath); 

    return jsonDf; 

# creates beautiful soup instance and return all rows; 
def soup_table_rows_and_date(filePath: str): 
    
    soup = BeautifulSoup(open(filePath,"r+"), "lxml"); 

    rows = soup.find_all("tr"); 

    date = soup.find("td").text.strip()
    
    return rows, date; 

def get_report_day_name(date: str):

    report_day_name = pd.to_datetime(date).day_name(); 

    return report_day_name

"""
    creates a dictionary after html table scrap is complete; 
    the report has a ragged structure to it, and since its automatically generated there are 
    no class types for tables or rows. 
"""
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
# item in the report; 
def create_frame(report_dict: object, columns: list):

    dataframe = pd.DataFrame(report_dict, columns=columns); 

    dataframe["vendor"] = dataframe["vendor"].str.replace(r"(HM\d+)","HM",regex=True)\
                                    .str.replace(r"(HMR)","REPACK",regex=True)

    dataframe = dataframe[dataframe["vendor"].isin(["HM","REPACK"])]\
                    .reset_index()\
                        .drop(columns=["index", "vendor"]);

    return dataframe

# creating the final formatted frame; 
def create_final_frame(lot_list: list, ranch_name: list, item_label: list,item_name: list, quantity: list):

    final_dataframe = pd.DataFrame({
        "lot_id": lot_list["lot_id"],
        "ranch": ranch_name["ranch"],
        "item_label": item_label["item_label"],
        "item_name":item_name["item_name"],
        "quantity": quantity["quantity"]
    }); 

    final_dataframe = final_dataframe.loc[final_dataframe["quantity"] != ""]

    final_dataframe = strip_label_column(final_dataframe, 'item_label')

    final_dataframe = create_area_column(final_dataframe, 'lot_id','area')

    final_dataframe = remove_delimeter_from_int(final_dataframe, 'quantity')

    return final_dataframe

# removing special characters and whitespaces from the item_label, 
# this assures that the unique labels will be an exact match to the labels we have available on our end; 
def strip_label_column(dataFrame: object, column: str):

    dataFrame[column] = dataFrame[column].str.replace(r" ","", regex=True)\
                            .str.replace(r"#","", regex=True)
    
    return dataFrame

# Creates our area column; 
def create_area_column(dataFrame: object, lot_id_column: str, area_column: str):

    dataFrame[area_column] = dataFrame[lot_id_column]\
                                .astype(str)\
                                    .str.replace(r'''\w{1}\d+''','', regex=True)

    """
    filtering method to set all areas by the alhpabetic character from the replace method above; 
    figured out the A & B stand for Huron A in this case is Fall and B is for Spring; 
    Y and S are for Yuma and Salinas respectively; 
    """
    dataFrame.loc[((dataFrame[area_column] == 'A') | (dataFrame[area_column] == 'B')), area_column] = 'Huron'
    dataFrame.loc[dataFrame[area_column] == 'S', area_column] = "Salinas"
    dataFrame.loc[dataFrame[area_column] == 'Y', area_column] = "Yuma"

    return dataFrame

# removing the comma delimiter from the decimal data types in the report; 
# doing so to complete a sum aggregation to show grand totals for each commoodity; 
def remove_delimeter_from_int(dataFrame: object, quantity_column: str):

    dataFrame[quantity_column] = dataFrame[quantity_column]\
                                    .str.replace(",","", regex=True)\
                                            .astype(float).astype(int)

    return dataFrame

# getting the unique count of areas that reported product; 
def get_unique_list_of_area(dataFrame: object): 

    area_list = sorted(dataFrame['area'].unique()); 

    return area_list; 

# joining products conditionally to the area;
# if more than one area reported product, I decided to return a list or tuple
def conditional_frame(dataFrame: object, boxDataFrame, area_list: list):

    try: 
        if len(area_list) == 1: 

            return join_data_by_area(dataFrame,boxDataFrame, area_list[0])

        elif len(area_list) == 2: 

            return join_data_by_area(dataFrame,boxDataFrame, area_list[0]), join_data_by_area(dataFrame,boxDataFrame, area_list[1])

        elif len(area_list) == 3: 
            
            return join_data_by_area(dataFrame,boxDataFrame, area_list[0]), join_data_by_area(dataFrame,boxDataFrame, area_list[1]), join_data_by_area(dataFrame,boxDataFrame, area_list[2])
    except: 

        raise print("error happened at conditional_frame method")
        
    
# returning the column name on which I will be performing the join on; 
def return_box_label_columns(area: str):

    billing_center = None; 

    if area == 'Salinas':
        billing_center = 'ca_cost_center'
    elif area == 'Yuma':
        billing_center = 'az_cost_center'
    else: 
        billing_center = 'hu_cost_center'

    columns = ['item_label','commodity',billing_center]; 

    return columns; 

"""
    using a left merge which is similary to left join in sql to combine on the item lable 
    relationship with the area. It uses this, because there are cases in which the automated processing system from 
    the cooler creates a new label that we do not have saved on our end. I leave the field as an empty space instead
"""
def join_data_by_area(dataFrame: object, boxDataFrame: object, area: str): 

    filterd_frame = dataFrame[dataFrame['area'].isin([area])];

    boxDataFrame = boxDataFrame[return_box_label_columns(area=area)];

    joined_frame = filterd_frame.merge(boxDataFrame, on='item_label', how='left').fillna('New Label');

    return joined_frame; 

# Grand Summary Files finished; 
def create_grand_summary(dataFrame: object):

    columns = ['commodity','quantity']

    dataFrame = dataFrame[columns]\
                    .groupby(['commodity'], as_index=False)\
                        .sum().sort_values('commodity'); 

    grand_total = pd.DataFrame({
        'commodity':['Grand Total'],
        'quantity': dataFrame['quantity'].sum()
    })

    dataFrame = pd.concat([dataFrame, grand_total])

    return dataFrame

# Excel File Writer 
def create_excel_files(detailed_frame: object, grand_sum_frame: object, area: str, report_date: str):

    writer = pd.ExcelWriter(f"./data/excel-doc/{area}-Summary-{report_date}.xlsx", engine="openpyxl");

    grand_sum_frame.to_excel(writer, sheet_name=f"{area}-Grand-Summary", index=False);

    detailed_frame.to_excel(writer, sheet_name=f"{area}-Detailed-Summary", index=False);
    

    writer.sheets[f"{area}-Grand-Summary"].column_dimensions['A'].width = 17
    writer.sheets[f"{area}-Grand-Summary"].column_dimensions['B'].width = 10

    writer.sheets[f"{area}-Detailed-Summary"].column_dimensions['A'].width = 12
    writer.sheets[f"{area}-Detailed-Summary"].column_dimensions['B'].width = 35
    writer.sheets[f"{area}-Detailed-Summary"].column_dimensions['C'].width = 15
    writer.sheets[f"{area}-Detailed-Summary"].column_dimensions['D'].width = 40
    writer.sheets[f"{area}-Detailed-Summary"].column_dimensions['E'].width = 20
    writer.sheets[f"{area}-Detailed-Summary"].column_dimensions['F'].width = 17
    writer.sheets[f"{area}-Detailed-Summary"].column_dimensions['G'].width = 15

    writer.save()


# Conditional excel files with detailed and grand summary representation; 
def condition_excel_files(detailed_frame: object, area_list: str, report_date: str):

    if len(area_list) == 1: 
        create_excel_files(detailed_frame=detailed_frame[0], grand_sum_frame=create_grand_summary(detailed_frame[0]), area=area_list[0], report_date=report_date)

    elif len(area_list) == 2: 
        create_excel_files(detailed_frame=detailed_frame[0], grand_sum_frame=create_grand_summary(detailed_frame[0]), area=area_list[0], report_date=report_date)
        create_excel_files(detailed_frame=detailed_frame[1], grand_sum_frame=create_grand_summary(detailed_frame[1]), area=area_list[1], report_date=report_date)

    elif len(area_list) == 3: 
        create_excel_files(detailed_frame=detailed_frame[0], grand_sum_frame=create_grand_summary(detailed_frame[0]), area=area_list[0], report_date=report_date)
        create_excel_files(detailed_frame=detailed_frame[1], grand_sum_frame=create_grand_summary(detailed_frame[1]), area=area_list[1], report_date=report_date)
        create_excel_files(detailed_frame=detailed_frame[2], grand_sum_frame=create_grand_summary(detailed_frame[2]), area=area_list[2], report_date=report_date)