
import re
import streamlit as st


def analyze_document(text):
    words = re.findall(r"\b[\w'-]+\b", text)
    sentences = [
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence
    ]

    keywords = [
        "agreement",
        "payment",
        "termination",
        "liability",
        "confidentiality",
        "notice",
    ]

    found_keywords = [
        word for word in keywords
        if re.search(r"\b" + word + r"\b", text, re.IGNORECASE)
    ]

    return len(words), len(sentences), found_keywords


st.set_page_config(
    page_title="Legal Document Assistant",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ AI Legal Document Assistant")

st.write(
    "Upload a text file or paste text from a legal document "
    "to generate a basic analysis report."
)

st.info(
    "Educational prototype. This tool detects predefined keywords "
    "and does not determine legal validity or replace legal advice."
)

uploaded_file = st.file_uploader(
    "Upload a text document (.txt)",
    type=["txt"],
)

document_text = st.text_area(
    "Or paste your document text here",
    height=220,
    placeholder="Paste a fictional agreement or sample clause...",
)

if st.button("Analyze Document", type="primary"):
    if uploaded_file is not None:
        try:
            text_to_analyze = uploaded_file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error("This file could not be read as UTF-8 text.")
            st.stop()
    else:
        text_to_analyze = document_text

    if not text_to_analyze.strip():
        st.warning("Please upload a non-empty file or enter some text.")
    else:
        word_count, sentence_count, keywords = analyze_document(
            text_to_analyze
        )

        st.subheader("Analysis Report")

        col1, col2 = st.columns(2)
        col1.metric("Word Count", word_count)
        col2.metric("Sentence Count", sentence_count)

        st.subheader("Detected Keywords")

        if keywords:
            for keyword in keywords:
                st.write(f"• {keyword.title()}")
        else:
            st.write("No predefined keywords detected.")

        st.caption(
            "This report identifies text patterns only. "
            "It does not assess legal risk or provide legal advice."
        )
