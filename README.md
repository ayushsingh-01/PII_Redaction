# PII Redaction Tool for DOCX Documents

A general-purpose, privacy-focused Python application that accepts an arbitrary `.docx` file, detects Personally Identifiable Information (PII), Identification Numbers, and Website URLs, and generates a new `.docx` file where all detected entities are replaced with realistic but synthetic alternatives while preserving formatting, table structures, headers, footers, punctuation, and letter casing.

---

## Architecture & Processing Flow

```text
Input DOCX
    │
    ▼
Document Processor  ───────►  Extract Paragraphs, Tables, Headers, Footers
    │
    ▼
PII Detector Engine  ──────►  Hybrid Detection (Regex + SpaCy NER + Contextual Heuristics + URLs + Indian IDs)
    │
    ▼
Span Trimmer & Filter ─────►  Preserve Commas, Spaces, & Punctuation; Filter Non-PII Headers
    │
    ▼
Validation Engine   ───────►  Format & Boundary Validation (Luhn, IP, Phone, URL, PAN, Aadhaar, CIN, DOB Context)
    │
    ▼
Overlap Resolver    ───────►  Deterministic Conflict Resolution (Confidence > Type > Span)
    │
    ▼
Replacement Gen.    ───────►  Document-Consistent Synthetic Replacements + Casing Preservation
    │
    ▼
DOCX Redactor       ───────►  Run-Level Substitution (Preserves Bold, Italic, Color, Fonts)
    │
    ▼
Redacted Output DOCX
```

---

## Supported Categories

The tool detects and redacts 10 core categories of sensitive information:

1. **Full Names** (`PERSON`): Human names via SpaCy NER and prefix heuristics (`Mr.`, `Ms.`, `Dr.`, `Prof.`).
2. **Email Addresses** (`EMAIL`): Standard and tagged emails (`name@example.com`, `user+tag@example.co.in`).
3. **Websites / URLs** (`URL`): Domain names and web addresses (`www.example.com`, `https://domain.co.in`).
4. **Phone Numbers** (`PHONE`): International & domestic phone numbers (`+91 9876543210`, `+1 555 123 4567`) validated via `phonenumbers`.
5. **Company Names** (`ORG`): Organizations identified via SpaCy NER and corporate suffix matching (`Ltd`, `Pvt Ltd`, `LLP`, `Inc`).
6. **Physical Addresses** (`ADDRESS`): Street addresses, PIN/Postal codes, and contextual location blocks.
7. **Social Security & National IDs** (`SSN`):
   - US Social Security Numbers (`123-45-6789`).
   - **Indian Permanent Account Numbers (PAN)** (`ABCDE1234F`).
   - **Indian Aadhaar Numbers** (`9876 5432 1098`).
   - **Indian Corporate Identity Numbers (CIN)** (`U28129PN1979PLC141032`).
   - **Indian Voter ID / EPIC Numbers** (`ABC1234567`).
8. **Credit Card Numbers** (`CREDIT_CARD`): 13–19 digit payment cards validated with the **Luhn algorithm**.
9. **Dates of Birth** (`DOB`): Birth dates in multiple formats (`12/04/1998`, `April 12, 1998`) verified against DOB contextual cues.
10. **IP Addresses** (`IP`): IPv4 and IPv6 addresses verified with Python's standard `ipaddress` module.

---

## Key Features & Quality Enhancements

- **Indian Identification Numbers**: Integrated dynamic detection and validation for PAN, Aadhaar, CIN, and Voter IDs within the `SSN` category.
- **Punctuation & Delimiter Preservation**: Entity spans are strictly trimmed so commas `,`, periods `.`, colons `:`, and spaces between lists of names (e.g. `OUR PROMOTERS: NAME1, NAME2, NAME3`) are **100% preserved** without running text together.
- **Letter Case Preservation**: Synthetic replacements dynamically match the letter casing of original text (`KUSHAL SUBBAYYA HEGDE` -> `CRISTIAN SANTOS` in ALL CAPS).
- **Non-PII Header Protection**: Prospectus, financial, and table structure headers (e.g. `SIZE OF THE FRESH ISSUE`, `DETAILS OF THE OFFER TO PUBLIC`, `SEBI ICDR REGULATIONS`) are protected from false-positive company or name matches.

---

## Installation

### 1. Prerequisites
- Python 3.9+ installed.

### 2. Environment Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## Usage

```bash
python main.py input/document.docx
```

Custom Output Location:
```bash
python main.py input/document.docx --output output/custom_redacted.docx
```
