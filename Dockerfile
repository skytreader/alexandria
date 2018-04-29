FROM ubuntu:16.04

RUN apt-get update && apt-get install -y libmysqlclient-dev python python-pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . ./librarian
WORKDIR ./librarian
ENV ALEXANDRIA_CONFIG='config.DefaultAlexandriaConfig'
RUN python run.py
