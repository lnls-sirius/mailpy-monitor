FROM continuumio/miniconda3:4.10.3 as mailpy

ENV DEBIAN_FRONTEND noninteractive
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN set -ex; \
    apt-get update &&\
    apt-get install -y --fix-missing --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*  && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN conda install -c conda-forge pcaspy -y

RUN mkdir -p -v /opt/mailpy/log
WORKDIR /opt/mailpy

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY scripts scripts
COPY setup.py setup.py
COPY src src
RUN pip install -e . -v

COPY scripts-dev/entrypoint.sh entrypoint.sh
ENTRYPOINT /bin/bash entrypoint.sh


FROM mongo:4.4.3-bionic as db

ENV MONGO_INITDB_DATABASE=mailpy
ENV MONGO_INITDB_ROOT_USERNAME=mailpy-admin
ENV MONGO_INITDB_ROOT_PASSWORD=mailpy-admin
ENV MONGO_INITDB_USERNAME=mailpy-user
ENV MONGO_INITDB_PASSWORD=mailpy-user

COPY ./src/mailpy/resources/00-create-db-users.sh    /docker-entrypoint-initdb.d/00-create-db-users.sh
COPY ./src/mailpy/resources/01-create-collections.js /docker-entrypoint-initdb.d/01-create-collections.js
