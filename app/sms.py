#!/usr/bin/env python3

import ssl
import getpass
import argparse
import time
import typing
import pandas as pd
import logging
from time import localtime, strftime

import epics
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from commons import Entry

class SMSApp:

    def __init__(self, tls:bool, login:str, passwd:str, table:str):
        self.entries: typing.Dict[str, Entry] = []
        self.tls:bool = tls
        self.login  :str= login
        self.passwd :str = passwd
        self.table :str= table
        self.tick: float = 1
        self.enable: bool = True

    def load_csv_table(self, table_name:str):
        """ read csv file, read its values and store them in variables """
        df = pd.read_csv(args.table)

        # parse other columns
        for index, row in df.iterrows():
            self.entries[row['PV']] = Entry(
                pv = row['PV'],
                emails = row['emails'],
                condition = row['condition'],
                value = row['specified value'],
                unit = row['measurement unit'],
                warning = row['warning message'],
                subject = row['email subject'],
                timeout = row['timeout'],
                enable = row['enable PV'],)


    #==============================================================================
    # Composing the email
    #==============================================================================
    def compose_msg(self, PV_name, PV_value, specified_value, unit, warning, subject, email) -> MIMEMultipart:
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
        msg = MIMEMultipart("alternative")
        msg['From']     = args.login
        msg['To']       = email.replace(';', ', ')
        msg['Cc']       = ""
        msg['Bcc']      = ""
        msg['Subject']  = subject

        #==============================================================================
        # Defining message to be sent
        #==============================================================================
        # formating timestamp
        timestamp = strftime("%a, %d %b %Y %H:%M:%S", localtime())

        # creating the plain-text format of the message
        text = f"""{warning}\n
     - PV name:         {PV_name}
     - Specified range: {specified_value}
     - Value measured:  {PV_value} {unit}
     - Timestamp:       {timestamp}

     Archiver link: https://10.0.38.42

     Controls Group\n"""

        html = f"""\
        <html>
            <body>
                <p> {warning} <br>
                    <ul>
                        <li><b>PV name:         </b> {PV_name} <br></li>
                        <li><b>Specified range: </b> {specified_value}<br></li>
                        <li><b>Value measured:  </b> {PV_value} {unit}<br></li>
                        <li><b>Timestamp:       </b> {timestamp}<br></li>
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
    def send_email(self, login, password, email, msg):
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

    def log_info(self, pv_name, condition, specified_value, pv_value, mailing_list):
        # break mailing_list in multiple lines if more than one e-mail address
        # for each entry, one line feed ('\n') and two tab  ('\t') are added
        # e.g.:
        # input: mailing_list = 'rafael.ito@lnls.br;ito.rafael@gmail.com'
        # output: email = '\n\t\trafael.ito@lnls.br\n\t\tito.rafael@gmail.com'
        list = mailing_list.split(';')
        if (len(list) != 1):
            email = ""
            for i in list:
                email = email + "\n\t\t" + i
        # if mailing_list has only one entry, keep the text in the same line
        else:
            email = mailing_list
        logger.info('e-mail sent!\n' + \
                    '\tPV = ' + pv_name + '\n' + \
                    '\tcondition = ' + condition + '\n' + \
                    '\tspecified value = ' + specified_value + '\n' + \
                    '\tvalue measured = ' + pv_value + '\n' + \
                    '\tmailing list: ' + email
                    )

    #==============================================================================
    # main loop: check if PVs and email targets if not in specified range
    #==============================================================================
    def start(self):
        try:
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
            # main loop
            #=======================================
            while(True):
                time.sleep(self.tick)
                # if service is disabled, log and wait until it is enabled
                if not self.enable:#(caget("CON:MailServer:Enable") == 0):
                    logger.warning('SMS is disabled (PV "CON:MailServer:Enable" is zero)')
                    #while(caget("CON:MailServer:Enable") == 0):
                    continue

                #---------------------------------------
                for i in range(len(pv)):
                    # check when last event happened (if happened) and compare with the correspondet PV timeout
                    # also check if monitoring service is disabled for that PV
                    if(((time.time() - last_event_time[i]) > timeout[i]) and (caget(enable[i]) == 1)):
                        # check PV value
                        pv_value = caget(pv[i])
                        if(pv_value == None):
                            logger.warning('cannot connect to PV ' + str(pv[i]))
                        else:
                            # check if PV value is in specified range
                            if(condition[i] == 'out of range'):
                                min = float(value[i].split(':')[0])
                                max = float(value[i].split(':')[1])
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

        # log if an exception is raised:
        except Exception as e:
            logger.exception("Something wrong happened. Ops ¯\_(ツ)_/¯")

if __name__ == '__main__':
    LOGGING_FORMAT = '%(name)s [%(levelname)s]: %(message)s'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(LOGGING_FORMAT)
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

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

    app = SMSApp(tls=args.tls, login=args.login, passwd=args.passwd, table=args.table)
    app.start()
