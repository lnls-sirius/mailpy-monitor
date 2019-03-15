# use an official Python runtime as a parent image
FROM python:3

MAINTAINER Rafael Ito <rafael.ito@lnls.br>
USER root

# set the working directory to /app
WORKDIR /app

# copy the current directory contens into the container at /app
COPY . /app

# define environment variables
ENV EPICS_BASE /opt/epics-R3.15.6/base
ENV EPICS_HOST_ARCH linux-x86_64

# install EPICS base
RUN apt-get -y update
RUN apt-get install -y swig
RUN build/setup-epics.sh

# install needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# make ports 465 and 587 available to the world outside this container
# Port 465: authenticated SMTP over TLS/SSL (SMTPS)
# Port 587: email message submission (SMTP)
EXPOSE 465
EXPOSE 587

CMD ["python3", "sms.py"]
