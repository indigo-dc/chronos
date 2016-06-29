FROM ubuntu:14.04
MAINTAINER Marica Antonacci <marica.antonacci@gmail.com>

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl python-dev python-pip python-netifaces && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install awscli python-keystoneclient python-swiftclient

RUN curl --insecure -sS  https://get.onedata.org/oneclient.sh | bash

ENV AUTHENTICATION=token
ENV NO_CHECK_CERTIFICATE=true

COPY run.sh /

ENTRYPOINT ["/run.sh"]

