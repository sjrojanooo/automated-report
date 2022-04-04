from __future__ import print_function
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fileinput import filename
import mimetypes

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.base import MIMEBase
from mimetypes import MimeTypes, guess_type as guess_mime_type

import email.encoders; 

from io import BytesIO; # allows us to stream file in memory; 
import base64; # handles encoding and decoding of binary objects; 
from bs4 import BeautifulSoup; # to parse the htm documents table;
from dotenv import dotenv_values; # loading all dotenv variables; 
import pandas as pd; # pandas library; 
import datetime; # get date

# creating a dictionary from all the variables located in my .env file; 
config = {**dotenv_values(".env")}

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.modify",
"https://www.googleapis.com/auth/gmail.compose","https://www.googleapis.com/auth/gmail.send"];

# global variable that holds the email address 
foxy_email_address = config["FOXY_PRODUCE_EMAIL"]; 

def gmail_extract_load():

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=get_credentials())

        #performing the query to return all email threads from the automated systems email address; 
        results = query_foxy_product(service); 

        # retreiving the first instance of the message, this should be the most recent document received from the system; 
        msg = capture_message_id(service, results)

        # captruring the attachment in the body of the message and returning the binary object; 
        att = get_attachment_id(service, results, msg)

        # beautiful instance and parsing the html document; 
        soup = beautiful_soup_parsing(att)

        # writing object to local directory; 
        write_object_to_file(soup); 


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")




def get_credentials():

    """
    This is a GMAIL API template that can be found on the GMAIL API official documentation. 
    The original source was meant to get the list of mailbox labels from the intended users account. 
    I am implementing my own use case to automate some reporting for work. I removed the label fetch, 
    and am just using the credential authenticator part of the script to authorize access to my account.
    """
    creds = None
    # The file token.json stores the user"s access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("./secrets/token.json"):
        creds = Credentials.from_authorized_user_file("./secrets/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./secrets/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("./secrets/token.json", "w") as token:
            token.write(creds.to_json())

    return creds; 



# queries the email by the senders email address; 
def query_foxy_product(service: object):

        results = service.users()\
                        .messages()\
                            .list(
                                userId="me",
                                q = f"from: {foxy_email_address} is: unread").execute()
        return results; 

def capture_message_id(service:object, results: object): 

        # retreiving the first instance of the message, this should be the most recent document received from the system; 
        msg = service.users()\
                    .messages()\
                        .get(userId="me", id=results["messages"][0]["id"], format="full")\
                            .execute()
        return msg; 

def get_attachment_id(service:object, results:object, msg: object):

        # capturing the attachment Id, to perform a request for the body of the message with this target attachment Id; 
        target = msg["payload"]["body"]["attachmentId"]

        
        att = service.users()\
                    .messages()\
                        .attachments()\
                            .get(userId="me", messageId=results["messages"][0]["id"], id=target)\
                                .execute()
        return att; 

# decodes the captured attachment; 
def beautiful_soup_parsing(attachment: object):

        # processing the binary object and streaming it in memory. 
        # decoding the response to read its contents; 
        in_memory = BytesIO(base64.urlsafe_b64decode(attachment["data"]))

        
        soup = BeautifulSoup(in_memory, "html.parser")  

        return soup; 

# writes the beautiful soup object to the designated directory; 
def write_object_to_file(soup: object):

    # wrtiting the file to the local directory; 
    with open("./data/html-doc/cooler-report.htm", "w", encoding = "utf-8") as file:
    
        # prettify the soup object and convert it into a string  
        file.write(str(soup.prettify())); 


# walks directory to see which new files were created, splits by delimiter and retrieved the area for each file 
# and returns a list; 
def walk_data_excel_dir():
    
    area_list = []; 

    files_to_append = []; 

    for root, dir_names ,fileNames in os.walk(os.path.abspath("")):
        
        for f in fileNames: 

            # fileName is equal to the complete address to each file; 
            fileName = os.path.join(root, f);

            if f.endswith(".xlsx"):

                area_list.append(f.split("-")[0])

                files_to_append.append(fileName)

    return area_list, files_to_append; 


# prepares a the subject and body of the message conditionally by the len of the area_list obtained 
# after walking the directory; 
def prepare_mail(area_list: list):
    
    subject_message = None; 

    body_message = None; 

    date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")

    day_name = pd.to_datetime(date).day_name()

    if len(area_list) ==3: 

        subject_message = f"{area_list[0]}, {area_list[1]}, {area_list[2]} - HM - Cooler Report - {day_name} - {date}";

        body_message = f"Good Morning,\nAttached are the Harvest Management Cooler Reports from {area_list[0]}, {area_list[1]}, and {area_list[2]} for {date}. Have a great day everyone";

        return subject_message, body_message;    

    elif len(area_list) ==2: 

        subject_message = f"{area_list[0]}, {area_list[1]} - HM - Cooler Report - {day_name} - {date}";

        body_message = f"Good Morning,\nAttached are the Harvest Management Cooler Reports from {area_list[0]}, {area_list[1]}, and {area_list[2]} for {date}. Have a great day everyone";

        return subject_message, body_message;    

    elif len(area_list) ==1: 

        subject_message = f"{area_list[0]} - HM - Cooler Report - {day_name} - {date}";

        body_message = f"Good Morning,\nAttached are the Harvest Management Cooler Reports from {area_list[0]}, {area_list[1]}, and {area_list[2]} for {date}. Have a great day everyone";

        return subject_message, body_message;   


# creates message and attaches the files that reside in the file_names list variable; 
def create_and_send_message(sender: str, to:list, subject_message: str, body_message: str, file_names: list): 

    # builds subject and body of message; 
    message = MIMEMultipart()

    message["to"] = to; 
    message["from"] = sender; 
    message["subject"] = subject_message; 
    
    msg = MIMEText(body_message);

    message.attach(msg); 

    for file in file_names: 

        content_type, encoding = mimetypes.guess_type(file)

        main_type, sub_type = content_type.split('/',1); 

        fp = open(file, 'rb')
        msg = MIMEBase("application", "vnd.ms-excel")
        msg.set_payload(fp.read()); 
        email.encoders.encode_base64(msg)
        

        file_base_name = os.path.basename(file)


        msg.add_header('Content-Disposition', 'attachment', filename=file_base_name)
        message.attach(msg)
        fp.close()
        

        print(message)


    return {"raw":base64.urlsafe_b64encode(message.as_bytes()).decode()}

# just sent it to myself for trials; 
# successful; 
def build_message():

    service = build("gmail", "v1", credentials=get_credentials())

    message = create_and_send_message('sjrojano@gmail.com', 'sjrojano@gmail.com',prepare_mail(walk_data_excel_dir()[0])[0], prepare_mail(walk_data_excel_dir()[0])[1], walk_data_excel_dir()[1])

    (service.users().messages().send(userId="me", body=message)
               .execute())

