import typing

import mailpy.entities as entities
import mailpy.info


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
        https://10.0.38.42/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}
        https://10.0.38.46/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}
        https://10.0.38.59/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}

    GAS - Automação e Software

    Software {mailpy.info.__source_url__} "{mailpy.info.__version__}" {mailpy.info.__date__}\n"""


def _compose_html(event: entities.AlarmEvent):
    return f"""\
        <html>
            <body>
                <p>
                    <h2>{event.warning}</h2>
                    <br>
                    <ul>
                        <li><b>PV name:         </b> {event.pvname} <br></li>
                        <li><b>Specified range: </b> {event.specified_value_message}<br></li>
                        <li><b>Value measured:  </b> {event.value_measured} {event.unit}<br></li>
                        <li><b>Timestamp:       </b> {event.ts.local_str}<br></li>
                    </ul>
                    <h4>Archiver links:</h4>
                    <ul>
                        <li>
                            <a href="https://10.0.38.42/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}">
                                https://10.0.38.42/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}
                            </a>
                        </li>
                        <li>
                            <a href="https://10.0.38.46/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}">
                                https://10.0.38.46/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}
                            </a>
                       </li>
                       <li>
                            <a href="https://10.0.38.59/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}">
                                https://10.0.38.59/archiver-viewer/?pv={event.pvname}&to={event.ts.utc_str}
                            </a>
                       </li>
                    </ul>
                    <h5>GAS - Automação e Software</h5>
                </p>
                <i>
                    <b>Software</b> {mailpy.info.__source_url__} "{mailpy.info.__version__}" {mailpy.info.__date__}
                </i>
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
