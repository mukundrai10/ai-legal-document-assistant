
import re
import streamlit as st


def analyze_document(text):
    words = re.findall(r"\b[\w'-]+\b", text)
    sentences = [
        sentence for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
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
    "Paste text from a legal document to get a basic "
    "text analysis report."
)

st.info(
    "Educational prototype: keyword detection does not determine "
    "legal validity or replace professional legal advice."
)

document_text = st.text_area(
    "Paste your document text here",
    height=220,
    placeholder="Paste a fictional agreement or sample clause...",
)

if st.button("Analyze Document", type="primary"):
    if not document_text.strip():
        st.warning("Please enter some text first.")
    else:
        word_count, sentence_count, keywords = analyze_document(
            document_text
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
