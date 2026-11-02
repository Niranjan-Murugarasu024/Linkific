"""Format validators built on the shared regex pattern library."""
from patterns.regex_patterns import (
    EMAIL_PATTERN, INDIAN_PHONE_PATTERN, PINCODE_PATTERN, NAME_PATTERN,
    PASSWORD_PATTERN, TIME_PATTERN, GSTIN_PATTERN, UUID_PATTERN,
)

def _valid(pattern, value):
    return bool(pattern.fullmatch(str(value).strip()))

def validate_email(value): return _valid(EMAIL_PATTERN, value)
def validate_phone(value): return _valid(INDIAN_PHONE_PATTERN, value)
def validate_pincode(value): return _valid(PINCODE_PATTERN, value)
def validate_name(value): return _valid(NAME_PATTERN, value)
def validate_password(value): return _valid(PASSWORD_PATTERN, value)
def validate_time(value): return _valid(TIME_PATTERN, value)
def validate_gstin(value): return _valid(GSTIN_PATTERN, value)
def validate_uuid(value): return _valid(UUID_PATTERN, value)
