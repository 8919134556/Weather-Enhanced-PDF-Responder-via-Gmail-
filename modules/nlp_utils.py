import spacy
from spacy.cli import download as spacy_download
from PIL import Image
import pytesseract

# Load spaCy model once at import time, downloading if necessary
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Attempt to download the model and load again
    spacy_download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def extract_city_from_text(body_text, default_city="New Delhi"):
    """
    Runs spaCy NER over the email body text, returning the first detected GPE (city),
    or default_city if none found.
    """
    if not body_text:
        return default_city
    doc = nlp(body_text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            return ent.text
    return default_city


def ocr_extract_city(image_path, default_city="New Delhi"):
    """
    Runs Tesseract OCR on the image at image_path, then uses spaCy NER to extract a city.
    Falls back to default_city if none found.
    """
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return extract_city_from_text(text, default_city)
    except Exception:
        return default_city
