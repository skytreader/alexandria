FROM ubuntu:16.04
ADD . ./librarian
WORKDIR ./librarian

RUN apt-get update
RUN apt-get install -y libmysqlclient-dev python python-pip
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
