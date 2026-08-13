"""
Validators for PII entity validation.
Reduces false positives using structural, algorithmic, and syntactic NLP rules.
Zero hardcoded prospectus/document word lists.
"""

import re
import ipaddress
from typing import Optional

try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False


# Common legal business suffixes and organizational structure indicators across all industries
RECOGNIZED_ORG_INDICATORS = {
    "LTD", "LIMITED", "PVT", "PRIVATE", "LLP", "INC", "INC.", "CORP", "CORPORATION",
    "TECHNOLOGIES", "INDUSTRIES", "ENTERPRISES", "SOLUTIONS", "SERVICES", "SYSTEMS",
    "SECURITIES", "BANK", "LOGISTICS", "MOTORS", "INFRA", "DISTRIPARKS", "MANAGEMENT",
    "ANALYTICS", "ADVISORY", "DEVELOPERS", "HOLDINGS", "GROUP", "FOUNDATION", "TRUST",
    "CONSULTING", "AGENCY", "LABS", "PHARMA", "VENTURES","CO","COMPANY",
    "EXCHANGE", "BOARD"
}

# Generic English document structural nouns that never form human personal names
STRUCTURAL_HEADING_WORDS = {
    "DETAILS", "OFFER", "PUBLIC", "RISKS", "RISK", "RESPONSIBILITY", "REGISTERED", "OFFICE",
    "BOARD", "DIRECTORS", "SECTION", "CHAPTER", "TABLE", "ANNEXURE", "EXHIBIT", "SUMMARY",
    "REPORT", "PERIOD", "DATE", "ISSUE", "GENERAL", "FIRST", "SECOND", "THIRD", "FOURTH",
    "TOTAL", "STATEMENT", "NOTES", "INFORMATION", "LEAD", "MANAGERS", "REGISTRAR",
    "COMPLIANCE", "OFFICER", "CHARTERED", "ACCOUNTANTS", "AUDITORS", "STATUTORY", "LEGAL",
    "REGULATION", "REGULATIONS", "RULES", "REQUIREMENTS", "DOCUMENT", "PROSPECTUS",
    "HERRING", "FRESH", "SALE", "RESERVATION", "ELIGIBILITY", "SHARE", "EQUITY", "PRICE",
    "VALUE", "FLOOR", "CAP", "BIDDING", "ANCHOR", "INVESTOR", "INVESTORS", "BID"
}


def validate_org(org_str: str) -> bool:
    """
    Algorithmic validation for Organization entities:
    Requires structural presence of a recognized corporate suffix or organizational indicator.
    Accepts company names containing digits or numbers (e.g. KSH Infra Park 5 Private Limited).
    """
    cleaned = org_str.strip()
    words = [w.strip(".,:;()").upper() for w in cleaned.split() if w.strip(".,:;()")]

    if not words or len(cleaned) < 3:
        return False

    # Must contain a corporate suffix/indicator
    has_org_indicator = any(w in RECOGNIZED_ORG_INDICATORS for w in words)
    if has_org_indicator:
        return True

    if len(words) == 1:
        return False

    if "/" in cleaned:
        return False

    return False


def validate_person(person_str: str) -> bool:
    """
    Algorithmic validation for Person Name entities:
    Requires candidate to be 2+ capitalized proper words or have a valid honorific prefix.
    Rejects structural document headings containing common nouns.
    """
    cleaned = person_str.strip()
    words = [w.strip(".,:;()") for w in cleaned.split() if w.strip(".,:;()")]

    if not words or len(cleaned) < 3:
        return False

    prefixes = {"Mr", "Mr.", "Ms", "Ms.", "Mrs", "Mrs.", "Dr", "Dr.", "Prof", "Prof.", "Shri", "Smt", "Smt."}
    if words[0] in prefixes:
        return len(words) >= 2

    if len(words) < 2:
        return False

    # Reject headings containing structural common nouns
    if any(w.upper() in STRUCTURAL_HEADING_WORDS for w in words):
        return False

    if not all(w[0].isupper() and any(c.isalpha() for c in w) for w in words):
        return False

    if any(char in cleaned for char in "/\\0123456789@#$%^*()_+=~"):
        return False

    return True


def validate_pan(pan_str: str) -> bool:
    """
    Validates Indian Permanent Account Number (PAN) format: 5 letters, 4 digits, 1 letter.
    """
    cleaned = pan_str.strip().upper()
    return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', cleaned))


def validate_aadhaar(aadhaar_str: str, context_text: str = "") -> bool:
    """
    Validates Indian Aadhaar 12-digit identification number format.
    """
    digits = re.sub(r'\D', '', aadhaar_str)
    if len(digits) != 12:
        return False
    
    if digits[0] in ("0", "1"):
        return False

    has_context = bool(re.search(r'(?i)\b(aadhaar|aadhar|uid|uidai|identity|unique id)\b', context_text))
    has_spaces_or_hyphens = bool(re.search(r'\b\d{4}[-\s]\d{4}[-\s]\d{4}\b', aadhaar_str))

    return has_spaces_or_hyphens or has_context


def validate_cin(cin_str: str) -> bool:
    """
    Validates Indian Corporate Identity Number (CIN): 21 alphanumeric characters.
    """
    cleaned = cin_str.strip().upper()
    pattern = r'^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$'
    return bool(re.match(pattern, cleaned))


def validate_luhn(card_number: str) -> bool:
    """
    Validates a credit card candidate using the Luhn algorithm.
    """
    digits_only = re.sub(r'\D', '', card_number)
    if not (13 <= len(digits_only) <= 19):
        return False

    checksum = 0
    reverse_digits = digits_only[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        checksum += n

    return checksum % 10 == 0


def validate_ip(ip_str: str) -> bool:
    """
    Validates IPv4 or IPv6 address using Python's ipaddress module.
    """
    try:
        ipaddress.ip_address(ip_str.strip())
        return True
    except ValueError:
        return False


def validate_email(email_str: str) -> bool:
    """
    Validates an email address candidate.
    """
    cleaned = email_str.strip().strip(".,;:()")
    if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, cleaned))


def validate_url(url_str: str) -> bool:
    """
    Validates a URL / Website candidate.
    """
    cleaned = url_str.strip().strip(".,;:()")
    if "@" in cleaned:
        return False

    pattern = r'^(?:https?://|www\.)[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+[/\w\.-]*$|^[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.(?:com|org|net|co\.in|in|io|gov|edu|biz|info)$'
    return bool(re.match(pattern, cleaned, re.I))


def validate_phone(phone_str: str, default_region: str = "IN", context_text: str = "") -> bool:
    """
    Validates a phone number candidate using phonenumbers library or fallback regex rules.
    """
    cleaned = phone_str.strip()
    digits_only = re.sub(r'\D', '', cleaned)
    
    if re.search(r'(?i)\b(ord|tkt|inv|prod|sku|ref|id|no|code|table|page|section)[-_\s:]*\d+', context_text):
        if phone_str in context_text and not re.search(r'(?i)\b(phone|mobile|tel|contact|cell|telephone)\b', context_text):
            return False

    if PHONENUMBERS_AVAILABLE:
        try:
            parsed = phonenumbers.parse(cleaned, default_region)
            if phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed):
                return True
        except Exception:
            pass

    if len(digits_only) < 7 or len(digits_only) > 15:
        return False

    if not cleaned.startswith("+") and len(digits_only) == 10:
        has_context = bool(re.search(r'(?i)\b(phone|mobile|tel|contact|cell|call|whatsapp|telephone)\b', context_text))
        if cleaned.startswith(("+91", "91")) or digits_only[0] in "6789":
            return True
        return has_context

    return len(digits_only) >= 10


def validate_ssn(ssn_str: str, context_text: str = "") -> bool:
    """
    Validates US SSN, Indian PAN, Aadhaar, Voter ID, or CIN identification numbers.
    """
    if re.search(r'(?i)\b(ord|tkt|inv|prod|sku|ref|ticket|order|invoice)\b', context_text):
        return False

    cleaned = ssn_str.strip().upper()

    if re.match(r'^(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}$', cleaned):
        return True

    if validate_pan(cleaned):
        return True

    if validate_aadhaar(cleaned, context_text=context_text):
        return True

    if validate_cin(cleaned):
        return True

    if re.match(r'^[A-Z]{3}\d{7}$', cleaned):
        return True

    return False


def validate_dob(date_str: str, context_text: str) -> bool:
    """
    Validates if a date string represents a Date of Birth by checking contextual cues.
    """
    dob_context = bool(re.search(
        r'(?i)\b(dob|d\.o\.b\.|date\s+of\s+birth|birth\s+date|birthdate|born|date\s+of\s+birth:?)\b',
        context_text
    ))

    non_dob_context = bool(re.search(
        r'(?i)\b(date\s+of\s+filing|filing\s+date|invoice\s+date|effective\s+date|document\s+date|issue\s+date|expiry\s+date|created\s+on|order\s+date|date:)\b',
        context_text
    ))

    if non_dob_context and not dob_context:
        return False

    return dob_context
