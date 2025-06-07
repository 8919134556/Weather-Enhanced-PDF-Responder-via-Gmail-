import imaplib
import email
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

class GmailClient:
    def __init__(self):
        self.conn = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        self.conn.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)

    def search_unread_by_subject(self, subject_keyword="Local-weather-update"):
        self.conn.select("INBOX")
        status, data = self.conn.search(None, f'(UNSEEN SUBJECT "{subject_keyword}")')
        return data[0].split() if status == "OK" else []

    def fetch_email_message(self, uid):
        status, data = self.conn.fetch(uid, "(RFC822)")
        if status != "OK": return None
        return email.message_from_bytes(data[0][1])

    def download_pdf_attachments(self, msg, download_folder="temp_pdfs"):
        if not os.path.isdir(download_folder): os.makedirs(download_folder, exist_ok=True)
        saved = []
        for part in msg.walk():
            disp = part.get("Content-Disposition", "")
            if part.get_content_maintype() == "application" and "attachment" in disp:
                fn = part.get_filename()
                if fn and fn.lower().endswith('.pdf'):
                    path = os.path.join(download_folder, fn)
                    with open(path, 'wb') as f: f.write(part.get_payload(decode=True))
                    saved.append(path)
        return saved

    def download_image_attachments(self, msg, download_folder="temp_pdfs/images"):
        if not os.path.isdir(download_folder): os.makedirs(download_folder, exist_ok=True)
        saved = []
        for part in msg.walk():
            disp = part.get("Content-Disposition", "")
            ctype = part.get_content_maintype()
            if ctype == "image" and "attachment" in disp:
                fn = part.get_filename()
                path = os.path.join(download_folder, fn)
                with open(path, 'wb') as f: f.write(part.get_payload(decode=True))
                saved.append(path)
        return saved

    def mark_as_seen(self, uid):
        self.conn.store(uid, '+FLAGS', '\\Seen')

    def mark_as_processed(self, uid, label="Processed"):
        # Add custom label and remove from INBOX
        self.conn.store(uid, '+X-GM-LABELS', label)
        self.conn.store(uid, '-X-GM-LABELS', '\\Inbox')

    def logout(self):
        self.conn.logout()