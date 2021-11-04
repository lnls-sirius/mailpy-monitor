FROM continuumio/miniconda3:4.10.3

LABEL br.cnpem.maintainer="Claudio Carneiro <claudio.carneiro@cnpem.br>"
LABEL br.cnpem.git="https://github.com/carneirofc/mailpy-monitor"

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# set correct timezone
ENV DEBIAN_FRONTEND noninteractive
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN set -ex; \
    apt-get update &&\
    apt-get install -y --fix-missing --no-install-recommends \
        build-essential \
        ca-certificates \
        gettext-base \
        libpcre3-dev \
        libreadline-gplv2-dev \
        logrotate \
        tzdata \
        wget \
        && rm -rf /var/lib/apt/lists/*  && \
    dpkg-reconfigure --frontend noninteractive tzdata

RUN conda install -c conda-forge pcaspy -y

RUN mkdir -p -v /opt/mailpy
WORKDIR /opt/mailpy
COPY . .
RUN pip install -y -r requirements.text

ENTRYPOINT /bin/bash entrypoint.sh
