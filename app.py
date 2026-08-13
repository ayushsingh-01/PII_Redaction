"""
ShieldPII — Web Application for DOCX PII Redaction & Instant Download.
Built with Streamlit and Vanilla CSS glassmorphism styling.
"""

import os
import time
import tempfile
import streamlit as st
from pathlib import Path

from src.document_processor import DocumentProcessor
from src.pii_detector import PIIDetector
from src.replacement_generator import ReplacementGenerator
from src.redactor import DOCXRedactor


# 1. Streamlit Page Config
st.set_page_config(
    page_title="ShieldPII — DOCX PII Redactor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Modern Styling (Dark Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e1e2f 0%, #0f172a 100%);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 2rem;
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .main-header p {
        color: #94a3b8;
        font-size: 1.1rem;
    }

    .stMetric {
        background: rgba(30, 41, 59, 0.7);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header Banner
    st.markdown("""
    <div class="main-header">
        <h1>🔒 ShieldPII Redaction Studio</h1>
        <p>Upload any Word document (.docx) to automatically redact PII, URLs, and Identity Numbers while preserving formatting.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Controls
    with st.sidebar:
        st.header("⚙️ Redaction Options")
        seed = st.number_input("Random Generator Seed", min_value=1, max_value=9999, value=42)
        email_domain = st.text_input("Synthetic Email Domain", value="example.com")
        url_domain = st.text_input("Synthetic Website Domain", value="www.example.com")
        
        st.divider()
        st.markdown("### 🔍 Supported PII Types")
        st.markdown("""
        - 👤 **Full Names**
        - 📧 **Emails** & 🌐 **URLs**
        - 📞 **Phone Numbers**
        - 🏢 **Company Names**
        - 📍 **Addresses**
        - 🆔 **PAN, Aadhaar, CIN, Voter ID, SSN**
        - 💳 **Credit Cards** (Luhn Verified)
        - 🎂 **Dates of Birth**
        - 🌐 **IP Addresses**
        """)

    # Main File Upload Area
    uploaded_file = st.file_uploader(
        "Choose a DOCX document to redact",
        type=["docx"],
        help="Upload an arbitrary Microsoft Word .docx document"
    )

    if uploaded_file is not None:
        st.success(f"File uploaded successfully: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        
        if st.button("🚀 Process & Redact Document", type="primary", use_container_width=True):
            with st.spinner("Processing document text blocks, extracting entities, and applying redactions..."):
                start_time = time.time()
                
                # Save uploaded file to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
                    tmp_in.write(uploaded_file.getvalue())
                    tmp_in_path = tmp_in.name

                tmp_out_path = tmp_in_path + "_redacted.docx"

                try:
                    # 1. Extract Blocks
                    processor = DocumentProcessor(tmp_in_path)
                    blocks = processor.extract_blocks()

                    # 2. Detect PII
                    detector = PIIDetector()
                    block_entity_map = {}
                    total_detected = 0
                    type_counts = {}
                    location_counts = {}

                    for block in blocks:
                        entities = detector.detect(block.text)
                        if entities:
                            block_entity_map[block] = entities
                            total_detected += len(entities)
                            location_counts[block.block_type] = location_counts.get(block.block_type, 0) + len(entities)
                            for ent in entities:
                                type_counts[ent.entity_type] = type_counts.get(ent.entity_type, 0) + 1

                    # 3. Apply Redaction
                    replacement_gen = ReplacementGenerator(
                        seed=seed,
                        default_email_domain=email_domain,
                        default_url_domain=url_domain
                    )
                    redactor = DOCXRedactor(replacement_gen)
                    redactor.redact_document(processor.doc, block_entity_map)

                    # Save output
                    processor.doc.save(tmp_out_path)
                    elapsed = time.time() - start_time

                    # Read redacted doc bytes
                    with open(tmp_out_path, "rb") as f:
                        redacted_bytes = f.read()

                    # Cleanup temp files
                    os.unlink(tmp_in_path)
                    os.unlink(tmp_out_path)

                    # 4. Display Results Dashboard
                    st.balloons()
                    st.subheader("📊 Redaction Summary Dashboard")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Text Blocks", len(blocks))
                    with col2:
                        st.metric("PII Entities Redacted", total_detected)
                    with col3:
                        st.metric("Processing Time", f"{elapsed:.2f}s")
                    with col4:
                        st.metric("Status", "Complete ✅")

                    # Location & Type Breakdown
                    st.divider()
                    col_left, col_right = st.columns(2)

                    with col_left:
                        st.markdown("#### 📍 Redactions by Document Location")
                        st.json({
                            "Headers": location_counts.get("header", 0),
                            "Footers": location_counts.get("footer", 0),
                            "Body Paragraphs": location_counts.get("paragraph", 0),
                            "Table Cells": location_counts.get("table_cell", 0),
                        })

                    with col_right:
                        st.markdown("#### 🏷️ Redactions by Entity Category")
                        st.json(type_counts if type_counts else {"No PII Found": 0})

                    # Download Action Button
                    st.divider()
                    output_filename = f"redacted_{uploaded_file.name}"
                    st.download_button(
                        label=f"📥 Download Redacted Document ({output_filename})",
                        data=redacted_bytes,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"An error occurred during document redaction: {e}")
                    if os.path.exists(tmp_in_path):
                        os.unlink(tmp_in_path)


if __name__ == "__main__":
    main()
