#!/usr/bin/env python3
import smtplib
import typing
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import mailpy.entities as entities
import mailpy.logging as logging

from .message import compose_msg_content

logger = logging.getLogger()


class SMSException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class MailClient:
    DEFAULT_TLS_PORT = 587
    DEFAULT_SSL_PORT = 465

    def __init__(
        self,
        login: str,
        passwd: str,
        debug_level: int = 1,
        tls: bool = False,
        port: typing.Optional[int] = None,
        host: typing.Optional[str] = None,
    ):
        self._login = login
        self._passwd = passwd
        self._tls = tls
        self._host = "smtp.gmail.com" if host is None else host

        if port is None:
            self._port = self.DEFAULT_TLS_PORT if tls else self.DEFAULT_SSL_PORT
        else:
            self._port = port

        self._server: typing.Optional[smtplib.SMTP] = None
        self._debug_level = debug_level

        if self._tls and self._host == "smtp.gmail.com":
            raise ValueError(
                f"tls is not supported for host '{self._host}' '{self._port}'"
            )

    def __enter__(self):
        self._authenticate()
        return self

    def __exit__(self, *args, **kwargs):
        self._disconnect()

    def _create_server_tls(self):
        self._port = self.DEFAULT_TLS_PORT
        self._server = smtplib.SMTP(self._host, timeout=10)
        response = self._server.connect(host=self._host, port=self._port)
        self._server.ehlo()
        self._server.starttls()
        self._server.ehlo()
        return response

    def _create_server_ssl(self):
        self._port = self.DEFAULT_SSL_PORT
        self._server = smtplib.SMTP_SSL(self._host)
        return self._server.connect(host=self._host, port=self._port)

    def _create_server(self):
        if self._tls:
            (code, msg) = self._create_server_tls()
        else:
            (code, msg) = self._create_server_ssl()

        self._server.set_debuglevel(self._debug_level)
        logger.info(f"SMTP server connected with code {code} {msg}")

    def _disconnect(self):
        if not self._server:
            return

        self._server.quit()
        self._server.close()
        self._server = None

    def _authenticate(self):
        self._create_server()
        logger.info(f"Trying to authenticate at Gmail with {self._login}")

        self._server.login(self._login, self._passwd)
        logger.info(f"logged successfully with {self._login}")

    def _compose_msg(self, event: entities.AlarmEvent) -> MIMEMultipart:
        """
        :return: body of the e-mail that will be sent
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = self._login
        msg["To"] = ", ".join(event.emails)
        msg["Cc"] = ""
        msg["Bcc"] = ""
        msg["Subject"] = event.subject

        content = compose_msg_content(event)

        text_part = MIMEText(content.text, "plain")
        html_part = MIMEText(content.html, "html")
        # The email client will try to render the last part first (in this case the html)
        msg.attach(text_part)
        msg.attach(html_part)
        return msg

    def send_email(self, event: entities.AlarmEvent):
        if not self._server:
            logger.error(
                f"Failed to send email event {event}, SMTP server '{self._server}'is not connected"
            )
            return

        self._server.sendmail(
            from_addr=self._login,
            to_addrs=event.emails,
            msg=self._compose_msg(event).as_string(),
        )
        logger.info(f"Email sent with success, event {event}")
