FROM continuumio/miniconda3:4.10.3

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
