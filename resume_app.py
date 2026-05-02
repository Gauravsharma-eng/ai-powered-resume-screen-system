import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import time
import os
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- ⚙️ CONFIG ----------------
st.set_page_config(page_title="🚀 Resume Ranking System", layout="wide", page_icon="🎯")

# 🎨 **Custom CSS for a Beautiful UI**
st.markdown("""
    <style>
    .stApp { background-color: #1E1E1E; color: white; }
    h1 { text-align: center; color: #4CAF50; font-size: 36px; font-weight: bold; }
    .stTextArea, .stFileUploader { border-radius: 10px; box-shadow: 0 0 10px #4CAF50; }
    .stButton>button {
        background-color: #4CAF50; color: white; padding: 12px 18px;
        font-size: 18px; border-radius: 8px; border: none; transition: 0.3s; width: 100%;
    }
    .stButton>button:hover { background-color: #45a049; }
    </style>
""", unsafe_allow_html=True)

# 📌 **Functions**
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = "".join([page.extract_text() or "" for page in pdf.pages])
    return text.strip()

def rank_resumes(job_description, resumes):
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    job_desc_vector = vectors[0]
    resume_vectors = vectors[1:]
    return cosine_similarity([job_desc_vector], resume_vectors).flatten()

def generate_resume_tips(score):
    if score > 80: return "🔥 Excellent match! Your resume is well-optimized."
    elif score > 60: return "✅ Good match! Consider adding more relevant keywords."
    else: return "⚡ Low match! Try improving your skills section."

# ---------------- 🚀 UI LAYOUT ----------------

# Page Title
st.title("🚀 Resume Ranking System")

# 📸 Top Banner / Upload Image (upload.png logic)
if os.path.exists("upload.png"):
    st.image("upload.png", use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("📤 Upload Resumes")
    # Reference image for upload section (resumeupload.png)
    if os.path.exists("resumeupload.png"):
        st.image("resumeupload.png", caption="Supported: PDF format", width=300)
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

with col2:
    st.header("📝 Job Description")
    job_description = st.text_area("Enter the job description...", height=200)

# 📌 **Start Ranking Process**
if st.button("🚀 Analyze & Rank Resumes"):
    if uploaded_files and job_description:
        # Screening logic starts (screening.png context)
        st.header("📊 Resume Rankings")
        
        if os.path.exists("screening.png"):
            st.image("screening.png", caption="AI Analysis in Progress", use_container_width=True)

        resumes = [extract_text_from_pdf(file) for file in uploaded_files]

        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        scores = rank_resumes(job_description, resumes)

        results_df = pd.DataFrame({
            "Resume": [file.name for file in uploaded_files],
            "Match Score (%)": (scores * 100).round(2),
            "AI Suggestion": [generate_resume_tips(score * 100) for score in scores]
        }).sort_values(by="Match Score (%)", ascending=False)

        # Display Data
        st.dataframe(results_df.style.format({"Match Score (%)": "{:.2f}"}), use_container_width=True)
        
        st.success(f"✅ Ranking Complete! 🎯 Top Match: **{results_df.iloc[0]['Resume']}**")
        st.balloons()
    else:
        st.warning("⚠️ Please upload resumes AND enter a job description first!")

# Sidebar info
with st.sidebar:
    st.title("👨‍💻 Project Details")
    st.info("Developed by **Gaurav**")
    st.write("📍 Gwalior, India")
    st.markdown("---")
    st.write("🚀 **Tech Stack:**")
    st.write("- Streamlit\n- NLP (TF-IDF)\n- Scikit-Learn")
