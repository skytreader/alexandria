FROM ubuntu:16.04

RUN apt-get update && apt-get install -y libmysqlclient-dev python python-pip xvfb firefox
COPY . ./librarian
WORKDIR ./librarian
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt
ENV ALEXANDRIA_CONFIG='config.DockerConfig'
# This line is specifically for travis-ci builds.
RUN useradd --create-home --shell /bin/bash travis
