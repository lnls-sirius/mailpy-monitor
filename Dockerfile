# use an unofficial image with EPICS base (Debian 9) as a parent image
FROM itorafael/epics-base:r3.15.6
LABEL maintainer="Rafael Ito <rafael.ito@lnls.br>"
USER root

#================================================
# install prerequisites
#================================================
RUN apt-get update && apt-get install -y \
    swig \
    python3 \
    python3-pip
#------------------------------------------------
# copy "requirements.txt" file and install needed packages
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt
#------------------------------------------------
# set correct timezone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#================================================
# PORTS exposure
#================================================
# make ports 465 and 587 available to the world outside this container
# Port 465: authenticated SMTP over TLS/SSL (SMTPS)
# Port 587: email message submission (SMTP)
EXPOSE 465
EXPOSE 587

#================================================
# Environment Variables
#================================================
#ENV EPICS_CA_ADDR_LIST="$EPICS_CA_ADDR_LIST localhost"
ARG CONS2_SMS_PASSWD

#================================================
# start the container
#================================================
WORKDIR /app
COPY app/sms.py /app
COPY app/sms_table.csv /app
CMD python3 sms.py -p ${CONS2_SMS_PASSWD}
