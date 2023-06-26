from operator import index
import os
from importlib_metadata import files
from loguru import logger
from pathlib import Path
from send_alert import send_alert





current_dir = os.getcwd()


def generate_email(received_contents):
    default = "-"
    expected_content = dict.fromkeys(["current_user", "datetime"], default)

    for content in expected_content:
        if content in received_contents:
            expected_content[content] = received_contents[content]
        else:
            logger.warning(f"The value for {content} was not passed to write failure email. Default value {default} will be used")
    send_alert_path = Path(current_dir+"/send_alert_email.html")

    print(send_alert_path)

    if send_alert_path.exists() and send_alert_path.is_file():
        with open(str(send_alert_path), "r") as message:
            html = message.read().format(**expected_content)
    else:
        logger.critical("SEND_ALERT_TEMPLATE_PATH does not exists so dumping expected content as string into email")
        html = f"ERROR: SEND_ALERT_TEMPLATE_PATH was not set or does not exist so dumping email content as string:<br/>{expected_content}"

    return html


            
def alert_information(current_user, datetime):
    email_contents = {
        "current_user": current_user,
        "datetime": datetime, 
        
}
    body = generate_email(email_contents)
    send_alert(body=body, subject="ALERT! MOTION DETECTED!", files=[]) 

    