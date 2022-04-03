from __future__ import print_function
from email.header import decode_header

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from io import StringIO,BytesIO; 
import base64; 
from bs4 import BeautifulSoup; # to parse the htm documents table;
from dotenv import dotenv_values; # loading all dotenv variables; 

# creating a dictionary from all the variables located in my .env file; 
config = {**dotenv_values('.env')}
FOXY_PRODUCE_MAIL= config["FOXY_PRODUCE_EMAIL"]

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify',
'https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.send'];


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

        # performing a query that filters out all messages by a specific sender; 
        # I am replaces the email as a variable from my .env file to hide the contents; 
        results = service\
                    .users()\
                        .messages()\
                            .list(
                                userId='me',
                                q =f'from: {FOXY_PRODUCE_MAIL} is: unread').execute()

        messageId = results['messages'][0]['id']

        msg = service\
                .users()\
                    .messages()\
                        .get(userId='me', id=messageId, format='full').execute()
        
        target = msg['payload']['body']['attachmentId']

        att = service\
                .users()\
                    .messages()\
                        .attachments()\
                            .get(userId='me', messageId=messageId, id=target).execute()

        decoded_attachment = base64.b64decode(att['data'])

        print(decoded_attachment)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()