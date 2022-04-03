from __future__ import print_function
from email.header import decode_header

import os.path
import zipfile

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from io import BytesIO; # allows us to stream file in memory; 
import base64; # handles encoding and decoding of binary objects; 
from bs4 import BeautifulSoup; # to parse the htm documents table;
from dotenv import dotenv_values; # loading all dotenv variables; 

# creating a dictionary from all the variables located in my .env file; 
config = {**dotenv_values('.env')}

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify',
'https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.send'];

# global variable that holds the email address 
foxy_email_address = config["FOXY_PRODUCE_EMAIL"]; 

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('./secrets/token.json'):
        creds = Credentials.from_authorized_user_file('./secrets/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './secrets/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./secrets/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

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
        print(f'An error occurred: {error}')


def query_foxy_product(service: object):

        results = service.users()\
                        .messages()\
                            .list(
                                userId='me',
                                q = f'from: {foxy_email_address} is: unread').execute()
        return results; 

def capture_message_id(service:object, results: object): 

        # retreiving the first instance of the message, this should be the most recent document received from the system; 
        msg = service.users()\
                    .messages()\
                        .get(userId='me', id=results['messages'][0]['id'], format='full')\
                            .execute()
        return msg; 

def get_attachment_id(service:object, results:object, msg: object):

        # capturing the attachment Id, to perform a request for the body of the message with this target attachment Id; 
        target = msg['payload']['body']['attachmentId']

        
        att = service.users()\
                    .messages()\
                        .attachments()\
                            .get(userId='me', messageId=results['messages'][0]['id'], id=target)\
                                .execute()
        return att; 

def beautiful_soup_parsing(attachment: object):

        # processing the binary object and streaming it in memory. 
        # decoding the response to read its contents; 
        in_memory = BytesIO(base64.urlsafe_b64decode(attachment['data']))

        
        soup = BeautifulSoup(in_memory, 'html.parser')  

        return soup; 

def write_object_to_file(soup: str):

    # wrtiting the file to the local directory; 
    with open("./data/html-doc/cooler-report.htm", "w", encoding = 'utf-8') as file:
    
        # prettify the soup object and convert it into a string  
        file.write(str(soup.prettify())); 

if __name__ == '__main__':
    main()