#!/usr/bin/python3
# -*- coding: utf-8 -*-
#==============================================================================
'''
#==============================================================================
    SMS: Spam Mailing Service (former CMS - CON Mailing Service)
#==============================================================================
README:
----------
This code reads a list of EPICS PVs and their corresponding specified values
from a CSV file and monitor them. If any these PVs is not in it's specified
value, an e-mail is sent with a warning message to one or a list of e-mail
address.

So far, it's monitoring the following systems:
    - water temperature of Linac Klystron 1
    - water temperature of Linac Klystron 2
    - water temperature of Linac Accelerating Structures
    - total dose of radiation detectors (Thermo, ELSE, Berthold)
#==============================================================================
To do:
----------
    - if cell is empty, its breaking the code
    - from time to time read csv file to update tables (?)
    - support for condition 'decreasing step' (similar to 'increasing step')
    - loop for generating PVs according to csv colums (check "test.py")
    - supervisory for the SMS (Spam Mail Server) --> PyDM? Web?
        - load supervisory by reading csv file (similar to this code)
#==============================================================================
Syntax:
----------
    - cells should not be left empty!
    - separate e-mails with semicolon (";") and no space
        e.g.: "rafael.ito@lnls.br;ito.rafael@gmail.com"
    - separate specified value with colon (":") and no space
        e.g.:
        "out of range"     -->  "17:22"
        "increasing step"  -->  "1.0:1.5:2.0:2.5:3.0"
        "superior than"    -->  "46"
#==============================================================================
CSV definitions:
    conditions:
        -"out of range"
        -"if superior than"
        -"if inferior than"
        -"increasing step"
        -"decreasing step"
#==============================================================================
'''
#==============================================================================
# general libraries
import sys
import ssl
import getpass
import argparse
import time
import threading
import pandas as pd
#import numpy as np
#---------------------------------------
# EPICS libraries
from pcaspy import Driver, SimpleServer
#from epics import caget, caput, camonitor
from epics import caget
#---------------------------------------
# log libraries
import logging
from logging.handlers import RotatingFileHandler
import traceback
#---------------------------------------
# mailing libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#==============================================================================
# define minimum time between emails in seconds
#TIMEOUT = 60*60
#==============================================================================
# Parsing arguments
#==============================================================================
parser = argparse.ArgumentParser(description='Monitor PV EPICS values and if any of them isn\'t in a specified range, email a warning message to a list of targets.')
#---------------------------------------
# security and encryption
parser.add_argument(
    '--tls',
    action='store_true',
    help='start an unsecured SMTP connection and encrypt it using .starttls() (default: use SMTP_SSL)'
    )
#---------------------------------------
# select who is sending the email
parser.add_argument(
    '-l', '--login',
    metavar='email@example.com',
    default='controle.supervisorio@gmail.com',
    help='define the sender email (default: controle.supervisorio@gmail.com)'
    )
#---------------------------------------
# password
parser.add_argument(
    '-p', '--passwd',
    metavar='my_password',
    help='set the password used when trying to log in'
    )
#---------------------------------------
# table (csv file) that will be used
parser.add_argument(
    '-t', '--table',
    metavar='my_table.csv',
    default='sms_table.csv',
    help='choose the csv file to read data from (default: sms_table.csv)'
    )
#---------------------------------------
args = parser.parse_args()
#==============================================================================
# read csv file, read its values and store them in variables
df = pd.read_csv(args.table)
# parse e-mail column
email = df['emails']
'''
# the following section was used when the SAME email list was used for all PVs monitored
for i in range(len(df['emails'])):
    # check if cell is NaN
   if(not df['emails'].isnull()[i]):
        email.append(df['emails'][i])
'''
# parse other columns
pv = df['PV']
condition = df['condition']
value = df['specified value']
unit = df['measurement unit']
warning = df['warning message']
subject = df['email subject']
timeout = df['timeout']
enable = df['enable PV']
#==============================================================================
# Composing the email
#==============================================================================
def compose_msg(PV_name, PV_value, specified_value, unit, warning, subject, email):
    '''
    input parameter:
        - PV_name: [str] EPICS PV that exceeded the limits
        - PV_value: value of the PV
        - specified_value: [str] range considered as normal for a given PV
        - unit: measurement unit of the PV
        - warning: warning message
        - subject: title of the e-mail
        - email: e-mail of the targets that will receive the message as one string separated with ';'
            --> e.g.: 'rafael.ito@lnls.br;ito.rafael@gmail.com'
    output parameter:
        - msg: body of the e-mail that will be sent
    '''
    # define headers of email: From, To and Subject
    #sender_email    = "controle.supervisorio@gmail.com"
    #receiver_email  = "rafael.ito@lnls.br"
    #subject_email   = "Linac Water Temperature Warning"
    #body_email      = "Hello World!"
    #msg = MIMEMultipart()
    #---------------------------------------
    # composing message headers
    msg = MIMEMultipart("alternative")
    msg['From']     = args.login
    #msg['To']       = 'rafael.ito@lnls.br, ito.rafael@gmail.com'
    msg['To']       = email.replace(';', ', ')
    msg['Cc']       = ""
    msg['Bcc']      = ""
    msg['Subject']  = subject
    #==============================================================================
    # Defining message to be sent
    #==============================================================================
    # formating timestamp
    from time import localtime, strftime
    timestamp = strftime("%a, %d %b %Y %H:%M:%S", localtime())

    # creating the plain-text format of the message
    text = warning + """\

 - PV name:         """ + PV_name   + """
 - Specified range: """ + specified_value + """
 - Value measured:  """ + PV_value  + " " + unit + """
 - Timestamp:       """ + timestamp + """

 Archiver link: https://10.0.38.42

 Controls Group
 """
    #---------------------------------------
    # creating the HTML version of the message
    # +/- signal: &#177
    html = """\
    <html>
        <body>
            <p>""" + warning + """<br>
                <ul>
                    <li><b>PV name:         </b>""" + PV_name   + """<br></li>
                    <li><b>Specified range: </b>""" + specified_value + """<br></li>
                    <li><b>Value measured:  </b>""" + PV_value  + " " + unit + """<br></li>
                    <li><b>Timestamp:       </b>""" + timestamp + """<br></li>
                </ul>
                Archiver link: <a href="https://10.0.38.42">https://10.0.38.42<a><br><br>
                Controls Group
            </p>
        </body>
    </html>
    """
    #------------------------------------------------------------------------------
    # convert the above into plain/html MIMEText objects
    text_part = MIMEText(text, "plain")
    html_part = MIMEText(html, "html")
    # add html/plain-text parts to MIMEMultipart message
    # the email client will try to render the last part first (in this case the html)
    msg.attach(text_part)
    msg.attach(html_part)
    return msg
#==============================================================================
# Starting a Secure SMTP Connection
#==============================================================================
def send_email(login, password, email, msg):
    '''
    input parameters:
        - login: sender of the email
        - password: password of the login user that will send the email
        - email: e-mail of the targets that will receive the message as one string separated with ';'
            --> e.g.: 'rafael.ito@lnls.br;ito.rafael@gmail.com'
        - msg: the message in the body of the email that will be sent
        - password:
    '''
    email = email.split(';')
    #------------------------------------------------------------------------------
    # Option 1: using .starttls()
    # start an unsecured SMTP connection and then encrypt it
    #---------------------------------------
    if(args.tls):
        #print('TLS')
        # Gmail SMTP server requires a connection with port 587 if using .starttls()
        port = 587
        # Create a secure SSL context
        context = ssl.create_default_context()
        # try to log in to server and send email
        try:
            server = smtplib.SMTP('smtp.gmail.com', port)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            # print login and ask for password
            print("login:", login)
            #password = getpass.getpass(prompt='password: ')
            #---------------------------------------
            # logging in and sending the email
            server.login(login, password)
            print("email to:")
            for i in range(len(email)): print("    *", email[i])
            server.sendmail(login, email, msg.as_string())
            #---------------------------------------
            print("========================================")
            print("email has been sent with success!")
            print("========================================\n")
        except Exception as e:
            print("\nSMTPAuthenticationError: username and password not accepted.")
        finally:
            server.quit()
    #---------------------------------------
    # Option 2: using SMTP_SSL()
    # start a secured SMTP connection from the beginning
    #---------------------------------------
    else:
        #print('SSL')
        # Gmail SMTP server requires a connection with port 465 if using SMTP_SSL()
        port = 465
        # Create a secure SSL context
        context = ssl.create_default_context()
        # create an SMTP object, used to connect to one server
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            try:
                # print login and ask for password
                print("login:", login)
                #password = getpass.getpass(prompt='password: ')
                #---------------------------------------
                # logging in and sending the email
                server.login(login, password)
                print("email to:")
                for i in range(len(email)): print("    *", email[i])
                server.sendmail(login, email, msg.as_string())
                #---------------------------------------
                print("========================================")
                print("email has been sent with success!")
                print("========================================\n")
            except Exception as e:
                print("\nSMTPAuthenticationError: username and password not accepted.")
#==============================================================================
# creating PVs using PCASpy
#==============================================================================
PV = {}
# create general PV to enable/disable the whole SMS
PV = {
    "CON:MailServer:Enable" : {
        'type'  : 'enum',
        'enums' : ['Off', 'On'],
        'value' : 1,
    },
}
# create PVs for disabling groups of PVs monitored
enable_grp = list(set(enable))
for i in enable_grp:
    aux = {
        i : {
            'type' : 'enum',
            'enums' : ['Off', 'On'],
            'value' : 1,
        }
    }
    PV.update(aux)
#---------------------------------------
# EPICS driver
class PSDriver(Driver):
    # class constructor
    def __init__(self):
        # call the superclass constructor
        Driver.__init__(self)
    # writing in PVs function
    def write(self, reason, value):
        self.setParam(reason, value)
        self.updatePVs()
        return (True)
#---------------------------------------
# start EPICS server
CAserver = SimpleServer()
CAserver.createPV("", PV)
driver = PSDriver()
#---------------------------------------
# thread_1 is responsible for maintaining the process status PVs
def thread_1():
    while(True):
        CAserver.process(0.1)
#==============================================================================
# initializing the logger
#==============================================================================
#logging.basicConfig(filename='sms.log', format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%b-%d %H:%M:%S', level=logging.DEBUG)
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# the next section was used when dealing with handler "FileHandler"
'''
# create file handler and set level to debug
fh = logging.FileHandler('sms.log')
fh.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%b-%d %H:%M:%S')
# add formatter to fh
fh.setFormatter(formatter)
# add fh to logger
logger.addHandler(fh)
'''

# for handler "RotatingFileHandler", used the above
# create file handler and set level to debug
rfh = RotatingFileHandler("sms.log", maxBytes=10000, backupCount=5)
# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%b-%d %H:%M:%S')
# add formatter to rfh
rfh.setFormatter(formatter)
# add rfh to logger
logger.addHandler(rfh)

#==============================================================================
# main loop: check if PVs and email targets if not in specified range
#==============================================================================
def thread_2():
    try:
        # reset last_event_time for all PVs, so it start monitoring right away
        last_event_time = []
        start_time = time.time()
        for i in range(len(timeout)):
            last_event_time.append(start_time - timeout[i])
        #=======================================
        # ask for authentication in gmail account
        #=======================================
        authentication = False
        context = ssl.create_default_context()
        while(authentication == False):
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                try:
                    if(args.passwd != None):
                        password = args.passwd
                        server.login(args.login, password)
                    else:
                        print("login:", args.login)
                        password = getpass.getpass(prompt='password: ')
                        server.login(args.login, password)
                    authentication = True
                    print("========================================")
                    print("logged in with success!")
                    print("========================================")
                except Exception as e:
                    args.passwd = None
                    logger.info('failure when trying to connect to SMTP server with ' + args.login)
                    print("============================================================")
                    print("SMTPAuthenticationError: username and password not accepted.")
                    print("============================================================")
        logger.info('logged successfully with ' + args.login)
        #=======================================
        # create dictionary to assign a step level for each entry in 'increasing step'
        #=======================================
        '''
         create two dictionaries, "step_level" and "step":
          -------------------------------------------------------------------------
          * step_level:
              - keys: [int] indexes that contain the 'increasing step' condition
              - values: [int] represent the current step in the stair, where 0 is
                        the lowest level, and len(step[i]) is highest level
             e.g.:
                value = '1.5:2.0:2.5:3.0'
                step  = [1.5,2.0,2.5,3.0]
                len(step) = 4

                3.0 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _  ___Level_4___
                2.5 _ _ _ _ _ _ _ _ _ _ _ _ _ _ __L3__|
                2.0 _ _ _ _ _ _ _ _ _ _  __L2__|
                1.5 _ _ _ _ _ _ _ __L1__|
                                 |
                                 |
                  0 ___Level_0___|

               -Level 0: lowest level, 0 ~ 1.5 u (normal operation)
                  ...
               -Level 4: highest level, 3.0+

           obs.: emails are only sent when moving from any level to a higher one
          -------------------------------------------------------------------------
          * step:
              - keys: [int] indexes that contain the 'increasing step' condition
              - values: [array of float] represent the steps that triggers mailing
        '''
        step_level = {}
        step = {}
        for i in range(len(condition)):
            if(condition[i] == 'increasing step'):
                # create dictionary for step level
                step_level.update({i : 0})
                # split steps in str format
                step_array_str = value[i].split(':')
                # convert from string to float
                step_array = []
                for j in range(len(step_array_str)):
                    step_array.append(float(step_array_str[j]))
                # create dictionary for step arrays
                step.update({i : step_array})
        #=======================================
        # function that checks PV value
        #=======================================
        def check_pv(PV):
            value = caget(PV)
            if(value == None):
                logger.warning('cannot connect to PV ' + str(PV))
            return value
        #=======================================
        # function that writes in log
        #=======================================
        def log_info(pv_name, condition, specified_value, pv_value, mailing_list):
            # break mailing_list in multiple lines if more than one e-mail address
            # for each entry, one line feed ('\n') and two tab  ('\t') are added
            # e.g.:
            # input: mailing_list = 'rafael.ito@lnls.br;ito.rafael@gmail.com'
            # output: email = '\n\t\trafael.ito@lnls.br\n\t\tito.rafael@gmail.com'
            list = mailing_list.split(';')
            if(len(list) != 1):
                email = ""
                for i in list:
                    email = email + "\n\t\t" + i
            # if mailing_list has only one entry, keep the text in the same line
            else: email = mailing_list
            logger.info('e-mail sent!\n' + \
                        '\tPV = ' + pv_name + '\n' + \
                        '\tcondition = ' + condition + '\n' + \
                        '\tspecified value = ' + specified_value + '\n' + \
                        '\tvalue measured = ' + pv_value + '\n' + \
                        '\tmailing list: ' + email
            )
        #=======================================
        # main loop
        #=======================================
        while(True):
            # if service is disabled, log and wait until it is enabled
            if (caget("CON:MailServer:Enable") == 0):
                logger.warning('SMS is disabled (PV "CON:MailServer:Enable" is zero)')
                while(caget("CON:MailServer:Enable") == 0):
                    time.sleep(1)
            # only check PVs if service is enable
            else:
                #---------------------------------------
                '''
                # the next section was used when a single TIMEOUT was used for all PVs monitored
                # after an email has been sent, wait TIMEOUT to start checking PVs again
                while((time.time() - LAST_EVENT_TIME) < TIMEOUT):
                    sys.stdout.write("\033[K")
                    print("waiting timeout:", str(TIMEOUT - (round(time.time() - LAST_EVENT_TIME))), "s", end='\r')
                    time.sleep(1)
                '''
                #---------------------------------------
                for i in range(len(pv)):
                    # check when last event happened (if happened) and compare with the correspondet PV timeout
                    # also check if monitoring service is disabled for that PV
                    if(((time.time() - last_event_time[i]) > timeout[i]) and (caget(enable[i]) == 1)):
                        pv_value = check_pv(pv[i])
                        if (pv_value != None):
                            # check if PV value is in specified range
                            if(condition[i] == 'out of range'):
                                min = int(value[i].split(':')[0])
                                max = int(value[i].split(':')[1])
                                if( (pv_value < min) or (pv_value > max) ):
                                    pv_str = caget(pv[i], as_string=True)
                                    specified_value = "from " + str(min) + " " + unit[i] + " to " + str(max) + " " + unit[i]
                                    msg = compose_msg(pv[i], pv_str, specified_value, unit[i], warning[i], subject[i], email[i])
                                    send_email(args.login, password, email[i], msg)
                                    log_info(pv[i], condition[i], value[i], pv_str, email[i])
                                    last_event_time[i] = time.time()
                            # check if PV value exceeded its specified value
                            elif(condition[i] == 'superior than'):
                                if(pv_value > float(value[i])):
                                    pv_str = caget(pv[i], as_string=True)
                                    specified_value = "lower than " + str(value[i]) + " " + unit[i]
                                    msg = compose_msg(pv[i], pv_str, specified_value, unit[i], warning[i], subject[i], email[i])
                                    send_email(args.login, password, email[i], msg)
                                    log_info(pv[i], condition[i], value[i], pv_str, email[i])
                                    last_event_time[i] = time.time()
                            # check if PV value is lower than its specified value
                            elif(condition[i] == 'inferior than'):
                                if(pv_value < float(value[i])):
                                    pv_str = caget(pv[i], as_string=True)
                                    specified_value = "higher than " + str(value[i]) + " " + unit[i]
                                    msg = compose_msg(pv[i], pv_str, specified_value, unit[i], warning[i], subject[i], email[i])
                                    send_email(args.login, password, email[i], msg)
                                    log_info(pv[i], condition[i], value[i], pv_str, email[i])
                                    last_event_time[i] = time.time()
                            elif(condition[i] == 'increasing step'):
                                # get the maximum and minimum level possible
                                max_level = len(step.get(i))
                                min_level = 0
                                # get the current level
                                level = step_level.get(i)
                                # get the next limiar step to compare with
                                if(level != max_level):
                                    compare_next = step.get(i)[level]
                                compare_previous = step.get(i)[level-1]
                                #---------------------------------------
                                # print used to debbug only
                                #print("PV = " + pv[i])
                                #print("PV value = " + str(pv_value))
                                #print("level = " + str(level))
                                #print("compare_next = " + str(compare_next))
                                #print("compare_previous = " + str(compare_previous) + "\n")
                                #---------------------------------------
                                # if it's already in the maximum level, don't compare with next limiar
                                if( (level != max_level) and (pv_value > compare_next) ):
                                    # PV is bigger than next step limiar
                                    pv_str = str(pv_value)
                                    specified_value = "lower than " + str(step.get(i)[0]) + " " + unit[i]
                                    msg = compose_msg(pv[i], pv_str, specified_value, unit[i], warning[i], subject[i], email[i])
                                    send_email(args.login, password, email[i], msg)
                                    log_info(pv[i], condition[i], value[i], pv_str, email[i])
                                    #print("EMAIL SENT\n")  # used in debug --> print instead sending e-mail
                                    last_event_time[i] = time.time()
                                    # check if new value is only one level higher or more
                                    # start assuming the PV value is one step higher than the previous one
                                    hop = 1
                                    # check
                                    if((level+hop) != max_level):
                                        # for each step higher the value is, increment "hop"
                                        while(pv_value > step.get(i)[level+hop]):
                                            hop += 1
                                            # if it reached the maximum step level, exit the loop to avoid "IndexError"
                                            if((level+hop) == max_level):
                                                break
                                    # finally, update the level according to the new value
                                    step_level.update({i : (level+hop)})
                                # if it's already in the minimum level, dont't compare with previous limiar
                                if( (level != min_level) and (pv_value < compare_previous) ):
                                    # PV is smaller than previous step limiar
                                    # start assuming the PV value is one step lower than the previous one
                                    hop = 1
                                    # for each step higher the value is, increment "hop"
                                    while(pv_value < step.get(i)[level-hop-1]):
                                        if((level-hop) == min_level):
                                            break
                                        # if it reached the minimum step level, exit the loop to avoid "IndexError"
                                        hop += 1
                                    # finally, update the level according to the new value
                                    step_level.update({i : (level-hop)})
                                time.sleep(1)
                            elif(condition[i] == 'decreasing step'):
                                # to be implemented
                                pass
                #---------------------------------------
                time.sleep(1)
                # clean to the end of line
                sys.stdout.write("\033[K")
                print("standby", end='\r')

    # log if an exception is raised:
    except Exception as e:
        logger.error(str(e))
        traceback.print_exc()
        logger.error(traceback.format_exc())
#==============================================================================
t1 = threading.Thread(target=thread_1, args=[])
t2 = threading.Thread(target=thread_2, args=[])
t1.start()
t2.start()
