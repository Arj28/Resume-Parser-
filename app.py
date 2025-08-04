import streamlit as st
import pdfplumber
import re
from langdetect import detect

# Page config
st.set_page_config(page_title="Resume Parser", layout="centered")
st.title("📄 Rule-Based Resume Parser")
st.markdown("Upload a **PDF resume** to extract name, email, phone, language, and skills — without using ML models.")

uploaded_file = st.file_uploader("📤 Upload Resume (PDF)", type=["pdf"])

def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_info(text):
    lines = text.split('\n')

    name = lines[0].strip() if lines else "Not found"
    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.findall(r"\+?\d[\d\s\-\(\)]{9,}\d", text)

    # Language Detection
    try:
        lang = detect(text)
    except:
        lang = "Could not detect"

    # Skills matching
    with open("skills_list.txt") as f:
        known_skills = [skill.lower() for skill in f.read().splitlines()]
    matched_skills = [skill for skill in known_skills if skill in text.lower()]

    return {
        "Name": name,
        "Email": email[0] if email else "Not found",
        "Phone": phone[0] if phone else "Not found",
        "Language": lang,
        "Skills": matched_skills[:15],  # top 15 matches
        "Text Snippet": text[:800] + "..." if len(text) > 800 else text
    }

if uploaded_file:
    with st.spinner("Parsing resume..."):
        text = extract_text(uploaded_file)
        data = extract_info(text)

    st.success("✅ Resume parsed!")

    col1, col2 = st.columns(2)
    col1.metric("📛 Name", data["Name"])
    col2.metric("📧 Email", data["Email"])
    st.metric("📱 Phone", data["Phone"])
    st.metric("🌐 Language", data["Language"])

    with st.expander("🧠 Skills Found"):
        st.write(", ".join(data["Skills"]) if data["Skills"] else "No skills matched.")

    with st.expander("📃 Resume Text Snippet"):
        st.text(data["Text Snippet"])

    # Download summary
    summary = f"""Name: {data['Name']}
Email: {data['Email']}
Phone: {data['Phone']}
Language: {data['Language']}
Skills: {', '.join(data['Skills'])}
"""
    st.download_button("⬇️ Download Summary", summary, file_name="resume_summary.txt")
else:
    st.info("👈 Upload a resume to begin parsing.")
