FROM python:3.12

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    poppler-utils

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .