FROM python:latest

# creates a working directory; 
WORKDIR /automate 

COPY . /automate

RUN python3 pip install -m requirements.txt