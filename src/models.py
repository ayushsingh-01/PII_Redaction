"""
Core Data Models for PII Redaction Tool.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class PIIEntity:
    """
    Represents a detected PII entity within text.
    """
    entity_type: str        # e.g., "PERSON", "EMAIL", "PHONE", "ORG", "ADDRESS", "SSN", "CREDIT_CARD", "DOB", "IP"
    text: str               # The detected text string
    start: int              # Start character index in the parent block text
    end: int                # End character index in the parent block text
    confidence: float       # Detection confidence score (0.0 - 1.0)
    source: str             # Detection method, e.g., "regex", "spacy_ner", "context_heuristic"

    def __post_init__(self):
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"Invalid entity span: start={self.start}, end={self.end}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {self.confidence}")

@dataclass(unsafe_hash=True)
class DocumentBlock:
    """
    Represents a logical text block extracted from a DOCX file (e.g. Paragraph, Table Cell, Header, Footer).
    """
    block_type: str         # "paragraph", "table_cell", "header", "footer"
    text: str               # Full string of the text block
    block_id: str           # Unique identifier for the block
    element_ref: Any = field(hash=False)  # Reference to underlying docx element
    section_index: int = 0  # Section index if header/footer

@dataclass
class RedactionStats:
    """
    Summary statistics of entities detected and redacted.
    """
    total_entities: int = 0
    entity_counts: Dict[str, int] = field(default_factory=dict)
    blocks_processed: int = 0
    processing_time_seconds: float = 0.0

    def add_entity(self, entity_type: str):
        self.total_entities += 1
        self.entity_counts[entity_type] = self.entity_counts.get(entity_type, 0) + 1
