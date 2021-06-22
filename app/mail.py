import logging
import ssl
from time import localtime, strftime

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import commons


logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, login: str, passwd: str, tls: bool):
        self._tls: bool = tls
        self._login: str = login
        self._passwd: str = passwd

    def authenticate_account(self) -> bool:
        """
        Authenticate gmail account
        :return bool: Successfully connected
        """
        logger.info(f"Trying to authenticate at Gmail with {self._login}")

        authentication = False

        try:
            context = ssl.create_default_context()
            while not authentication:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(self._login, self._passwd)
                    authentication = True
                    logger.info(f"logged successfully with {self._login}")
                    return True

        except ssl.SSLError:
            logger.exception("Error from the underlying SSL implementation")
        except smtplib.SMTPAuthenticationError:
            logger.exception(
                f"Failed to authenticate with username:{self._login} and password: {self._passwd}"
            )
        except smtplib.SMTPException:
            logger.exception("Error from the smtplib module")

        self._passwd = ""
        return False

    def compose_msg(self, event: commons.EmailEvent) -> MIMEMultipart:
        """
        :param commons.EmailEvent event: Message content
        :return: body of the e-mail that will be sent
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = self._login
        msg["To"] = event.emails.replace(";", ", ")
        msg["Cc"] = ""
        msg["Bcc"] = ""
        msg["Subject"] = event.subject

        timestamp = strftime("%a, %d %b %Y %H:%M:%S", localtime())

        # creating the plain-text format of the message
        text = f"""{event.warning}\n
     - PV name:         {event.pvname}
     - Specified range: {event.specified_value_message}
     - Value measured:  {event.value_measured} {event.unit}
     - Timestamp:       {timestamp}

     Archiver link: https://10.0.38.42

     Controls Group\n"""

        html = f"""\
        <html>
            <body>
                <p> {event.warning} <br>
                    <ul>
                        <li><b>PV name:         </b> {event.pvname} <br></li>
                        <li><b>Specified range: </b> {event.specified_value_message}<br></li>
                        <li><b>Value measured:  </b> {event.value_measured} {event.unit}<br></li>
                        <li><b>Timestamp:       </b> {timestamp}<br></li>
                    </ul>
                    Archiver link: <a href="https://10.0.38.42">https://10.0.38.42<a><br><br>
                    Controls Group
                </p>
            </body>
        </html>
        """

        text_part = MIMEText(text, "plain")
        html_part = MIMEText(html, "html")
        # add html/plain-text parts to MIMEMultipart message.
        # The email client will try to render the last part first (in this case the html)
        msg.attach(text_part)
        msg.attach(html_part)
        return msg

    def send_email(self, event: commons.EmailEvent, msg: MIMEMultipart):
        """
        Send an email
        :param commons.EmailEvent event: Email content specifics
        :param MIMEMultipart msg: Message content
        """
        email = event.emails.split(";")

        try:
            # Create a secure SSL context
            context = ssl.create_default_context()

            if self._tls:
                # Start an unsecured SMTP connection and then encrypt it.
                # Gmail SMTP server requires a connection with port 587 if using .starttls()
                PORT = 587
                # Create a secure SSL context
                # try to log in to server and send email
                with smtplib.SMTP("smtp.gmail.com", PORT) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(self._login, self._passwd)
                    server.sendmail(self._login, email, msg.as_string())

            else:
                # Start a secured SMTP connection from the beginning.
                # Gmail SMTP server requires a connection with port 465 if using SMTP_SSL()
                PORT = 465
                with smtplib.SMTP_SSL(
                    "smtp.gmail.com", PORT, context=context
                ) as server:
                    server.login(self._login, self._passwd)
                    server.sendmail(self._login, email, msg.as_string())

            logger.info(f"Email sent with success. {email}")
        except ssl.SSLError:
            logger.exception("Error from the underlying SSL implementation")
        except smtplib.SMTPAuthenticationError:
            logger.exception(
                f"Failed to authenticate with username:{self._login} and password: {self._passwd}"
            )
        except smtplib.SMTPException:
            logger.exception("Error from the smtplib module")
