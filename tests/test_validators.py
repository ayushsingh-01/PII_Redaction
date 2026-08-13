"""
Tests for validator logic in src/validators.py.
"""

import pytest
from src.validators import (
    validate_luhn,
    validate_ip,
    validate_email,
    validate_url,
    validate_phone,
    validate_ssn,
    validate_pan,
    validate_aadhaar,
    validate_cin,
    validate_dob,
    validate_org,
    validate_person,
)


def test_validate_luhn():
    assert validate_luhn("4111 1111 1111 1111") is True
    assert validate_luhn("4111-1111-1111-1111") is True
    assert validate_luhn("4111111111111111") is True
    assert validate_luhn("4111 1111 1111 1112") is False
    assert validate_luhn("12345") is False


def test_validate_ip():
    assert validate_ip("192.168.1.1") is True
    assert validate_ip("10.0.0.255") is True
    assert validate_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
    assert validate_ip("999.999.999.999") is False
    assert validate_ip("abc.def.ghi.jkl") is False


def test_validate_email():
    assert validate_email("rashi.patil@gmail.com") is True
    assert validate_email("john.doe+tag@example.co.in") is True
    assert validate_email("invalid-email") is False
    assert validate_email("user@domain") is False


def test_validate_url():
    assert validate_url("www.kshinternational.com") is True
    assert validate_url("https://www.example.com") is True
    assert validate_url("http://sub.domain.co.in") is True
    assert validate_url("rashi.patil@gmail.com") is False


def test_validate_indian_ids():
    assert validate_pan("ABCDE1234F") is True
    assert validate_pan("AAAPK1234C") is True
    assert validate_pan("12345ABCDE") is False

    assert validate_aadhaar("9876 5432 1098") is True
    assert validate_aadhaar("9876-5432-1098") is True
    assert validate_aadhaar("0123 4567 8901") is False

    assert validate_cin("U28129PN1979PLC141032") is True
    assert validate_cin("L12345MH2020PLC123456") is True
    assert validate_cin("INVALIDCIN123") is False


def test_validate_ssn_with_indian_ids():
    assert validate_ssn("123-45-6789") is True
    assert validate_ssn("ABCDE1234F") is True
    assert validate_ssn("9876 5432 1098") is True
    assert validate_ssn("U28129PN1979PLC141032") is True
    assert validate_ssn("ABC1234567") is True


def test_validate_org_structural_rules():
    # Valid Organizations with Corporate Indicators
    assert validate_org("Example Technologies Pvt Ltd") is True
    assert validate_org("KSH International Private Limited") is True
    assert validate_org("Apex Solutions Inc.") is True
    assert validate_org("Vanguard Consultants LLP") is True
    assert validate_org("ICICI Securities Limited") is True

    # Generic Table Headers & Non-ORG Strings
    assert validate_org("REGISTRAR TO THE OFFER") is False
    assert validate_org("BID/OFFER PERIOD") is False
    assert validate_org("NAME OF THE REGISTRAR") is False
    assert validate_org("RISKS IN RELATION TO THE FIRST OFFER") is False
    assert validate_org("ISSUER'S ABSOLUTE RESPONSIBILITY") is False


def test_validate_person_structural_rules():
    # Valid Person Names
    assert validate_person("Ms. Rashi Patil") is True
    assert validate_person("Mr. Rohan Dey") is True
    assert validate_person("Kushal Subbayya Hegde") is True
    assert validate_person("Sarthak Malvadkar") is True

    # Generic Table Titles & Non-Person Strings
    assert validate_person("Company") is False
    assert validate_person("Risks") is False
    assert validate_person("BID/OFFER") is False
    assert validate_person("DETAILS OF THE OFFER TO PUBLIC") is False


def test_validate_phone():
    assert validate_phone("+91 9876543210") is True
    assert validate_phone("+1 555 123 4567") is True
    assert validate_phone("9876543210", context_text="Call mobile: 9876543210") is True
    assert validate_phone("123456", context_text="Order ID: ORD-123456") is False


def test_validate_dob():
    assert validate_dob("12/04/1998", context_text="DOB: 12/04/1998") is True
    assert validate_dob("12/04/1998", context_text="Date of Birth 12/04/1998") is True
    assert validate_dob("15/08/2026", context_text="Date of Filing: 15/08/2026") is False
