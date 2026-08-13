"""
Tests for PII detector modules in src/pii_detector.py.
"""

import pytest
from src.pii_detector import (
    PIIDetector,
    EmailDetector,
    URLDetector,
    PhoneDetector,
    SSNDetector,
    CreditCardDetector,
    IPDetector,
    DOBDetector,
    NameDetector,
    CompanyDetector,
    AddressDetector,
)


def test_email_detector():
    detector = EmailDetector()
    text = "Contact us at support@example.com or user.name@domain.co.in."
    entities = detector.detect(text)
    assert len(entities) == 2
    assert entities[0].text == "support@example.com"
    assert entities[1].text == "user.name@domain.co.in"


def test_url_detector():
    detector = URLDetector()
    text = "Visit www.kshinternational.com or https://www.example.org for details."
    entities = detector.detect(text)
    assert len(entities) == 2
    assert entities[0].text == "www.kshinternational.com"
    assert entities[1].text == "https://www.example.org"


def test_phone_detector():
    detector = PhoneDetector()
    text = "Call mobile +91 9876543210 or +1 555 123 4567 today."
    entities = detector.detect(text)
    assert len(entities) >= 2
    phone_texts = [e.text for e in entities]
    assert "+91 9876543210" in phone_texts or "9876543210" in phone_texts


def test_ssn_detector_us_and_indian():
    detector = SSNDetector()
    text = "US SSN 123-45-6789, PAN ABCDE1234F, Aadhaar 9876 5432 1098, CIN U28129PN1979PLC141032."
    entities = detector.detect(text)
    assert len(entities) == 4
    texts = [e.text for e in entities]
    assert "123-45-6789" in texts
    assert "ABCDE1234F" in texts
    assert "9876 5432 1098" in texts
    assert "U28129PN1979PLC141032" in texts


def test_credit_card_detector():
    detector = CreditCardDetector()
    text = "Payment card 4111 1111 1111 1111 was charged."
    entities = detector.detect(text)
    assert len(entities) == 1
    assert entities[0].text == "4111 1111 1111 1111"


def test_ip_detector():
    detector = IPDetector()
    text = "Connecting to 192.168.1.10 and 10.0.0.1."
    entities = detector.detect(text)
    assert len(entities) == 2
    assert entities[0].text == "192.168.1.10"
    assert entities[1].text == "10.0.0.1"


def test_dob_detector():
    detector = DOBDetector()
    text = "Date of Birth: 12/04/1998 for the applicant."
    entities = detector.detect(text)
    assert len(entities) == 1
    assert entities[0].text == "12/04/1998"


def test_name_detector():
    detector = NameDetector()
    text = "Please contact Ms. Rashi Patil or Mr. Rohan Dey."
    entities = detector.detect(text)
    assert len(entities) >= 2
    names = [e.text for e in entities]
    assert any("Rashi Patil" in n for n in names)
    assert any("Rohan Dey" in n for n in names)


def test_company_detector():
    detector = CompanyDetector()
    text = "Signed by Example Technologies Pvt Ltd and Apex Solutions Inc."
    entities = detector.detect(text)
    assert len(entities) >= 2
    orgs = [e.text for e in entities]
    assert any("Example Technologies" in o for o in orgs)


def test_address_detector():
    detector = AddressDetector()
    text = "Mailing Address: 123 Example Road, Sector 17, Chandigarh 160017."
    entities = detector.detect(text)
    assert len(entities) >= 1
    assert any("123 Example Road" in e.text for e in entities)


def test_overlap_resolution():
    detector = PIIDetector()
    text = "Email rashi.patil@gmail.com is primary."
    entities = detector.detect(text)
    assert len(entities) == 1
    assert entities[0].entity_type == "EMAIL"


def test_non_pii_header_traps():
    detector = PIIDetector()
    text = "DETAILS OF THE OFFER TO PUBLIC: SIZE OF THE FRESH ISSUE"
    entities = detector.detect(text)
    assert len(entities) == 0
