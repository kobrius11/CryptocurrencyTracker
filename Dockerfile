# syntax=docker/dockerfile:1
FROM python:slim-bullseye
ENV PYTHONBUFFERED=1
WORKDIR /app
COPY ./crypto_tracker .
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
RUN apt update
RUN apt install nano

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]