# PII Redaction Tool — Complete Implementation Task

You are an experienced Python engineer specializing in DOCX document processing, NLP, PII detection, privacy-preserving data processing, testing, and software architecture.

Build a complete, production-quality Python application for a PII Redaction assignment.

---

# 1. Objective

Build a general-purpose tool that accepts an arbitrary `.docx` file and produces a new `.docx` file where detected personally identifiable information (PII) is replaced with realistic but synthetic alternatives.

The application must be **document-agnostic**.

It must NOT be hard-coded to any particular document, person, company, prospectus, or dataset.

The real assignment document will NOT be provided to you during development.

I will provide the real assignment DOCX myself later and test the completed application separately.

The final application should work with:

```bash
python main.py input/document.docx
```

and produce:

```text
output/redacted_document.docx
```

No source-code modification should be required when changing the input document.

---

# 2. Required PII Types

The system must detect and redact at minimum:

1. Full names
2. Email addresses
3. Phone numbers
4. Company names
5. Physical/mailing addresses
6. Social Security Numbers (SSNs)
7. Credit card numbers
8. Dates of birth
9. IP addresses

Design the architecture so additional PII types can be added easily later.

For example, adding PAN, passport number, driver's license, or bank account detection should not require rewriting the entire application.

---

# 3. Important Development Constraint

The actual assignment document / Red Herring Prospectus is NOT available during development.

Do NOT:

- ask for the assignment document
- assume it exists
- search for it online
- download a real prospectus
- hard-code PII from a real document
- create rules specifically designed for one prospectus
- use real people's private information as test data

The application must be completely generic.

Instead, create synthetic test documents containing fake PII.

The developer will later run:

```bash
python main.py path/to/real_assignment.docx
```

against the actual assignment document.

---

# 4. Recommended Technology

Use Python.

Recommended libraries:

- `python-docx` — DOCX reading/writing
- `spaCy` — PERSON and ORG NER
- `Faker` — synthetic replacement generation
- `phonenumbers` — phone validation
- `regex` or Python `re` — structured PII patterns
- Python `ipaddress` — IP validation
- standard-library utilities where possible

Do not use external APIs or cloud services.

All processing must happen locally.

If spaCy is used, specify the required model in `requirements.txt` and provide installation instructions.

Prefer lightweight, practical dependencies.

---

# 5. Project Structure

Create this structure:

```text
pii-redaction-tool/
│
├── README.md
├── requirements.txt
├── .gitignore
├── main.py
│
├── src/
│   ├── __init__.py
│   ├── document_processor.py
│   ├── pii_detector.py
│   ├── replacement_generator.py
│   ├── redactor.py
│   ├── validators.py
│   └── models.py
│
├── config/
│   └── config.yaml
│
├── input/
│
├── output/
│
├── evaluation/
│   ├── ground_truth.json
│   ├── evaluate.py
│   └── evaluation_report.md
│
├── examples/
│   ├── create_test_document.py
│   └── synthetic_test.docx
│
└── tests/
    ├── test_detector.py
    ├── test_replacement.py
    ├── test_redactor.py
    ├── test_validators.py
    └── test_evaluation.py
```

Keep responsibilities separated.

Do not put the entire implementation inside `main.py`.

---

# 6. CLI

Implement:

```bash
python main.py input/document.docx
```

Default output:

```text
output/redacted_document.docx
```

Also support:

```bash
python main.py input/document.docx --output output/my_redacted.docx
```

Add:

```bash
python main.py --help
```

The CLI should provide useful error messages.

---

# 7. Processing Pipeline

Implement this architecture:

```text
Input DOCX
    │
    ▼
Document Processor
    │
    ▼
Text Extraction
    │
    ▼
PII Detection
 ┌──┼───────────────┐
 │  │               │
Regex NER      Context Rules
 │  │               │
 └──┼───────────────┘
    ▼
Validation
    │
    ▼
Overlap Resolution
    │
    ▼
Replacement Generator
    │
    ▼
DOCX Redactor
    │
    ▼
Redacted DOCX
    │
    ▼
Detection Statistics
```

---

# 8. DOCX Processing

Use `python-docx`.

Do NOT extract all text and recreate the document from scratch.

Preserve the original document structure and formatting as much as reasonably possible.

Preserve:

- paragraphs
- character formatting
- fonts
- font size
- bold
- italic
- underline
- colors
- alignment
- lists
- tables
- headers
- footers
- section structure
- page layout where possible
- pictures/images
- existing document design

Process text in:

- normal paragraphs
- table cells
- headers
- footers

Pictures/images should remain unchanged.

IMPORTANT:

The assignment says the document may contain personal information inside normal document content. Do not delete or replace images simply because they exist.

For images containing text, document the limitation that OCR is not currently supported unless you implement it safely and locally.

---

# 9. Handling DOCX Runs

DOCX text can be split across multiple runs.

For example:

```text
Run 1: "Rashi "
Run 2: "Patil"
```

The detector should be able to detect the combined phrase where practical.

Design the document processor so detection can operate on logical paragraph/cell text while the redactor maps replacements back into the original runs.

Do not unnecessarily destroy formatting.

If perfect cross-run replacement is technically difficult, implement the safest reasonable strategy and document the limitation.

---

# 10. PII Entity Model

Create a common model, preferably using a dataclass.

It should contain:

```text
entity_type
text
start
end
confidence
source
```

Example:

```python
PIIEntity(
    entity_type="EMAIL",
    text="example@example.com",
    start=100,
    end=119,
    confidence=0.99,
    source="regex"
)
```

Use a consistent representation throughout the application.

---

# 11. Detection Architecture

Use a hybrid approach:

### Structured PII

Use regex plus validation for:

- email
- phone
- SSN
- credit card
- IP
- DOB

### Unstructured PII

Use spaCy NER plus contextual heuristics for:

- names
- organizations
- addresses

### Validation

Use validators to reduce false positives.

### Post-processing

Implement:

- normalization
- deduplication
- confidence ranking
- overlap resolution

---

# 12. Email Detection

Detect examples such as:

```text
john.doe@example.com
rashi.patil@gmail.com
user+tag@example.co.in
```

Use high-precision regex.

Do not modify ordinary text that only resembles an email.

---

# 13. Phone Detection

Support:

```text
+91 9876543210
+91-98765-43210
9876543210
+1 555 123 4567
```

Use `phonenumbers` where practical.

Support Indian phone numbers.

Do not classify every arbitrary long number as a phone number.

Use contextual information when necessary:

```text
phone
mobile
telephone
contact
cell
```

---

# 14. Full Name Detection

Use spaCy `PERSON`.

Also support contextual patterns such as:

```text
Mr. Rohan Dey
Ms. Rashi Patil
Dr. Amit Sharma
```

Do not simply treat every capitalized word as a person's name.

Use NER plus heuristics.

Document known limitations in README.

---

# 15. Company Detection

Use spaCy `ORG`.

Also support company suffixes such as:

```text
Ltd
Limited
Pvt Ltd
Private Limited
LLP
Inc
Inc.
Corporation
Corp
Technologies
Industries
Enterprises
Solutions
```

The assignment explicitly requires company names to be detected.

Document that this may produce false positives because business/company names are common in corporate documents.

---

# 16. Address Detection

Implement a heuristic address detector.

Support address indicators such as:

```text
House
Flat
Apartment
Building
Street
Road
Lane
Sector
Block
District
City
State
PIN
Postal Code
Country
```

Contextual indicators:

```text
Address
Registered Office
Corporate Office
Residence
Mailing Address
Permanent Address
Communication Address
```

Support Indian-style addresses and PIN codes.

Address detection is inherently more difficult than email/phone detection.

Document expected limitations.

---

# 17. SSN Detection

Detect standard SSNs:

```text
123-45-6789
```

Do not classify arbitrary nine-digit numbers as SSNs without sufficient evidence.

Use contextual detection where appropriate.

---

# 18. Credit Card Detection

Detect formats such as:

```text
4111 1111 1111 1111
4111-1111-1111-1111
4111111111111111
```

IMPORTANT:

Use the Luhn algorithm to validate candidates.

Do not classify arbitrary 16-digit numbers as credit cards.

For generated replacement values, use clearly synthetic/test values rather than generating potentially usable financial credentials.

---

# 19. Date of Birth Detection

Do NOT replace every date in the document.

Use context such as:

```text
DOB
D.O.B.
Date of Birth
Birth Date
Birthdate
Born
```

Then detect nearby dates.

Support:

```text
12/04/1998
12-04-1998
1998-04-12
April 12, 1998
```

Do not classify ordinary dates such as:

```text
Date of Filing: 15/08/2026
```

as DOB.

---

# 20. IP Address Detection

Support:

```text
192.168.1.10
10.0.0.1
```

and IPv6.

Use Python's `ipaddress` module for validation.

Do not rely on regex alone.

---

# 21. Overlap Resolution

Different detectors may detect the same text.

For example:

```text
phone detector
number detector
```

may both match the same value.

Implement deterministic overlap resolution.

Prefer:

1. higher confidence
2. more specific PII detector
3. longer valid span

Do not replace the same text multiple times.

---

# 22. Replacement Generator

Create a dedicated replacement generator.

Use Faker or safe deterministic generators.

Examples:

```text
PERSON:
Rashi Patil
→
Emily Carter

EMAIL:
rashi.patil@gmail.com
→
emily.carter@example.com

PHONE:
+91 9876543210
→
+91 9123456780

ADDRESS:
real address
→
742 Example Road, Sector 12

COMPANY:
real company
→
Example Technologies Pvt Ltd

DOB:
12/04/1998
→
23/08/1994

SSN:
123-45-6789
→
987-65-4321

CREDIT CARD:
real value
→
safe synthetic test value

IP:
192.168.1.10
→
192.0.2.10
```

---

# 23. Replacement Consistency

This is mandatory.

Maintain:

```text
original → replacement
```

mapping.

If:

```text
Rashi Patil
```

appears 20 times, all 20 occurrences must become the same generated name.

Likewise:

```text
rashi.patil@gmail.com
```

must always map to the same fake email.

The replacement mapping should be generated once per document and reused throughout processing.

Avoid generating a new replacement for every occurrence.

---

# 24. Replacement Safety

Never use real people's private information as replacement data.

For email addresses, use:

```text
example.com
example.org
example.net
```

For IP addresses, prefer documentation/reserved ranges.

For financial data, use safe synthetic/test values.

Make replacements clearly synthetic.

---

# 25. Privacy

This is a privacy-focused application.

Never:

- print original PII to terminal
- write original PII to logs
- send document content to external services
- call cloud AI APIs
- upload documents anywhere

Logs may contain:

```text
Detected 12 PERSON entities
Detected 8 EMAIL entities
Redaction completed
```

but must never contain:

```text
Detected Rashi Patil
Detected rashi.patil@gmail.com
```

---

# 26. Synthetic Test Document

Because the real assignment document is unavailable, create:

```text
examples/create_test_document.py
```

This script should generate:

```text
examples/synthetic_test.docx
```

The synthetic document must contain examples of every required PII type.

Include repeated PII values.

Example:

```text
Name: Rashi Patil
Email: rashi.patil@gmail.com
Phone: +91 9876543210
Date of Birth: 12/04/1998
Address: 123 Example Road, Sector 17, Chandigarh 160017
SSN: 123-45-6789
Credit Card: 4111 1111 1111 1111
IP Address: 192.168.1.10
Company: Example Technologies Pvt Ltd
```

Use clearly synthetic/test data.

Also include non-PII data such as:

```text
Order number: ORD-123456
Ticket number: TKT-987654
Invoice number: INV-2026-001
Product ID: PROD-12345
Document date: 15/08/2026
Revenue: 12,500,000
```

The detector should not automatically redact these as PII.

---

# 27. Synthetic Ground Truth

Create:

```text
evaluation/ground_truth.json
```

for the synthetic test document.

It should contain manually known entities.

Use it to validate the detector during development.

Do not invent evaluation metrics.

Metrics must be calculated from actual detector output.

---

# 28. Evaluation

Implement:

```text
evaluation/evaluate.py
```

It should compare detector output against ground truth.

Calculate:

- TP
- FP
- FN
- TN where meaningful
- Precision
- Recall
- F1
- Accuracy

Use:

```text
Precision = TP / (TP + FP)

Recall = TP / (TP + FN)

F1 = 2 × Precision × Recall / (Precision + Recall)

Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

Calculate results:

1. Overall
2. Per PII type

Important:

Accuracy is less meaningful for PII detection because most document content is non-PII.

Therefore explain that precision, recall, and F1 are the primary metrics.

Do not fabricate any metrics.

---

# 29. Evaluation Report

Create:

```text
evaluation/evaluation_report.md
```

Include:

1. Dataset
2. Evaluation methodology
3. Ground-truth methodology
4. Entity matching methodology
5. Per-type results
6. Overall results
7. False positives
8. False negatives
9. Known limitations
10. Future improvements

Use a table:

| PII Type | Ground Truth | Detected | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|

Do not claim the synthetic evaluation represents performance on every real-world document.

Clearly state that the final assignment evaluation will be performed separately on the real assignment DOCX.

---

# 30. Final Assignment Evaluation Workflow

The developer will later provide the actual assignment DOCX.

The tool must work without source-code modification:

```bash
python main.py path/to/real_assignment.docx
```

Expected output:

```text
output/redacted_real_assignment.docx
```

Then the developer will:

1. Inspect the original document.
2. Manually establish ground truth.
3. Run the detector.
4. Inspect the redacted output.
5. Update `evaluation/ground_truth.json`.
6. Run `evaluation/evaluate.py`.
7. Generate the final evaluation report.
8. Submit the source code, redacted DOCX, README, and evaluation report.

The implementation must support this workflow.

Do not require the real assignment file during development.

---

# 31. Tests

Write unit tests for:

- email detection
- phone detection
- name detection
- company detection
- address detection
- SSN detection
- credit-card detection
- Luhn validation
- DOB detection
- IP validation
- overlap handling
- replacement consistency
- document redaction
- evaluation metrics

Test repeated PII.

For example:

```text
Rashi Patil emailed rashi.patil@gmail.com.

Later, Rashi Patil called from rashi.patil@gmail.com.
```

Verify that both occurrences of the name have the same replacement and both email occurrences have the same replacement.

Also test that ordinary:

```text
ORD-123456
TKT-987654
INV-2026-001
```

are not unnecessarily redacted.

---

# 32. Formatting Tests

The synthetic DOCX should contain:

- bold PII
- italic PII
- PII inside tables
- PII inside headers
- PII inside footers
- PII in different font sizes
- PII surrounded by normal text

Verify that replacing PII does not unnecessarily destroy formatting.

Pictures should remain present.

Document any limitations.

---

# 33. Error Handling

Handle:

- missing file
- invalid file extension
- malformed DOCX
- empty document
- missing output directory
- permission errors
- invalid command-line arguments

Provide clear error messages.

Do not expose sensitive document content in error messages.

---

# 34. Logging

Use Python logging.

Example:

```text
INFO Loading document
INFO Extracting document text
INFO Running PII detection
INFO Detected 42 entities
INFO Generating synthetic replacements
INFO Applying redactions
INFO Saving output document
INFO Redaction completed successfully
```

Never log original PII.

---

# 35. README

Create a professional README containing:

## Overview

Explain what the tool does.

## Features

List all supported PII types.

## Architecture

Explain:

```text
DOCX
→ extraction
→ detection
→ validation
→ replacement
→ redaction
→ output
```

## Installation

Example:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Then:

```bash
pip install -r requirements.txt
```

If spaCy requires a model, provide the exact installation command.

## Usage

```bash
python main.py input/document.docx
```

## Custom Output

```bash
python main.py input/document.docx --output output/redacted.docx
```

## Detection Approach

Explain which PII types use:

- regex
- NER
- contextual rules
- validators

## Replacement Strategy

Explain deterministic mapping and consistency.

## Evaluation

Explain ground truth, precision, recall, F1, and accuracy.

## Limitations

Be honest about:

- names
- addresses
- organizations
- OCR/image text
- unusual document formatting
- ambiguous dates

## Extending the System

Explain how a developer can add another PII detector.

---

# 36. Code Quality

Use:

- type hints
- dataclasses where appropriate
- docstrings
- small functions
- meaningful variable names
- separation of concerns
- reusable classes
- error handling
- logging

Avoid:

- giant functions
- hard-coded PII
- duplicated logic
- external API dependencies
- unnecessary complexity

---

# 37. Extensibility

Make it easy to add a new detector.

For example, a future PAN detector should conceptually require:

```text
1. Add PAN pattern
2. Add PAN validator
3. Add PAN replacement generator
4. Register detector
```

without rewriting the document processor.

Prefer a detector registry/plugin-like architecture if it keeps the implementation clean.

---

# 38. Security and Privacy

Treat all input documents as sensitive.

Do not:

- upload documents
- call external APIs
- send text to LLMs
- store raw PII unnecessarily
- print PII
- commit test secrets

Add appropriate entries to `.gitignore`.

---

# 39. Important Design Decision: Redaction vs Masking

This assignment requires replacement with fake alternatives.

Therefore do NOT simply produce:

```text
[REDACTED]
```

Instead generate synthetic replacements:

```text
Rashi Patil
→
Emily Carter
```

```text
rashi.patil@gmail.com
→
emily.carter@example.com
```

The resulting document should remain readable and structurally useful.

---

# 40. Final Deliverables

Before finishing, ensure the repository contains:

```text
README.md
requirements.txt
main.py

src/
    document_processor.py
    pii_detector.py
    replacement_generator.py
    redactor.py
    validators.py
    models.py

examples/
    create_test_document.py
    synthetic_test.docx

evaluation/
    ground_truth.json
    evaluate.py
    evaluation_report.md

tests/
    test_detector.py
    test_replacement.py
    test_redactor.py
    test_validators.py
    test_evaluation.py
```

Generate the synthetic test document.

Run all tests.

Run the application against the synthetic document.

Verify the resulting DOCX.

Generate synthetic evaluation metrics from the actual synthetic ground truth and detector output.

Do NOT generate the final real-assignment evaluation metrics because the real assignment document has not been provided.

---

# 41. Final Verification

Before declaring the implementation complete:

1. Install dependencies.
2. Generate the synthetic DOCX.
3. Run all unit tests.
4. Run the redaction tool against the synthetic DOCX.
5. Verify the output DOCX opens successfully.
6. Verify repeated PII receives consistent replacements.
7. Verify tables remain intact.
8. Verify headers/footers remain intact.
9. Verify pictures remain present.
10. Verify non-PII identifiers are not unnecessarily redacted.
11. Run the evaluation script.
12. Generate the evaluation report.
13. Check that no original PII appears in logs.
14. Check that no external API is used.
15. Check that no real assignment document is required.
16. Check that the application accepts an arbitrary DOCX path.

---

# 42. Final Response

When implementation is complete, provide a concise summary containing:

- architecture used
- files created
- dependencies
- command to run the tool
- synthetic test results
- synthetic evaluation results
- known limitations
- exact command I should use later with the real assignment DOCX

Do not claim that the system has been evaluated on the real assignment document.

The real assignment document will be tested separately by me.