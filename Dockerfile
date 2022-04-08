FROM python:latest

# creates a working directory; 
WORKDIR /cooler

COPY . /cooler

RUN python3 pip install -m requirements.txt