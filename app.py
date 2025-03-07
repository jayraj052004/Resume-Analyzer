import streamlit as st
import pdfplumber
import spacy
import matplotlib.pyplot as plt
from collections import Counter

# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    """
    This function takes a PDF file as input and returns the text content 
    of the PDF as a string.
    """
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # Check if page_text is not None or empty
                text += page_text
        return text.strip()  # Remove leading/trailing whitespace

def analyze_resume(text):
    """
    This function analyzes the resume text and extracts key information like
    total words, top keywords, entities (names, organizations, locations), 
    and skills.
    """
    doc = nlp(text)  # Process the text with spaCy

    # Extract words (excluding punctuation and special characters)
    words = [token.text.lower() for token in doc if token.is_alpha]
    word_freq = Counter(words)  # Count word frequencies

    # Define a set of skills to look for
    skills = {"python", "java", "html", "css", "javascript", "excel", "sql", 
              "power bi", "machine learning"}
    extracted_skills = [word for word in words if word in skills]

    # Extract entities (names, organizations, locations, etc.)
    entities = []
    for entity in doc.ents:
        entities.append((entity.text, entity.label_))

    # Return the analysis results
    return {
        "Total Words": len(words),
        "Top 10 Keywords": word_freq.most_common(10),
        "Entities": entities,
        "Skills": list(set(extracted_skills))  # Remove duplicate skills
    }

# Streamlit UI
st.set_page_config(page_title="Resume Analyzer", layout="wide")

# Add some styling to the page
st.markdown("""
    <style>
        .big-title {
            text-align: center; 
            font-size: 36px; 
            font-weight: bold; 
            color: #4A90E2;
        }
        .sub-text {
            text-align: center; 
            font-size: 20px; 
            color: #777;
        }
        .result-box {
            padding: 15px; 
            background-color: #f9f9f9; 
            border-radius: 8px; 
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='big-title'>📄 Resume Analyzer</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>Upload your resume PDF and get insights instantly!</p>", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Analyzing Resume..."):
        text = extract_text_from_pdf(uploaded_file)

        if text:
            results = analyze_resume(text)

            st.subheader("📊 Analysis Report")
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)

            st.write("### ✅ Resume Insights")
            st.write(f"**Total Words:** {results['Total Words']}")
            st.write("**Top 10 Keywords:**", results['Top 10 Keywords'])

            st.write("### 🔍 Named Entities")
            if results['Entities']:
                # Create a DataFrame for entities
                entity_table = {"Entity": [ent[0] for ent in results['Entities']], 
                                "Label": [ent[1] for ent in results['Entities']]}
                st.dataframe(entity_table, use_container_width=True)
            else:
                st.write("No named entities detected.")

            st.write("### 🛠 Extracted Skills")
            if results['Skills']:
                st.write(", ".join(results['Skills']))
            else:
                st.write("No relevant skills detected.")

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Could not extract text from the PDF. Please upload a clear resume.")
            