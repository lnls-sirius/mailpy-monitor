FROM centos:7
LABEL br.cnpem.maintainer="Claudio Carneiro <claudio.carneiro@cnpem.br>"
LABEL br.cnpem.git="https://github.com/carneirofc/mailpy"
USER root

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /etc/yum/repos.d &&\
    rpm --import https://repo.anaconda.com/pkgs/misc/gpgkeys/anaconda.asc &&\
    echo "[conda]" > /etc/yum/repos.d/conda.repo &&\
    echo "name=Conda" >> /etc/yum/repos.d/conda.repo &&\
    echo "baseurl=https://repo.anaconda.com/pkgs/misc/rpmrepo/conda" >> /etc/yum/repos.d/conda.repo &&\
    echo "enabled=1" >> /etc/yum/repos.d/conda.repo &&\
    echo "gpgcheck=1" >> /etc/yum/repos.d/conda.repo &&\
    echo "gpgkey=https://repo.anaconda.com/pkgs/misc/gpgkeys/anaconda.asc" >> /etc/yum/repos.d/conda.repo

RUN yum install -y conda

RUN groupadd --gid 1001 mailpy &&\
    useradd --system \
    --create-home \
    --home-dir /home/mailpy \
    --shell /bin/bash \
    --uid 1001 \
    --gid mailpy \
    mailpy

RUN chown -R mailpy:mailpy /opt/conda

USER mailpy
WORKDIR /home/mailpy

RUN mkdir -p /home/mailpy/mailpy

ADD requirements.txt /home/mailpy/mailpy/requirements.txt

RUN /bin/bash -c \
    "source /opt/conda/etc/profile.d/conda.sh && \
    conda init &&\
    conda activate &&\
    conda install -y swig python=3.8.5 &&\
    conda install -c conda-forge epics-base pcaspy &&\
    pip install -r /home/mailpy/mailpy/requirements.txt"

ADD . /home/mailpy/mailpy

USER root
RUN chown -R mailpy:mailpy /home/mailpy/mailpy
USER mailpy

WORKDIR /home/mailpy/mailpy

ENV DB_URL mongodb://localhost:27017/mailpy-db

CMD /bin/bash -c '\
set -e;\
source /opt/conda/etc/profile.d/conda.sh;\
conda activate;\
set -x;\
python entrypoint.py\
    -p "$(cat /run/secrets/SMS_PASSWORD)"\
    --login "$(cat /run/secrets/SMS_LOGIN)"\
    --db_url "${DB_URL}"\
\'

