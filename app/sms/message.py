import typing
import time

import app.entities as entities


def compose_msg_content(event: entities.EmailEvent) -> typing.Tuple[str, str]:
    """
    @return (text, html)
    """
    timestamp = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

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

    return text, html
