# PII Redaction Tool & Web Application for DOCX Documents

A general-purpose, privacy-focused application and web interface that accepts an arbitrary `.docx` file, detects Personally Identifiable Information (PII), Identification Numbers, and Website URLs, and generates a redacted `.docx` document with realistic synthetic replacements while preserving formatting, table structures, headers, footers, punctuation, and letter casing.

---

## 🚀 Web Application & Deployment Options

### Option 1: Streamlit Community Cloud (Recommended - 100% Free)
1. Go to **[share.streamlit.io](https://share.streamlit.io/)**.
2. Click **"New App"** and select your GitHub repository `ayushsingh-01/PII_Redaction`.
3. Set **Main file path** to `app.py`.
4. Click **"Deploy"**! Your web app will be live with a shareable URL and direct `.docx` download button.

### Option 2: Hugging Face Spaces (Free)
1. Create a new Space on **[huggingface.co/spaces](https://huggingface.co/spaces)**.
2. Choose **Streamlit** as the Space SDK.
3. Push/Sync this GitHub repo.

### Option 3: Run Web App Locally
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```
Open `http://localhost:8501` in your browser to drag & drop documents and download redacted outputs directly.

---

## Supported Categories

1. **Full Names** (`PERSON`)
2. **Email Addresses** (`EMAIL`)
3. **Websites / URLs** (`URL`)
4. **Phone Numbers** (`PHONE`)
5. **Company Names** (`ORG`)
6. **Physical Addresses** (`ADDRESS`)
7. **Social Security & National IDs** (`SSN` - US SSN, Indian PAN, Aadhaar, CIN, Voter ID)
8. **Credit Card Numbers** (`CREDIT_CARD` - Luhn Validated)
9. **Dates of Birth** (`DOB` - Context Validated)
10. **IP Addresses** (`IP` - IPv4 & IPv6 Validated)

---

## CLI Usage

```bash
python main.py input/document.docx --output output/redacted.docx
```
