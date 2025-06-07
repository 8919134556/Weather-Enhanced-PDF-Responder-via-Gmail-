import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

ALLOWED_SENDERS_PATH = os.getenv("ALLOWED_SENDERS_PATH", "allowed_senders.xlsx")

def load_allowed_senders():
    """
    Reads the Excel file (allowed_senders.xlsx) and returns a set of email addresses.
    Assumes the column header is 'email' (case-insensitive).
    """
    if not os.path.exists(ALLOWED_SENDERS_PATH):
        raise FileNotFoundError(f"Whitelist Excel not found at {ALLOWED_SENDERS_PATH}")

    df = pd.read_excel(ALLOWED_SENDERS_PATH, dtype=str)
    df.columns = [c.lower() for c in df.columns]
    if "email" not in df.columns:
        raise KeyError("Excel file must have a column named 'email' (case-insensitive).")

    allowed = set(df["email"].str.strip().str.lower().tolist())
    return allowed

def is_sender_authorized(sender_email, allowed_senders_set):
    """
    Checks if sender_email (string) is in the allowed_senders_set.
    """
    return sender_email.strip().lower() in allowed_senders_set
