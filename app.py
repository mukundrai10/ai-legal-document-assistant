
import re

def analyze_document(text):
    """Extract basic information from a sample legal document."""

    if not text.strip():
        return "Please enter some document text."

    words = re.findall(r"\b[\w'-]+\b", text)
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

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

    report = [
        "DOCUMENT ANALYSIS",
        "=" * 30,
        f"Word count: {len(words)}",
        f"Sentence count: {len([s for s in sentences if s.strip()])}",
        "",
        "Topics found:",
    ]

    if found_keywords:
        report.extend(f"- {word.title()}" for word in found_keywords)
    else:
        report.append("- No predefined keywords found.")

    report.extend([
        "",
        "Note: This is a basic text analysis, not legal advice."
    ])

    return "\n".join(report)


if __name__ == "__main__":
    sample = """
    This agreement requires payment within 30 days.
    Either party may request termination by written notice.
    """

    print(analyze_document(sample))
