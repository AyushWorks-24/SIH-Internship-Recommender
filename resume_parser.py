# resume_parser.py

import spacy
import json
import PyPDF2
from docx import Document
import re

# Load the spaCy model and skills from the JSON file
nlp = spacy.load("en_core_web_sm")
with open('skills.json', 'r') as f:
    SKILL_LIST = json.load(f)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_skills_from_resume(file_path):
    """
    Reads a resume file (PDF or DOCX), extracts text, and finds matching skills.
    """
    # 1. Extract raw text from the file
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return []

    # 2. Pre-process text and use NLP to find skills
    # We use a simple regex-based approach for high recall on our skill list
    found_skills = set()
    for skill in SKILL_LIST:
        # Create a regex pattern to find the skill as a whole word, case-insensitive
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.add(skill.capitalize()) # Standardize the skill format


    return sorted(list(found_skills))
