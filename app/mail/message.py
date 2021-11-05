import typing

import app.entities as entities


class MessageContent(typing.NamedTuple):
    text: str
    html: str


def _compose_text(event: entities.AlarmEvent):
    return f"""{event.warning}\n
     - PV name:         {event.pvname}
     - Specified range: {event.specified_value_message}
     - Value measured:  {event.value_measured} {event.unit}
     - Timestamp:       {event.ts.local_str}

     Archiver link:
        https://10.0.38.42/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}
        https://10.0.38.46/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}
        https://10.0.38.59/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}

     Controls Group\n"""


def _compose_html(event: entities.AlarmEvent):
    return f"""\
        <html>
            <body>
                <p> {event.warning} <br>
                    <ul>
                        <li><b>PV name:         </b> {event.pvname} <br></li>
                        <li><b>Specified range: </b> {event.specified_value_message}<br></li>
                        <li><b>Value measured:  </b> {event.value_measured} {event.unit}<br></li>
                        <li><b>Timestamp:       </b> {event.ts.local_str}<br></li>
                    </ul>
                    Archiver link:
                       <a href="https://10.0.38.42/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}">
                        https://10.0.38.42/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}
                       </a><br><br>

                       <a href="https://10.0.38.46/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}">
                        https://10.0.38.46/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}
                       </a><br><br>

                       <a href="https://10.0.38.59/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}">
                        https://10.0.38.59/archiver-vewer/?pv={event.pvname}&to={event.ts.utc_str}
                       </a><br><br>

                    GAS - Automação e Software
                </p>
            </body>
        </html>"""


def compose_msg_content(event: entities.AlarmEvent) -> MessageContent:
    """
    @return (text, html)
    """

    # creating the plain-text format of the message
    text = _compose_text(event)

    html = _compose_html(event)
    return MessageContent(text, html)
