# PII Redaction Tool for DOCX Documents

## Approach
This tool implements a hybrid PII detection and redaction pipeline for arbitrary `.docx` documents across paragraphs, tables, headers, and footers. It combines pattern-based regex (emails, URLs, IP addresses, Luhn-validated credit cards, US SSN, and Indian ID numbers like PAN, Aadhaar, CIN, and Voter ID), SpaCy Named Entity Recognition (`en_core_web_sm`) with contextual prefix/suffix heuristics for person names and organizations, `phonenumbers` validation for phone numbers, and a document-level mapping cache to ensure consistent synthetic replacements while preserving font styling, letter casing, list delimiters, and table layouts.

## Tradeoffs, False Positives & False Negatives
- **Tradeoffs**: Requiring structural business indicators (e.g., corporate suffixes like `Pvt Ltd` or `Inc`) prevents non-PII table headers and legal titles from being corrupted, but requires strict context verification.
- **False Positives**: Can occur if capitalized generic phrases resemble organizational names or overlap with location keywords.
- **False Negatives**: Can occur on un-prefixed single-word names or non-standard regional street addresses that lack postal codes or explicit address labels.
