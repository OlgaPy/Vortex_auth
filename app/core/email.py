import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from pydantic import EmailStr

from app.core.settings import settings

EmailAddress = EmailStr | list[EmailStr]


def send_email_via_ses(
    sender: EmailStr,
    to: EmailAddress,
    subject: str,
    message: str,
    message_html: str | None = None,
    cc: EmailAddress | None = None,
    bcc: EmailAddress | None = None,
):
    """Send email using AWS SES."""
    if isinstance(to, str):
        to = [to]
    if cc and isinstance(cc, str):
        cc = [cc]
    if bcc and isinstance(bcc, str):
        bcc = [bcc]

    ses = boto3.client("ses")

    email_params = {
        "Source": sender,
        "Destination": {"ToAddresses": to},
        "Message": {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": message}},
        },
    }

    if cc:
        email_params["Destination"]["CcAddresses"] = cc

    if bcc:
        email_params["Destination"]["BccAddresses"] = bcc

    if message_html:
        email_params["Message"]["Body"] = {"Html": {"Data": message_html}}

    ses.send_email(**email_params)


def send_email(
    sender: EmailStr,
    to: EmailAddress,
    subject: str,
    message: str,
    message_html: str | None = None,
    cc: EmailAddress | None = None,
    bcc: EmailAddress | None = None,
):
    """Send email using smtp."""
    if isinstance(to, str):
        to = [to]
    if cc and isinstance(cc, str):
        cc = [cc]
    if bcc and isinstance(bcc, str):
        bcc = [bcc]
    email = MIMEMultipart("alternative")

    email["Subject"] = subject
    email["From"] = sender
    email["To"] = ",".join(to)

    if cc:
        email["Cc"] = ",".join(cc)
    if bcc:
        email["Bcc"] = ",".join(bcc)

    email.attach(MIMEText(message, "plain"))
    if message_html:
        email.attach(MIMEText(message_html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.sendmail(sender, to, email.as_string())
