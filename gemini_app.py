
import streamlit as st
from google import genai
from pypdf import PdfReader
from io import BytesIO

st.set_page_config(
    page_title="AI Legal Document Assistant",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ AI Legal Document Assistant")
st.write("Upload a document and use AI to understand it in simple language.")

st.warning(
    "For educational purposes only. AI can make mistakes "
    "and this tool does not provide legal advice."
)

uploaded_file = st.file_uploader(
    "Upload a TXT or text-based PDF",
    type=["txt", "pdf"]
)

document_text = ""

if uploaded_file:
    try:
        if uploaded_file.name.lower().endswith(".txt"):
            document_text = uploaded_file.getvalue().decode(
                "utf-8", errors="replace"
            )
        else:
            pdf = PdfReader(BytesIO(uploaded_file.getvalue()))
            document_text = "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )

        st.success("Document loaded successfully!")

    except Exception as e:
        st.error(f"Could not read the document: {e}")

document_text = st.text_area(
    "Or paste your document text here",
    value=document_text,
    height=220,
    max_chars=30000
)

task = st.selectbox(
    "What would you like the AI to do?",
    [
        "Explain in simple English",
        "Summarize key points and obligations",
        "Identify clauses that may need review",
        "Generate questions to ask a lawyer"
    ]
)

if st.button("Analyze Document", type="primary"):
    if not document_text.strip():
        st.warning("Please upload a document or paste some text.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            prompt = f"""
You are an assistant that helps people understand legal documents.

Task: {task}

Analyze the text below.
Use clear, simple English and organized headings.
Do not invent facts or claim certainty where the text is unclear.
For clauses needing review, explain why they may deserve attention.
Do not present your answer as legal advice.

DOCUMENT:
{document_text[:20000]}
"""

            with st.spinner("AI is analyzing your document..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            st.subheader("Analysis")
            st.markdown(response.text or "No text response was returned.")

            if response.text:
                st.download_button(
                    "Download Analysis",
                    data=response.text,
                    file_name="legal_document_analysis.txt",
                    mime="text/plain"
                )

        except KeyError:
            st.error(
                "API key is not configured yet. "
                "Add GEMINI_API_KEY in Streamlit Secrets."
            )
        except Exception as e:
            st.error(
                "The analysis failed. Check your API key, "
                "API quota, and app logs."
            )
            st.caption(str(e))
