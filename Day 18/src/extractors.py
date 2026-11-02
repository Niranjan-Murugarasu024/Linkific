"""Extract common entities from unstructured text."""
from patterns.regex_patterns import (
    EMAIL_EXTRACT_PATTERN, URL_PATTERN, DATE_DMY_PATTERN, DATE_ISO_PATTERN,
    IPV4_CANDIDATE_PATTERN, NUMBER_PATTERN, HASHTAG_PATTERN, MENTION_PATTERN,
    ORDER_ID_PATTERN, TRANSACTION_ID_PATTERN,
)

def extract_emails(text): return EMAIL_EXTRACT_PATTERN.findall(text)
def extract_urls(text): return URL_PATTERN.findall(text)
def extract_dates(text):
    return DATE_DMY_PATTERN.findall(text) + DATE_ISO_PATTERN.findall(text)
def extract_ip_candidates(text): return IPV4_CANDIDATE_PATTERN.findall(text)
def extract_numbers(text): return NUMBER_PATTERN.findall(text)
def extract_hashtags(text): return HASHTAG_PATTERN.findall(text)
def extract_mentions(text): return MENTION_PATTERN.findall(text)
def extract_order_ids(text): return ORDER_ID_PATTERN.findall(text)
def extract_transaction_ids(text): return TRANSACTION_ID_PATTERN.findall(text)

def valid_ip_addresses(text):
    """Return only valid IPv4 addresses among regex-extracted candidates."""
    import ipaddress
    valid = []
    for candidate in extract_ip_candidates(text):
        try:
            ipaddress.IPv4Address(candidate)
            valid.append(candidate)
        except ipaddress.AddressValueError:
            pass
    return valid
