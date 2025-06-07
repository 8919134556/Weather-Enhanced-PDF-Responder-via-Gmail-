import os
import email
import traceback
from dotenv import load_dotenv
import re
from modules.nlp_utils import extract_city_from_text, ocr_extract_city

from modules.gmail_client import GmailClient
from modules.excel_utils import load_allowed_senders, is_sender_authorized
from modules.weather_client import fetch_current_weather
from modules.pdf_utils import append_weather_to_pdf
from modules.email_reply import send_reply_with_attachments
from modules.nlp_utils import extract_city_from_text, ocr_extract_city
from modules.logger import log_event

load_dotenv()

DOWNLOAD_FOLDER = 'temp_pdfs'
IMG_FOLDER      = 'temp_pdfs/images'
PROCESSED_FOLDER = 'temp_pdfs/processed'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(IMG_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def process_incoming_emails():
    gmail = GmailClient()
    allowed = load_allowed_senders()
    try:
        uids = gmail.search_unread_by_subject('Local-weather-update')
        for uid in uids:
            try:
                msg = gmail.fetch_email_message(uid)
                sender = email.utils.parseaddr(msg['From'])[1]
                if not is_sender_authorized(sender, allowed):
                    gmail.mark_as_seen(uid)
                    log_event(uid, sender, '', [], 'Skipped: unauthorized')
                    continue

                # Extract city from body / OCR
                # body = ''
                # for part in msg.walk():
                #     if part.get_content_type()=='text/plain':
                #         body = part.get_payload(decode=True).decode(part.get_content_charset('utf-8'))
                #         break
                # city = extract_city_from_text(body)
                # if city == os.getenv('DEFAULT_CITY'):
                #     imgs = gmail.download_image_attachments(msg, IMG_FOLDER)
                #     for img in imgs:
                #         city = ocr_extract_city(img)
                #         if city != os.getenv('DEFAULT_CITY'):
                #             break
                body = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)\
                                .decode(part.get_content_charset("utf-8"), "ignore")
                        break

                # 1) Try spaCy NER first:
                city = extract_city_from_text(body, default_city=os.getenv("DEFAULT_CITY"))

                # 2) If spaCy gives you the default (i.e. found nothing), try a simple regex as a backup:
                if city == os.getenv("DEFAULT_CITY"):
                    m = re.search(r'City\s*[:\-]?\s*([A-Za-z ]+)', body, re.IGNORECASE)
                    if m:
                        city = m.group(1).strip()

                # 3) Finally, if you still have the default, try OCR on any image attachments:
                if city == os.getenv("DEFAULT_CITY"):
                    image_paths = gmail.download_image_attachments(msg, IMG_FOLDER)
                    for img in image_paths:
                        ocr_city = ocr_extract_city(img, default_city=city)
                        if ocr_city != city:
                            city = ocr_city
                            break

                weather_info = fetch_current_weather(city)

                # PDFs
                pdfs = gmail.download_pdf_attachments(msg, DOWNLOAD_FOLDER)
                updated = []
                status = 'Success'
                for pdf in pdfs:
                    try:
                        out = os.path.join(PROCESSED_FOLDER, 'updated_'+os.path.basename(pdf))
                        updated.append(append_weather_to_pdf(pdf, weather_info, output_pdf_path=out))
                    except Exception:
                        status = 'Error: PDF processing'

                if updated:
                    send_reply_with_attachments(msg, updated)
                    gmail.mark_as_processed(uid)
                else:
                    gmail.mark_as_seen(uid)

                log_event(uid, sender, city, updated, status)

            except Exception:
                traceback.print_exc()
                gmail.mark_as_seen(uid)
                log_event(uid, sender, '', [], 'Error: exception')
    finally:
        gmail.logout()

if __name__=='__main__':
    process_incoming_emails()