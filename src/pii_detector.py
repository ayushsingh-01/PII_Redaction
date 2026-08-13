"""
Extensible PII Detection Engine.
Combines Regex, SpaCy NER, Contextual Heuristics, Entity Trimming, and Overlap Resolution.
Uses structural and algorithmic validation for Person names and Organizations without static word lists.
"""

import re
import yaml
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple

from src.models import PIIEntity
from src.validators import (
    validate_luhn,
    validate_ip,
    validate_email,
    validate_url,
    validate_phone,
    validate_ssn,
    validate_dob,
    validate_org,
    validate_person,
)

logger = logging.getLogger(__name__)

SPACY_AVAILABLE = False
nlp_model = None
try:
    import spacy
    try:
        nlp_model = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except Exception:
        logger.warning("spaCy model 'en_core_web_sm' not found. Fallback to heuristic NER.")
except ImportError:
    logger.warning("spaCy package not installed. Fallback to heuristic NER.")


def trim_entity_span(text: str, start: int, end: int) -> Tuple[int, int, str]:
    """
    Trims leading and trailing punctuation/symbols (commas, colons, periods, quotes, brackets)
    from detected entity spans to ensure surrounding delimiters are preserved intact.
    """
    new_start = start
    new_end = end

    # Strip leading non-alphanumeric (except '+' or '$')
    while new_start < new_end and not (text[new_start].isalnum() or text[new_start] in "+$"):
        new_start += 1

    # Strip trailing non-alphanumeric
    while new_end > new_start and not text[new_end - 1].isalnum():
        new_end -= 1

    trimmed_str = text[new_start:new_end]
    return new_start, new_end, trimmed_str


class BaseDetector(ABC):
    """
    Abstract base class for all PII detectors.
    """
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def detect(self, text: str) -> List[PIIEntity]:
        """
        Detect PII entities in the given text string.
        """
        pass


class EmailDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("EMAIL", config)
        pattern = self.config.get("regex", r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b')
        self.pattern = re.compile(pattern)
        self.confidence = self.config.get("confidence", 0.99)

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        for match in self.pattern.finditer(text):
            candidate = match.group(0)
            if validate_email(candidate):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t:
                    entities.append(PIIEntity(
                        entity_type="EMAIL",
                        text=t,
                        start=s,
                        end=e,
                        confidence=self.confidence,
                        source="regex"
                    ))
        return entities


class URLDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("URL", config)
        pattern = self.config.get("regex", r'(?i)\b(?:https?://|www\.)[a-z0-9-]+(?:\.[a-z0-9-]+)+[/\w\.-]*\b|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|org|net|co\.in|in|io|gov|edu|biz|info)\b')
        self.pattern = re.compile(pattern)
        self.confidence = self.config.get("confidence", 0.98)

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        for match in self.pattern.finditer(text):
            candidate = match.group(0)
            if validate_url(candidate):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t:
                    entities.append(PIIEntity(
                        entity_type="URL",
                        text=t,
                        start=s,
                        end=e,
                        confidence=self.confidence,
                        source="regex_url"
                    ))
        return entities


class PhoneDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("PHONE", config)
        self.pattern = re.compile(r'(\+?\d{1,4}[-.\s]?)?(\(?\d{2,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}\b')
        self.confidence = self.config.get("confidence", 0.90)
        self.default_region = self.config.get("default_region", "IN")

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        for match in self.pattern.finditer(text):
            candidate = match.group(0).strip()
            digits = re.sub(r'\D', '', candidate)
            if len(digits) < 7 or len(digits) > 15:
                continue

            start_idx = max(0, match.start() - 30)
            end_idx = min(len(text), match.end() + 30)
            context_window = text[start_idx:end_idx]

            if validate_phone(candidate, default_region=self.default_region, context_text=context_window):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t:
                    entities.append(PIIEntity(
                        entity_type="PHONE",
                        text=t,
                        start=s,
                        end=e,
                        confidence=self.confidence,
                        source="regex_phonenumbers"
                    ))
        return entities


class SSNDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("SSN", config)
        self.confidence = self.config.get("confidence", 0.95)
        self.patterns = [
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'),
            re.compile(r'\b[2-9]\d{3}[-\s]?\d{4}[-\s]?\d{4}\b'),
            re.compile(r'\b[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b'),
            re.compile(r'\b[A-Z]{3}\d{7}\b'),
        ]

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        for pat in self.patterns:
            for match in pat.finditer(text):
                candidate = match.group(0)
                start_idx = max(0, match.start() - 30)
                end_idx = min(len(text), match.end() + 30)
                context_window = text[start_idx:end_idx]

                if validate_ssn(candidate, context_text=context_window):
                    s, e, t = trim_entity_span(text, match.start(), match.end())
                    if t:
                        entities.append(PIIEntity(
                            entity_type="SSN",
                            text=t,
                            start=s,
                            end=e,
                            confidence=self.confidence,
                            source="id_number_regex"
                        ))
        return entities


class CreditCardDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("CREDIT_CARD", config)
        self.pattern = re.compile(r'\b(?:\d[ -]*?){13,19}\b')
        self.confidence = self.config.get("confidence", 0.95)

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        for match in self.pattern.finditer(text):
            candidate = match.group(0).strip()
            if validate_luhn(candidate):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t:
                    entities.append(PIIEntity(
                        entity_type="CREDIT_CARD",
                        text=t,
                        start=s,
                        end=e,
                        confidence=self.confidence,
                        source="luhn_validation"
                    ))
        return entities


class IPDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("IP", config)
        self.pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b|\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')
        self.confidence = self.config.get("confidence", 0.95)

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        for match in self.pattern.finditer(text):
            candidate = match.group(0)
            if validate_ip(candidate):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t:
                    entities.append(PIIEntity(
                        entity_type="IP",
                        text=t,
                        start=s,
                        end=e,
                        confidence=self.confidence,
                        source="ipaddress_validation"
                    ))
        return entities


class DOBDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("DOB", config)
        self.confidence = self.config.get("confidence", 0.90)
        self.date_patterns = [
            re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])[\/\.-](0?[1-9]|1[0-2])[\/\.-](19|20)\d{2}\b'),
            re.compile(r'\b(19|20)\d{2}[\/\.-](0?[1-9]|1[0-2])[\/\.-](0?[1-9]|[12][0-9]|3[01])\b'),
            re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(0?[1-9]|[12][0-9]|3[01])(?:st|nd|rd|th)?,?\s+(19|20)\d{2}\b', re.I),
            re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(19|20)\d{2}\b', re.I),
        ]

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        for pat in self.date_patterns:
            for match in pat.finditer(text):
                candidate = match.group(0)
                start_idx = max(0, match.start() - 40)
                end_idx = min(len(text), match.end() + 40)
                context_window = text[start_idx:end_idx]

                if validate_dob(candidate, context_text=context_window):
                    s, e, t = trim_entity_span(text, match.start(), match.end())
                    if t:
                        entities.append(PIIEntity(
                            entity_type="DOB",
                            text=t,
                            start=s,
                            end=e,
                            confidence=self.confidence,
                            source="context_date_regex"
                        ))
        return entities


class NameDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("PERSON", config)
        self.confidence = self.config.get("confidence", 0.85)
        self.prefixes = self.config.get("prefixes", ["Mr.", "Ms.", "Mrs.", "Dr.", "Prof.", "Shri", "Smt."])
        prefix_pattern = r'\b(?:' + '|'.join(re.escape(p) for p in self.prefixes) + r')\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        self.prefix_regex = re.compile(prefix_pattern)

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        
        # 1. Prefix contextual detection
        for match in self.prefix_regex.finditer(text):
            candidate = match.group(0)
            if validate_person(candidate):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t and validate_person(t):
                    entities.append(PIIEntity(
                        entity_type="PERSON",
                        text=t,
                        start=s,
                        end=e,
                        confidence=0.95,
                        source="prefix_heuristic"
                    ))

        # 2. SpaCy NER detection if available
        if SPACY_AVAILABLE and nlp_model is not None:
            doc = nlp_model(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    candidate_text = ent.text.strip()
                    if validate_person(candidate_text):
                        s, e, t = trim_entity_span(text, ent.start_char, ent.end_char)
                        if t and validate_person(t):
                            entities.append(PIIEntity(
                                entity_type="PERSON",
                                text=t,
                                start=s,
                                end=e,
                                confidence=self.confidence,
                                source="spacy_ner"
                            ))
        return entities


class CompanyDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ORG", config)
        self.confidence = self.config.get("confidence", 0.95)
        self.suffixes = self.config.get("suffixes", [
            "Ltd", "Limited", "Pvt Ltd", "Private Limited", "LLP", "Inc", "Inc.",
            "Corporation", "Corp", "Technologies", "Industries", "Enterprises", "Solutions",
            "Co.", "Company"
        ])
        suffix_pattern = r'\b((?:[A-Z][A-Za-z0-9&.-]*\s+){1,6}(?:' + '|'.join(re.escape(s) for s in self.suffixes) + r'))\b'
        self.suffix_regex = re.compile(suffix_pattern)

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []

        # 1. Suffix heuristic detection
        for match in self.suffix_regex.finditer(text):
            candidate = match.group(0).strip()
            if validate_org(candidate):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t and validate_org(t):
                    entities.append(PIIEntity(
                        entity_type="ORG",
                        text=t,
                        start=s,
                        end=e,
                        confidence=0.95,
                        source="company_suffix_heuristic"
                    ))

        # 2. SpaCy ORG detection with structural validation
        if SPACY_AVAILABLE and nlp_model is not None:
            doc = nlp_model(text)
            for ent in doc.ents:
                if ent.label_ in ("ORG", "COMPANY"):
                    candidate_text = ent.text.strip()
                    if validate_org(candidate_text):
                        s, e, t = trim_entity_span(text, ent.start_char, ent.end_char)
                        if t and validate_org(t):
                            entities.append(PIIEntity(
                                entity_type="ORG",
                                text=t,
                                start=s,
                                end=e,
                                confidence=0.85,
                                source="spacy_ner"
                            ))
        return entities


class AddressDetector(BaseDetector):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ADDRESS", config)
        self.confidence = self.config.get("confidence", 0.88)
        self.pin_pattern = re.compile(r'\b\d{6}\b')
        self.address_context = re.compile(
            r'(?i)\b(address|registered office|corporate office|residence|mailing address|permanent address|communication address)\s*:\s*([^\n\r.]+)',
            re.I
        )
        self.keywords = [
            "House", "Flat", "Apartment", "Building", "Street", "Road", "Lane",
            "Sector", "Block", "District", "City", "State", "PIN", "Postal Code", "Marg", "Nagar"
        ]
        kw_pattern = r'\b(?:\d+[\/\d\w-]*\s+)?(?:' + '|'.join(re.escape(k) for k in self.keywords) + r')\b[^\n\r,.]{0,60}(?:\b\d{6}\b)?'
        self.heuristic_pattern = re.compile(kw_pattern, re.I)

    def detect(self, text: str) -> List[PIIEntity]:
        entities = []
        
        # 1. Address label pattern
        for match in self.address_context.finditer(text):
            addr_val = match.group(2).strip()
            if len(addr_val) > 5:
                val_start = match.start(2)
                val_end = match.end(2)
                s, e, t = trim_entity_span(text, val_start, val_end)
                if t:
                    entities.append(PIIEntity(
                        entity_type="ADDRESS",
                        text=t,
                        start=s,
                        end=e,
                        confidence=0.92,
                        source="address_label_heuristic"
                    ))

        # 2. Heuristic street/location scan
        for match in self.heuristic_pattern.finditer(text):
            candidate = match.group(0).strip()
            if len(candidate.split()) >= 2 or self.pin_pattern.search(candidate):
                s, e, t = trim_entity_span(text, match.start(), match.end())
                if t:
                    entities.append(PIIEntity(
                        entity_type="ADDRESS",
                        text=t,
                        start=s,
                        end=e,
                        confidence=self.confidence,
                        source="street_keyword_heuristic"
                    ))

        return entities


class PIIDetector:
    """
    Main Orchestrator for PII Detection across all registered detectors.
    """
    def __init__(self, config_path: Optional[str] = None):
        self.config = {}
        if config_path:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Could not load config file {config_path}: {e}")

        detector_cfg = self.config.get("detectors", {})

        # Plugin Registry of Detectors
        self.detectors: List[BaseDetector] = [
            EmailDetector(detector_cfg.get("email")),
            URLDetector(detector_cfg.get("url")),
            PhoneDetector(detector_cfg.get("phone")),
            SSNDetector(detector_cfg.get("ssn")),
            CreditCardDetector(detector_cfg.get("credit_card")),
            IPDetector(detector_cfg.get("ip")),
            DOBDetector(detector_cfg.get("dob")),
            NameDetector(detector_cfg.get("name")),
            CompanyDetector(detector_cfg.get("company")),
            AddressDetector(detector_cfg.get("address")),
        ]

    def register_detector(self, detector: BaseDetector):
        """Allows registering custom external detectors easily."""
        self.detectors.append(detector)

    def detect(self, text: str) -> List[PIIEntity]:
        """
        Detects all PII entities in text and applies overlap resolution.
        """
        if not text or not text.strip():
            return []

        raw_entities: List[PIIEntity] = []
        for detector in self.detectors:
            try:
                found = detector.detect(text)
                raw_entities.extend(found)
            except Exception as e:
                logger.error(f"Error in detector {detector.name}: {e}")

        # Deterministic Overlap Resolution
        resolved_entities = self.resolve_overlaps(raw_entities)
        return resolved_entities

    @staticmethod
    def resolve_overlaps(entities: List[PIIEntity]) -> List[PIIEntity]:
        """
        Resolves overlapping entities using a deterministic ranking:
        1. Higher confidence score
        2. Longer character span length
        3. Priority entity type
        """
        if not entities:
            return []

        type_priority = {
            "EMAIL": 10,
            "URL": 10,
            "CREDIT_CARD": 9,
            "SSN": 9,
            "IP": 8,
            "PHONE": 8,
            "DOB": 7,
            "ADDRESS": 6,
            "ORG": 5,
            "PERSON": 4,
        }

        sorted_entities = sorted(
            entities,
            key=lambda e: (
                e.confidence,
                e.end - e.start,
                type_priority.get(e.entity_type, 0),
                -e.start
            ),
            reverse=True
        )

        resolved: List[PIIEntity] = []
        for candidate in sorted_entities:
            overlap = False
            for existing in resolved:
                if not (candidate.end <= existing.start or candidate.start >= existing.end):
                    overlap = True
                    break
            if not overlap:
                resolved.append(candidate)

        resolved.sort(key=lambda e: e.start)
        return resolved
