FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y python python-pip
RUN apt-get install -y mysql-server-5.7
RUN apt-get install -y mysql-client-core-5.7
RUN apt-get install -y mysql-client-5.7
RUN apt-get install -y libmysqlclient-dev

ADD ./librarian
WORKDIR ./librarian

RUN pip install -r requirements.txt
