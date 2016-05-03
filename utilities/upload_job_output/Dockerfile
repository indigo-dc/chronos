FROM python:2.7
MAINTAINER Marica Antonacci <marica.antonacci@gmail.com>

RUN pip install awscli python-keystoneclient python-swiftclient

COPY run.sh /

ENTRYPOINT ["/run.sh"]

