"""Reusable regular-expression pattern library.

Regex patterns validate syntax and extract candidates; they do not prove that
an email/phone/GSTIN is registered or reachable.
"""
import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
EMAIL_EXTRACT_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
INDIAN_PHONE_PATTERN = re.compile(r"^(?:\+91[- ]?)?[6-9]\d{9}$")
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
DATE_DMY_PATTERN = re.compile(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b")
DATE_ISO_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
IPV4_CANDIDATE_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PINCODE_PATTERN = re.compile(r"^[1-9]\d{5}$")
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z '\-]*$")
ALPHANUMERIC_PATTERN = re.compile(r"^[A-Za-z0-9]+$")
SPECIAL_CHAR_PATTERN = re.compile(r"[^A-Za-z0-9\s]")
WHITESPACE_PATTERN = re.compile(r"\s+")
NUMBER_PATTERN = re.compile(r"\d+")
CURRENCY_PATTERN = re.compile(r"(?:₹|Rs\.?|INR)\s?\d+(?:,\d{3})*(?:\.\d{1,2})?", re.I)
USERNAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,19}$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")
HASHTAG_PATTERN = re.compile(r"#[A-Za-z0-9_]+")
MENTION_PATTERN = re.compile(r"@[A-Za-z0-9_]+")
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
LOG_LEVEL_PATTERN = re.compile(r"\b(INFO|DEBUG|WARNING|ERROR|CRITICAL)\b")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
ORDER_ID_PATTERN = re.compile(r"\bORD-\d{5,10}\b")
TRANSACTION_ID_PATTERN = re.compile(r"\bTXN-[A-Z0-9]{6,12}\b")
HTML_ENTITY_PATTERN = re.compile(r"&(?:amp|lt|gt|quot|apos);")
TRIM_PATTERN = re.compile(r"^\s+|\s+$")
PHONE_DIGITS_PATTERN = re.compile(r"\d+")
LOG_LINE_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"(?P<level>INFO|DEBUG|WARNING|ERROR|CRITICAL) "
    r"(?P<ip>(?:\d{1,3}\.){3}\d{1,3}) (?P<message>.*)$"
)
