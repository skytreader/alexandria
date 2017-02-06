FROM mysql:mysql-server

FROM python:2.7-wheezy
ADD ./librarian
WORKDIR ./librarian
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
