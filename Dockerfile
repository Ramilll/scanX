FROM python:3.12-slim

WORKDIR /app
RUN mkdir -p /app/data

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

# COPY . .
