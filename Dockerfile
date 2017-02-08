FROM ubuntu:16.04

ADD . ./librarian
WORKDIR ./librarian

RUN apt-get update
RUN apt-get install -y sl
#RUN apt-get -y install python python-pip
#RUN apt-get -y install mysql-client-core-5.7
#RUN apt-get -y install mysql-client-5.7
#RUN apt-get -y install libmysqlclient-dev
#RUN pip install -r requirements.txt
#RUN which mysql
#RUN mysql -u root -e "exit;"

#CMD ["python", "run.py"]
#RUN fab create_database
