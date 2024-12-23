import os
from celery import Celery
import models

app = Celery("tasks", broker=f"pyamqp://guest@{os.environ.get('RABBITMQ_HOST', 'localhost')}//")


@app.task
def send_contract_notification(item_id):
    # from email.message import EmailMessage
    # import smtplib
    # from database import init_db
    #
    # msg = EmailMessage()
    # msg.set_content("My email")
    #
    # init_db()
    # item = models.Item.query.get(item_id)
    #
    # msg['Subject'] = f"New contract request for your item {item.name}"
    # msg['From'] = "app_email@example.com"
    # msg['To'] = "owner_email@example.com"
    #
    # s = smtplib.SMTP_SSL("localhost")
    # s.send_message(msg)

    return f"Task completed for item with ID: {item_id}"
