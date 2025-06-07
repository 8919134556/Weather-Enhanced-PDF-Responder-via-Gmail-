import smtplib
import os
import email.utils
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_reply_with_attachments(original_msg, updated_pdf_paths, reply_body=None):
    """
    Composes and sends an email via SMTP, replying to original_msg.
    - original_msg: an email.message.Message object.
    - updated_pdf_paths: list of file paths to attach.
    - reply_body: optional plain-text body. If None, a default message is used.
    """
    from_addr = GMAIL_EMAIL
    to_addr = email.utils.parseaddr(original_msg.get("From"))[1]

    orig_subject = original_msg.get("Subject", "")
    reply_subject = "Re: " + orig_subject

    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = reply_subject

    if original_msg.get("Message-ID"):
        msg["In-Reply-To"] = original_msg.get("Message-ID")
        if original_msg.get("References"):
            msg["References"] = original_msg.get("References") + " " + original_msg.get("Message-ID")
        else:
            msg["References"] = original_msg.get("Message-ID")

    if reply_body is None:
        reply_body = (
            "Hello,\n\n"
            "Please find attached the PDF(s) updated with the current weather information.\n\n"
            "Best regards,\n"
            "Automated Weather-Enhanced PDF Responder"
        )
    msg.set_content(reply_body)

    for path in updated_pdf_paths:
        with open(path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(path)
            msg.add_attachment(
                file_data,
                maintype="application",
                subtype="pdf",
                filename=file_name
            )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)
