"""
Replacement Generator for creating privacy-safe, consistent synthetic alternatives.
Maintains a document-level lookup cache to ensure consistent replacements.
Supports case-preservation and format-matching for US SSN and Indian Identification Numbers (PAN, Aadhaar, CIN, Voter ID).
"""

import re
import logging
from typing import Dict, Optional

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False

logger = logging.getLogger(__name__)


class ReplacementGenerator:
    """
    Generates synthetic PII replacements and maintains document-wide mapping consistency.
    """
    def __init__(self, seed: Optional[int] = 42, default_email_domain: str = "example.com", default_url_domain: str = "www.example.com"):
        self.default_email_domain = default_email_domain
        self.default_url_domain = default_url_domain
        self.mapping_cache: Dict[str, str] = {}
        self.counter = 1

        if FAKER_AVAILABLE:
            self.fake = Faker()
            if seed is not None:
                Faker.seed(seed)
                self.fake.seed_instance(seed)
        else:
            self.fake = None

    def get_replacement(self, entity_type: str, original_text: str) -> str:
        """
        Retrieves or generates a synthetic replacement for the given entity text.
        Guarantees exact consistency for duplicate entity occurrences.
        Preserves original letter casing (UPPERCASE, Title Case, lowercase).
        """
        cleaned_key = f"{entity_type.upper()}:{original_text.strip().lower()}"
        if cleaned_key in self.mapping_cache:
            raw_replacement = self.mapping_cache[cleaned_key]
        else:
            raw_replacement = self._generate_synthetic_value(entity_type, original_text)
            self.mapping_cache[cleaned_key] = raw_replacement

        return self._apply_casing(original_text, raw_replacement)

    def _apply_casing(self, original: str, replacement: str) -> str:
        """
        Matches synthetic replacement casing with original text format.
        """
        if original.isupper():
            return replacement.upper()
        elif original.islower():
            return replacement.lower()
        elif original.istitle():
            return replacement.title()
        return replacement

    def _generate_synthetic_value(self, entity_type: str, original_text: str) -> str:
        etype = entity_type.upper()

        if etype == "PERSON":
            if self.fake:
                name = self.fake.name()
            else:
                name = f"Alex Smith {self.counter}"

            orig_lower = original_text.lower()
            if orig_lower.startswith("mr."):
                return f"Mr. {name.split()[-1]}"
            elif orig_lower.startswith("ms."):
                return f"Ms. {name.split()[-1]}"
            elif orig_lower.startswith("dr."):
                return f"Dr. {name.split()[-1]}"
            elif orig_lower.startswith("prof."):
                return f"Prof. {name.split()[-1]}"
            return name

        elif etype == "EMAIL":
            user_part = f"user_{self.counter}"
            if self.fake:
                user_part = self.fake.user_name()
            self.counter += 1
            return f"{user_part}@{self.default_email_domain}"

        elif etype in ("URL", "WEBSITE"):
            if original_text.lower().startswith("https://"):
                return f"https://{self.default_url_domain}"
            elif original_text.lower().startswith("http://"):
                return f"http://{self.default_url_domain}"
            elif original_text.lower().startswith("www."):
                return f"{self.default_url_domain}"
            else:
                return f"www.example{self.counter}.com"

        elif etype == "PHONE":
            if original_text.startswith("+91"):
                return f"+91 91234 56{self.counter:03d}"
            elif original_text.startswith("+1"):
                return f"+1 555-01{self.counter:02d}"
            else:
                return f"+91 98765 00{self.counter:03d}"

        elif etype in ("ORG", "COMPANY"):
            if self.fake:
                company = self.fake.company()
            else:
                company = f"Acme Corporation {self.counter}"
            
            orig_lower = original_text.lower()
            if "pvt ltd" in orig_lower or "private limited" in orig_lower:
                return "Example Technologies Pvt Ltd"
            elif "ltd" in orig_lower or "limited" in orig_lower:
                return "Global Solutions Ltd"
            elif "inc" in orig_lower:
                return "Apex Systems Inc."
            elif "llp" in orig_lower:
                return "Vanguard Consultants LLP"
            return "Example Enterprises Ltd"

        elif etype == "ADDRESS":
            if self.fake:
                street = self.fake.street_address()
                city = self.fake.city()
                return f"{street}, Sector {self.counter}, {city} 110001"
            return f"{742 + self.counter} Example Road, Sector 12, Sample City 110001"

        elif etype == "SSN":
            orig_upper = original_text.strip().upper()

            # Indian PAN Card format (e.g. ABCDE1234F)
            if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', orig_upper):
                return f"ABZPS{1000 + self.counter:04d}K"

            # Indian Aadhaar format (12 digits e.g. 1234 5678 9012)
            elif re.match(r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}$', orig_upper):
                if "-" in original_text:
                    return f"9123-4567-89{self.counter:02d}"
                elif " " in original_text:
                    return f"9123 4567 89{self.counter:02d}"
                else:
                    return f"9123456789{self.counter:02d}"

            # Indian Corporate Identity Number (CIN) format e.g. U28129PN1979PLC141032
            elif re.match(r'^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$', orig_upper):
                return f"U99999MH2020PLC{100000 + self.counter}"

            # Indian Voter ID / EPIC format e.g. ABC1234567
            elif re.match(r'^[A-Z]{3}\d{7}$', orig_upper):
                return f"XYZ{1000000 + self.counter}"

            # US SSN format e.g. 123-45-6789
            else:
                return f"900-{self.counter:02d}-1234"

        elif etype == "CREDIT_CARD":
            return "4111 1111 1111 1111"

        elif etype == "IP":
            return f"192.0.2.{10 + self.counter}"

        elif etype == "DOB":
            if "/" in original_text:
                return "15/05/1995"
            elif "-" in original_text:
                return "1995-05-15"
            else:
                return "May 15, 1995"

        else:
            return f"[SYNTHETIC_{etype}_{self.counter}]"
