FROM centos:7
LABEL maintainer="Claudio Carneiro <claudio.carneiro@cnpem.br>"
LABEL github="https://github.com/carneirofc/mailpy"
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

RUN yum install conda -y

RUN groupadd --gid 1001 wsgi &&\
    useradd --system \
            --create-home \
            --home-dir /home/wsgi \
            --shell /bin/bash \
            --uid 1001 \
            --gid wsgi \
            wsgi

RUN chown -R wsgi:wsgi /opt/conda

USER wsgi
WORKDIR /home/wsgi

RUN mkdir -p /home/wsgi/mailpy

ADD requirements.txt /home/wsgi/mailpy/requirements.txt

RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate &&\
    conda install -y swig python=3.8.5 &&\
    conda install -c conda-forge epics-base pcaspy &&\
    pip install -r /home/wsgi/mailpy/requirements.txt"

ADD . /home/wsgi/mailpy

WORKDIR /home/wsgi/mailpy

ENV DB_URL mongodb://localhost:27017/mailpy-db

CMD /bin/bash -c 'source /opt/conda/etc/profile.d/conda.sh &&\
    conda activate &&\
    python entrypoint.py \
        -p "$(cat /run/secrets/SMS_PASSWORD)"\
        --login "$(cat /run/secrets/SMS_LOGIN)"\
        --db_url "${DB_URL}" '

