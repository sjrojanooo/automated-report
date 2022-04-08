FROM python:latest

# creates a working directory; 
WORKDIR /cooler-report 

COPY . /cooler-report 

RUN python3 pip install -m requirements.txt