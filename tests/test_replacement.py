"""
Tests for synthetic replacement generator and mapping consistency.
"""

import pytest
from src.replacement_generator import ReplacementGenerator


def test_replacement_consistency():
    generator = ReplacementGenerator(seed=42)

    rep1 = generator.get_replacement("PERSON", "Rashi Patil")
    rep2 = generator.get_replacement("PERSON", "Rashi Patil")

    assert rep1 == rep2
    assert rep1 != "Rashi Patil"

    email_rep1 = generator.get_replacement("EMAIL", "rashi.patil@gmail.com")
    email_rep2 = generator.get_replacement("EMAIL", "rashi.patil@gmail.com")

    assert email_rep1 == email_rep2
    assert "@example.com" in email_rep1


def test_replacement_safety():
    generator = ReplacementGenerator(seed=42)

    ip_rep = generator.get_replacement("IP", "192.168.1.10")
    assert ip_rep.startswith("192.0.2.")  # Reserved RFC 5737 documentation range

    cc_rep = generator.get_replacement("CREDIT_CARD", "4111 1111 1111 1111")
    assert cc_rep == "4111 1111 1111 1111"  # Safe test card

    ssn_rep = generator.get_replacement("SSN", "123-45-6789")
    assert ssn_rep.startswith("900-")  # Safe test SSN range
