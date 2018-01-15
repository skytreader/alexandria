FROM ubuntu:16.04
COPY . ./librarian
WORKDIR ./librarian
ENV ALEXANDRIA_CONFIG='/librarian/docker_config.py'
# This line is specifically for travis-ci builds.
RUN useradd --create-home --shell /bin/bash travis

RUN apt-get update
RUN apt-get install -y libmysqlclient-dev python python-pip
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt
