# Set Base Image
FROM python:3.8-alpine

#EXPOSE 5000/tcp

#ENV FLASK_APP=app.py

COPY requirements.txt .

RUN apk update && apk add python3-dev \
    gcc \
    libc-dev

RUN pip3 install -r requirements.txt

COPY helper.py . 
COPY priceFeed.py . 
COPY run.py .
COPY abis.py .  
COPY logic.py . 
COPY eht_call.py . 
COPY config.json . 
COPY .env . 
