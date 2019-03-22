# use an official Python runtime as a parent image
FROM itorafael/epics-base:r3.15.6

LABEL maintainer="Rafael Ito <rafael.ito@lnls.br>"
USER root

# set the working directory to /app
WORKDIR /app

# copy the "requirements.txt" file to container
COPY requirements.txt /app
# install prerequisites
RUN apt-get update -y
RUN apt-get install -y \
    swig \
    python3 \
    python3-pip
# install needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# make ports 465 and 587 available to the world outside this container
# Port 465: authenticated SMTP over TLS/SSL (SMTPS)
# Port 587: email message submission (SMTP)
EXPOSE 465
EXPOSE 587

# define environment variables
ENV EPICS_CA_ADDR_LIST="$EPICS_CA_ADDR_LIST localhost"
ARG CONS2_SMS_PASSWD

# copy necessary files to container
COPY app/sms.py /app
COPY app/sms_table.csv /app

CMD python3 sms.py -p ${CONS2_SMS_PASSWD}
