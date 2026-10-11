
import re
from io import BytesIO
from datetime import datetime

import streamlit as st
from pypdf import PdfReader


# ----------------------------------------
# PAGE SETTINGS
# ----------------------------------------

st.set_page_config(
    page_title="Legal Document Assistant",
    page_icon="⚖️",
    layout="wide",
)

# ----------------------------------------
# TOPIC DETECTION RULES
# ----------------------------------------

KEYWORDS = {
    "Agreement": ["agreement", "contract"],
    "Payment": ["payment", "invoice", "fees", "consideration"],
    "Termination": ["termination", "terminate", "expiry"],
    "Liability": ["liability", "liable", "damages"],
    "Confidentiality": ["confidentiality", "confidential"],
    "Notice": ["notice", "written notice"],
    "Indemnity": ["indemnity", "indemnify"],
    "Dispute Resolution": [
        "dispute resolution", "arbitration", "jurisdiction"
    ],
    "Force Majeure": ["force majeure"],
    "Governing Law": ["governing law", "applicable law"],
}

# General educational explanations, not legal conclusions.

CLAUSE_GUIDE = {
    "Agreement": {
        "meaning": (
            "This topic relates to an agreement or contract "
            "between parties."
        ),
        "check": (
            "Check who the parties are, what they agree to do, "
            "and whether their obligations are clearly described."
        ),
    },
    "Payment": {
        "meaning": (
            "This topic may describe money owed, fees, invoices, "
            "or payment obligations."
        ),
        "check": (
            "Look for payment amounts, due dates, payment methods, "
            "taxes, late fees, and conditions for payment."
        ),
    },
    "Termination": {
        "meaning": (
            "This topic may explain when or how an agreement "
            "can come to an end."
        ),
        "check": (
            "Look for permitted reasons, notice periods, termination "
            "procedures, and consequences after termination."
        ),
    },
    "Liability": {
        "meaning": (
            "This topic may concern responsibility for losses, "
            "damage, or other claims."
        ),
        "check": (
            "Review any limits on liability, exclusions, types of "
            "loss covered, and exceptions."
        ),
    },
    "Confidentiality": {
        "meaning": (
            "This topic may concern information that parties "
            "must keep confidential."
        ),
        "check": (
            "Check what information is covered, permitted disclosures, "
            "duration, and any exceptions."
        ),
    },
    "Notice": {
        "meaning": (
            "This topic may explain how formal communications "
            "must be delivered."
        ),
        "check": (
            "Look for permitted delivery methods, recipient details, "
            "notice periods, and when a notice takes effect."
        ),
    },
    "Indemnity": {
        "meaning": (
            "This topic may concern responsibility for specified "
            "losses, claims, or expenses."
        ),
        "check": (
            "Identify who gives the indemnity, what losses are covered, "
            "any exclusions, and the process for making a claim."
        ),
    },
    "Dispute Resolution": {
        "meaning": (
            "This topic may describe how disagreements between "
            "the parties should be handled."
        ),
        "check": (
            "Look for negotiation steps, arbitration or court procedures, "
            "the chosen forum, and applicable deadlines."
        ),
    },
    "Force Majeure": {
        "meaning": (
            "This topic may address certain exceptional events "
            "that affect contractual performance."
        ),
        "check": (
            "Review the covered events, notification requirements, "
            "mitigation duties, and possible consequences."
        ),
    },
    "Governing Law": {
        "meaning": (
            "This topic may identify the law intended to govern "
            "the agreement."
        ),
        "check": (
            "Check the named jurisdiction and how this clause interacts "
            "with any dispute-resolution provision."
        ),
    },
}


# ----------------------------------------
# EXTRACT TEXT FROM TXT OR PDF
# ----------------------------------------

def extract_document_text(uploaded_file):
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if filename.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8-sig"), None
        except UnicodeDecodeError:
            return None, (
                "This text file could not be read as UTF-8. "
                "Save it as UTF-8 and try again."
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
                    return None, "This PDF could not be opened."

            pages = [
                page.extract_text() or ""
                for page in reader.pages
            ]
            text = "\n".join(pages).strip()

            if not text:
                return None, (
                    "No extractable text was found. This PDF may be "
                    "scanned or image-based. OCR is not included yet."
                )

            return text, None

        except Exception:
            return None, (
                "The PDF could not be read. Try another text-based PDF."
            )

    return None, "Please upload a TXT or PDF file."


# ----------------------------------------
# ANALYZE DOCUMENT
# ----------------------------------------

def analyze_document(text):
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


# ----------------------------------------
# SIDEBAR
# ----------------------------------------

with st.sidebar:
    st.title("⚖️ Legal Assistant")
    st.write("Your document-analysis workspace.")

    st.divider()
    st.write("**Available features**")
    st.write("- TXT and PDF upload")
    st.write("- Word and sentence counts")
    st.write("- Contract-topic detection")
    st.write("- Plain-English clause guide")
    st.write("- Downloadable report")

    st.divider()
    st.caption("Educational prototype — not legal advice.")


# ----------------------------------------
# MAIN PAGE
# ----------------------------------------

st.title("⚖️ Legal Document Assistant")

st.write(
    "Upload a document or paste text to identify common "
    "contract topics and view a general educational guide."
)

st.info(
    "This app uses predefined keyword rules. It does not use "
    "an AI model or determine whether a contract is valid, "
    "enforceable, fair, or legally risky."
)

uploaded_file = st.file_uploader(
    "Upload a TXT or PDF file (optional)",
    type=["txt", "pdf"],
)

pasted_text = st.text_area(
    "Or paste document text here",
    height=220,
    placeholder="Paste a fictional contract or clause...",
)

if uploaded_file is not None and pasted_text.strip():
    st.caption(
        "The uploaded file takes priority over the pasted text."
    )

# ----------------------------------------
# RUN ANALYSIS
# ----------------------------------------

if st.button("Analyze Document", type="primary",
             use_container_width=True):

    if uploaded_file is not None:
        document_text, error = extract_document_text(uploaded_file)

        if error:
            st.warning(error)
            st.stop()
    else:
        document_text = pasted_text

    if not document_text or not document_text.strip():
        st.warning("Please upload a non-empty file or paste text.")
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

    # ------------------------------------
    # TOPIC GUIDE
    # ------------------------------------

    st.header("📚 Plain-English Clause Guide")

    if topics:
        st.write(
            "The following topics were detected by matching "
            "predefined words and phrases."
        )

        for topic in topics:
            guide = CLAUSE_GUIDE[topic]

            with st.expander(topic, expanded=True):
                st.markdown("**What it generally means**")
                st.write(guide["meaning"])

                st.markdown("**What to review**")
                st.write(guide["check"])

                st.caption(
                    "This is general educational information, "
                    "not an assessment of your specific clause."
                )
    else:
        st.warning(
            "No predefined topics were detected. This does not "
            "mean the document contains no important clauses."
        )

    # ------------------------------------
    # DOCUMENT PREVIEW
    # ------------------------------------

    st.header("📄 Extracted Text Preview")

    st.text_area(
        "First 3,000 characters",
        value=document_text[:3000],
        height=180,
        disabled=True,
    )

    if len(document_text) > 3000:
        st.caption(
            "Preview shortened. The full text is included "
            "in the downloadable report."
        )

    # ------------------------------------
    # DOWNLOAD REPORT
    # ------------------------------------

    topic_report = []

    for topic in topics:
        guide = CLAUSE_GUIDE[topic]

        topic_report.append(
            f"{topic}\n"
            f"General meaning: {guide['meaning']}\n"
            f"What to review: {guide['check']}"
        )

    report = f"""
LEGAL DOCUMENT ASSISTANT
========================

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

DOCUMENT STATISTICS
-------------------
Word count: {word_count}
Sentence count: {sentence_count}
Topics detected: {len(topics)}

PLAIN-ENGLISH TOPIC GUIDE
-------------------------
{"\n\n".join(topic_report) if topic_report else "No predefined topics detected."}

DISCLAIMER
----------
This report uses text extraction and predefined keyword matching.
The explanations are general educational information, not legal
advice or an assessment of this document's legal validity,
enforceability, fairness, completeness, or risk.

EXTRACTED DOCUMENT TEXT
-----------------------
{document_text}
"""

    st.download_button(
        "⬇️ Download Full Analysis Report",
        data=report,
        file_name="legal_document_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.success("Analysis complete.")

st.divider()

st.caption(
    "Legal Document Assistant | Educational prototype | "
    "Rule-based analysis, not legal advice"
)
