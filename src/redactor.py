"""
DOCX Redactor for applying synthetic PII replacements to DOCX files.
Preserves formatting (bold, italic, font size, color, structure, images).
Includes bounds verification to prevent nested replacement corruption.
"""

import logging
from typing import List, Dict, Any
from docx import Document
from docx.text.paragraph import Paragraph

from src.models import DocumentBlock, PIIEntity, RedactionStats
from src.replacement_generator import ReplacementGenerator

logger = logging.getLogger(__name__)


class DOCXRedactor:
    """
    Applies synthetic replacements to DOCX text elements while preserving run formatting.
    """
    def __init__(self, replacement_generator: ReplacementGenerator):
        self.replacement_gen = replacement_generator

    def redact_document(self, doc: Document, block_entity_map: Dict[DocumentBlock, List[PIIEntity]]) -> RedactionStats:
        """
        Redacts PII entities across all document blocks and returns summary statistics.
        """
        stats = RedactionStats()

        for block, entities in block_entity_map.items():
            if not entities:
                continue

            paragraph: Paragraph = block.element_ref
            if not paragraph or not paragraph.runs:
                continue

            # Resolve overlaps again per block to ensure zero span collisions
            clean_entities = self._filter_block_overlaps(entities)

            # Sort entities right-to-left (descending start index) to prevent offset corruption
            sorted_entities = sorted(clean_entities, key=lambda e: e.start, reverse=True)

            for entity in sorted_entities:
                current_p_text = paragraph.text
                # Safeguard: Verify text at [entity.start, entity.end] matches expected entity text
                if 0 <= entity.start < len(current_p_text) and entity.end <= len(current_p_text):
                    actual_text = current_p_text[entity.start:entity.end]
                    # If offsets shifted due to unexpected split, perform safe replacement
                    if actual_text.strip() == entity.text.strip():
                        replacement_text = self.replacement_gen.get_replacement(entity.entity_type, entity.text)
                        self._replace_entity_in_paragraph(paragraph, entity.start, entity.end, replacement_text)
                        stats.add_entity(entity.entity_type)

            stats.blocks_processed += 1

        return stats

    def _filter_block_overlaps(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        """
        Discards overlapping entity spans within a single block, keeping longer, higher confidence spans.
        """
        if not entities:
            return []

        sorted_ents = sorted(entities, key=lambda e: (e.confidence, e.end - e.start), reverse=True)
        resolved: List[PIIEntity] = []

        for candidate in sorted_ents:
            overlap = False
            for existing in resolved:
                if not (candidate.end <= existing.start or candidate.start >= existing.end):
                    overlap = True
                    break
            if not overlap:
                resolved.append(candidate)

        resolved.sort(key=lambda e: e.start)
        return resolved

    def _replace_entity_in_paragraph(self, paragraph: Paragraph, start_idx: int, end_idx: int, replacement: str):
        """
        Replaces text spanning from start_idx to end_idx in a paragraph across one or multiple runs,
        preserving font styles and formatting.
        """
        runs = paragraph.runs
        if not runs:
            return

        # Compute character offset boundaries for each run
        run_spans = []
        current_offset = 0
        for run in runs:
            r_len = len(run.text)
            run_spans.append((current_offset, current_offset + r_len, run))
            current_offset += r_len

        # Find intersecting runs
        target_runs = []
        for r_start, r_end, run in run_spans:
            if not (end_idx <= r_start or start_idx >= r_end):
                target_runs.append((r_start, r_end, run))

        if not target_runs:
            return

        if len(target_runs) == 1:
            # Single run replacement
            r_start, r_end, run = target_runs[0]
            rel_start = start_idx - r_start
            rel_end = end_idx - r_start
            run.text = run.text[:rel_start] + replacement + run.text[rel_end:]
        else:
            # Multi-run replacement
            first_r_start, first_r_end, first_run = target_runs[0]
            last_r_start, last_r_end, last_run = target_runs[-1]

            rel_start = start_idx - first_r_start
            rel_end = end_idx - last_r_start

            first_run.text = first_run.text[:rel_start] + replacement

            for _, _, mid_run in target_runs[1:-1]:
                mid_run.text = ""

            last_run.text = last_run.text[rel_end:]
