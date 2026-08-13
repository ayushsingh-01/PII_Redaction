"""
PII Redaction Tool — Production CLI Application.

Usage:
    python main.py input/document.docx
    python main.py input/document.docx --output output/redacted.docx
"""

import sys
import os
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, List

from src.document_processor import DocumentProcessor
from src.pii_detector import PIIDetector
from src.replacement_generator import ReplacementGenerator
from src.redactor import DOCXRedactor
from src.models import DocumentBlock, PIIEntity


def setup_logging(verbose: bool = False):
    """
    Configures privacy-safe logging (never logs raw PII).
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    parser = argparse.ArgumentParser(
        description="PII Redaction Tool — Redacts PII from DOCX files using synthetic replacements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input/document.docx
  python main.py input/document.docx --output output/my_redacted_doc.docx
  python main.py input/document.docx --config config/config.yaml --verbose
        """
    )
    parser.add_argument("input_docx", type=str, help="Path to input .docx document")
    parser.add_argument("-o", "--output", type=str, default=None, help="Path for redacted output .docx file")
    parser.add_argument("-c", "--config", type=str, default="config/config.yaml", help="Path to YAML configuration file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    start_time = time.time()
    input_path = Path(args.input_docx)

    # 1. Input Path Validation
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    if input_path.suffix.lower() != ".docx":
        logger.error(f"Invalid file extension '{input_path.suffix}'. Only '.docx' files are supported.")
        sys.exit(1)

    # Determine Output Path
    if args.output:
        output_path = Path(args.output)
    else:
        out_dir = Path("output")
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"redacted_{input_path.name}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Loading document...")
    try:
        processor = DocumentProcessor(str(input_path))
    except Exception as e:
        logger.error(f"Failed to parse input DOCX file: {e}")
        sys.exit(1)

    logger.info("Extracting document text...")
    blocks = processor.extract_blocks()
    if not blocks:
        logger.warning("No text blocks found in document. Saving output unchanged.")
        processor.doc.save(str(output_path))
        logger.info(f"Saved output document to: {output_path}")
        sys.exit(0)

    logger.info(f"Processing {len(blocks)} document text blocks...")

    # 2. PII Detection
    logger.info("Running PII detection...")
    config_file = args.config if os.path.exists(args.config) else None
    detector = PIIDetector(config_path=config_file)

    block_entity_map: Dict[DocumentBlock, List[PIIEntity]] = {}
    total_detected = 0
    type_counts: Dict[str, int] = {}

    for block in blocks:
        entities = detector.detect(block.text)
        if entities:
            block_entity_map[block] = entities
            total_detected += len(entities)
            for ent in entities:
                type_counts[ent.entity_type] = type_counts.get(ent.entity_type, 0) + 1

    logger.info(f"Detected {total_detected} total PII entities.")
    for etype, count in sorted(type_counts.items()):
        logger.info(f"  - {etype}: {count}")

    # 3. Synthetic Replacement & Redaction
    logger.info("Generating synthetic replacements...")
    replacement_gen = ReplacementGenerator(seed=42)
    redactor = DOCXRedactor(replacement_gen)

    logger.info("Applying redactions...")
    stats = redactor.redact_document(processor.doc, block_entity_map)

    # 4. Save Output Document
    logger.info("Saving output document...")
    try:
        processor.doc.save(str(output_path))
    except Exception as e:
        logger.error(f"Failed to save redacted document to {output_path}: {e}")
        sys.exit(1)

    elapsed = time.time() - start_time
    logger.info(f"Redaction completed successfully in {elapsed:.2f} seconds.")
    logger.info(f"Redacted document saved to: {output_path}")


if __name__ == "__main__":
    main()
