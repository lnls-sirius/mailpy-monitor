# use an official Python runtime as a parent image
FROM itorafael/epics-base:r3.15.6

MAINTAINER Rafael Ito <rafael.ito@lnls.br>
USER root

# set the working directory to /app
WORKDIR /app

# copy the necessary files into the container at /app
COPY ../sms.py /app
COPY ../sms_table.csv /app

# define environment variables
#ENV 

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

CMD ["python3", "sms.py"]
