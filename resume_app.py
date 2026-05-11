import streamlit as st
import pyrebase
from PyPDF2 import PdfReader
import pandas as pd
import time
import os
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="🚀 Resume Ranking System",
    layout="wide",
    page_icon="🎯"
)

# ---------------- FIREBASE CONFIG ----------------

firebaseConfig = {
    "apiKey": "AIzaSyBGpk8kNpoXi1WD0tFBrglzJ8hNZjyVCVY",
    "authDomain": "resume-ranking-system-42b7e.firebaseapp.com",
    "projectId": "resume-ranking-system-42b7e",
    "storageBucket": "resume-ranking-system-42b7e.firebasestorage.app",
    "messagingSenderId": "921266630636",
    "appId": "1:921266630636:web:cab54110158f28be025ac9",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0

# ---------------- LOGIN SYSTEM ----------------

if not st.session_state.logged_in:
    st.title("🔐 Resume Ranking Login")
    choice = st.selectbox("Select Option", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Sign Up":
        if st.button("Create Account"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("✅ Account Created Successfully")
            except:
                st.error("❌ Signup Failed")
    else:
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.rerun()
            except:
                st.error("❌ Invalid Email or Password")
    st.stop()

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("👨‍💻 Project Details")
    st.info("Developed by Gaurav")
    st.write("📍 Gwalior, India")
    st.markdown("---")
    st.write("🚀 Tech Stack")
    st.write("- Streamlit\n- NLP (TF-IDF)\n- Firebase Auth\n- Scikit-Learn\n- Python")
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp { background-color: #1E1E1E; color: white; }
h1 { text-align: center; color: #4CAF50; font-size: 40px; font-weight: bold; }
.stButton>button { background-color: #4CAF50; color: white; border-radius: 10px; height: 3em; width: 100%; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------

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
    if score > 80: return "🔥 Excellent match!"
    elif score > 60: return "✅ Good resume. Add more keywords."
    else: return "⚡ Improve skills and experience section."

def calculate_ats_score(score):
    return min(round(score * 100), 100)

def find_missing_skills(job_description, resume_text):
    common_skills = ["python", "sql", "machine learning", "deep learning", "nlp", "tensorflow", "communication", "leadership", "excel", "power bi", "data analysis"]
    job_description = job_description.lower()
    resume_text = resume_text.lower()
    required_skills = [s for s in common_skills if s in job_description]
    missing_skills = [s for s in required_skills if s not in resume_text]
    return ", ".join(missing_skills)

# ---------------- MAIN UI ----------------

MAX_UPLOADS = 10 # Increased for testing
if st.session_state.upload_count >= MAX_UPLOADS:
    st.error("🚫 Daily upload limit reached")
    st.stop()

st.title("🚀 AI Resume Ranking System")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("📤 Upload Resumes")
    uploaded_files = st.file_uploader("Upload PDF resumes", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            if file.size > 5 * 1024 * 1024:
                st.error(f"❌ {file.name} exceeds 5 MB")
                st.stop()

with col2:
    st.header("📝 Job Description")
    job_description = st.text_area("Enter Job Description", height=220)

# ---------------- ANALYZE ----------------

if st.button("🚀 Analyze & Rank Resumes"):
    if uploaded_files and job_description:
        st.header("📊 Resume Ranking Results")
        resumes = [extract_text_from_pdf(f) for f in uploaded_files]
        
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        scores = rank_resumes(job_description, resumes)
        
        results_df = pd.DataFrame({
            "Resume": [f.name for f in uploaded_files],
            "Match Score (%)": (scores * 100).round(2),
            "ATS Score": [calculate_ats_score(s) for s in scores],
            "Missing Skills": [find_missing_skills(job_description, r) for r in resumes],
            "AI Suggestion": [generate_resume_tips(s * 100) for s in scores]
        }).sort_values(by="Match Score (%)", ascending=False)

        st.dataframe(results_df, use_container_width=True)

        st.success(f"🏆 Best Resume: {results_df.iloc[0]['Resume']}")
        st.balloons()
        st.session_state.upload_count += 1
    else:
        st.warning("⚠️ Upload resumes and enter job description")
