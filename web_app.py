
import re
from io import BytesIO
from datetime import datetime

import streamlit as st
from pypdf import PdfReader


# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="Legal Document Assistant",
    page_icon="⚖️",
    layout="wide",
)

# ---------------------------------------
# DOCUMENT ANALYSIS
# ---------------------------------------

KEYWORDS = {
    "Agreement": ["agreement", "contract"],
    "Payment": ["payment", "invoice", "fees", "consideration"],
    "Termination": ["termination", "terminate", "expiry"],
    "Liability": ["liability", "liable", "damages"],
    "Confidentiality": ["confidentiality", "confidential"],
    "Notice": ["notice", "written notice"],
    "Indemnity": ["indemnity", "indemnify"],
    "Dispute Resolution": [
        "dispute resolution",
        "arbitration",
        "jurisdiction",
    ],
    "Force Majeure": ["force majeure"],
    "Governing Law": ["governing law", "applicable law"],
}


def extract_document_text(uploaded_file):
    """Extract text from an uploaded TXT or PDF file."""

    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if filename.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8-sig"), None
        except UnicodeDecodeError:
            return None, (
                "This text file could not be read as UTF-8. "
                "Save it as UTF-8 and upload it again."
            )

    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(file_bytes))

            if reader.is_encrypted:
                try:
                    if reader.decrypt("") == 0:
                        return None, (
                            "This PDF is password-protected. "
                            "Please upload an unprotected PDF."
                        )
                except Exception:
                    return None, (
                        "This PDF is password-protected "
                        "or could not be opened."
                    )

            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")

            extracted_text = "\n".join(pages).strip()

            if not extracted_text:
                return None, (
                    "No extractable text was found. "
                    "This PDF may be scanned or image-based. "
                    "OCR support is not included yet."
                )

            return extracted_text, None

        except Exception:
            return None, (
                "The PDF could not be read. "
                "Try another text-based PDF."
            )

    return None, "Please upload a TXT or PDF file."


def analyze_document(text):
    """Produce a basic text-analysis report."""

    words = re.findall(r"\b[\w'-]+\b", text)

    sentences = [
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]

    found_topics = []

    for topic, terms in KEYWORDS.items():
        for term in terms:
            pattern = r"\b" + re.escape(term) + r"\b"

            if re.search(pattern, text, re.IGNORECASE):
                found_topics.append(topic)
                break

    return len(words), len(sentences), found_topics


# ---------------------------------------
# SIDEBAR
# ---------------------------------------

with st.sidebar:
    st.title("⚖️ Legal Assistant")
    st.write("Your basic document-analysis workspace.")

    st.divider()

    st.subheader("Features")
    st.write("• TXT document upload")
    st.write("• PDF text extraction")
    st.write("• Word and sentence counts")
    st.write("• Contract-topic detection")
    st.write("• Downloadable report")

    st.divider()

    st.caption(
        "Educational prototype. Not a substitute "
        "for professional legal advice."
    )


# ---------------------------------------
# MAIN INTERFACE
# ---------------------------------------

st.title("⚖️ Legal Document Assistant")

st.write(
    "Upload a document or paste a contract clause "
    "to generate a basic analysis report."
)

st.info(
    "Privacy tip: Use sample documents for testing. "
    "Avoid uploading confidential client documents "
    "or sensitive personal information."
)

uploaded_file = st.file_uploader(
    "1. Upload a TXT or PDF document (optional)",
    type=["txt", "pdf"],
)

st.write("**OR**")

pasted_text = st.text_area(
    "2. Paste document text",
    height=220,
    placeholder=(
        "Example: This agreement requires payment "
        "within 30 days..."
    ),
)

if uploaded_file is not None and pasted_text.strip():
    st.caption(
        "A file is uploaded, so the app will analyze "
        "the file and ignore the pasted text."
    )

analyze_clicked = st.button(
    "Analyze Document",
    type="primary",
    use_container_width=True,
)

# ---------------------------------------
# ANALYZE AND DISPLAY RESULTS
# ---------------------------------------

if analyze_clicked:

    if uploaded_file is not None:
        document_text, error_message = extract_document_text(
            uploaded_file
        )

        if error_message:
            st.warning(error_message)
            st.stop()

    else:
        document_text = pasted_text

    if not document_text or not document_text.strip():
        st.warning(
            "Please upload a non-empty TXT/PDF file "
            "or paste some document text."
        )
        st.stop()

    word_count, sentence_count, topics = analyze_document(
        document_text
    )

    st.divider()
    st.header("📊 Analysis Report")

    col1, col2, col3 = st.columns(3)

    col1.metric("Word Count", word_count)
    col2.metric("Sentence Count", sentence_count)
    col3.metric("Topics Detected", len(topics))

    st.subheader("🔎 Detected Contract Topics")

    if topics:
        columns = st.columns(2)

        for index, topic in enumerate(topics):
            with columns[index % 2]:
                st.success(f"✓ {topic}")
    else:
        st.write(
            "No predefined contract topics were detected."
        )

    st.subheader("📄 Extracted Text Preview")

    preview = document_text[:3000]

    st.text_area(
        "First 3,000 characters",
        value=preview,
        height=180,
        disabled=True,
    )

    if len(document_text) > 3000:
        st.caption(
            "Preview shortened. The complete extracted text "
            "is included in the downloadable report."
        )

    report = f"""
LEGAL DOCUMENT ASSISTANT
========================

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DOCUMENT STATISTICS
-------------------
Word count: {word_count}
Sentence count: {sentence_count}

DETECTED TOPICS
---------------
{chr(10).join("- " + topic for topic in topics) if topics else "No predefined topics detected."}

IMPORTANT DISCLAIMER
--------------------
This report uses basic text extraction and keyword matching.
A detected topic does not establish that a clause is legally
valid, enforceable, complete, or risky.

This tool does not provide legal advice.

EXTRACTED DOCUMENT TEXT
-----------------------
{document_text}
"""

    st.download_button(
        label="⬇️ Download Full Analysis Report",
        data=report,
        file_name="legal_document_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.caption(
        "Analysis complete. Please have important legal "
        "documents reviewed by a qualified professional."
    )

# ---------------------------------------
# FOOTER
# ---------------------------------------

st.divider()

st.caption(
    "Legal Document Assistant | Educational prototype | "
    "Rule-based analysis, not legal advice"
)
