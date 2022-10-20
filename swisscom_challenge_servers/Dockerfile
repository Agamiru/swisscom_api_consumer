FROM python:3.9.11
ENV PYTHONUNBUFFERED=1
WORKDIR /swisscom_challenge_servers/
COPY requirements.txt /swisscom_challenge_servers/requirements.txt
RUN pip install -r requirements.txt
COPY . /swisscom_challenge_servers/
EXPOSE 5000
# CMD make runserver