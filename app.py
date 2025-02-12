import spacy
import PyPDF2
from flask import Flask, render_template, request

app = Flask(__name__)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_skills(text):
    """Extracts keywords (skills) from text using NLP."""
    doc = nlp(text.lower())
    return {token.text for token in doc if token.pos_ in {"NOUN", "PROPN"}}

def extract_text_from_pdf(pdf_file):
    """Extracts raw text from a PDF file."""
    reader = PyPDF2.PdfReader(pdf_file)
    return " ".join([page.extract_text() or "" for page in reader.pages])

@app.route("/", methods=["GET", "POST"])
def index():
    match, missing = None, None

    if request.method == "POST":
        file = request.files.get("resume")
        job_description = request.form.get("job_description", "").strip()

        if file and job_description:
            resume_text = extract_text_from_pdf(file)
            resume_skills = extract_skills(resume_text)
            job_skills = extract_skills(job_description)

            if job_skills:
                match = round((len(resume_skills & job_skills) / len(job_skills)) * 100, 2)
                missing = list(job_skills - resume_skills)
            else:
                match, missing = 0, []

    return render_template("index.html", match=match, missing=missing)

if __name__ == "__main__":
    app.run(debug=True)
