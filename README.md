## Automated Report using Gmail API

I designed an automated reporting system that retrieves an attachment from a specified sender, parses the document, conditionally produces excel reports, and sends the information to various employees in the payroll department. 

The produced report from the service system provides a detailed report of every orgnization who reported product for that day. The task was to extract those products harvested by only the HM vendor, and also identify the area in which it was harvested. 

I have put some of the files that have already been produced with the nodejs program, these can be found in the data directory of the project. I want to rewrite the script in python to provide better readability and just get more practice with it. I will be updating this README file and providing some detail a little later. 

## The following steps are needed for the application
1. create a secrets directory that will hold the credentials.json and token.json file. This can be found gmail docs [here](https://developers.google.com/workspace/guides/create-credentials)

2. Create a .env file save sender email address as FOXY_PRODUCE_EMAIL. This will filter your inbox by email sent from this attachment. 

I am still going to work on moving all sent file into a data directory with the corresponding day. 