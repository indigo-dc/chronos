FROM ubuntu:15.10
MAINTAINER Marica Antonacci <marica.antonacci@gmail.com>

ARG ONEDATA_VERSION="3.0.0-beta4"

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl python-netifaces python-requests python-pip && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install awscli python-keystoneclient python-swiftclient

RUN curl -o install.sh http://onedata-dev-packages.cloud.plgrid.pl/oneclient.sh && \
sh install.sh ${ONEDATA_VERSION}

ENV AUTHENTICATION=token
ENV NO_CHECK_CERTIFICATE=true

COPY run.sh /

ENTRYPOINT ["/run.sh"]

