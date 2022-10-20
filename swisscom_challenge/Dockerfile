FROM python:3.9.11
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=1
WORKDIR /swisscom_challenge/
COPY requirements.txt /swisscom_challenge/requirements.txt
RUN pip install -r requirements.txt
COPY . /swisscom_challenge/