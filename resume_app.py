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
# Tip: Real project mein inke liye st.secrets use karein
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

# ---------------- CUSTOM CSS (MOBILE FIX) ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    /* Mobile par uploader ko click-friendly banane ke liye */
    [data-testid="stFileUploader"] {
        width: 100%;
        z-index: 999;
        position: relative;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 18px;
    }
    h1 {
        text-align: center;
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

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
                auth.sign_in_with_email_and_password(email, password)
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
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- HELPER FUNCTIONS ----------------
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = "".join([page.extract_text() or "" for page in pdf.pages])
    return text.strip()

def rank_resumes(job_description, resumes):
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    return cosine_similarity([vectors[0]], vectors[1:]).flatten()

def find_missing_skills(job_description, resume_text):
    common_skills = ["python", "sql", "machine learning", "deep learning", "nlp", "tensorflow", "excel", "data analysis"]
    job_desc = job_description.lower()
    resume_t = resume_text.lower()
    missing = [s for s in common_skills if s in job_desc and s not in resume_t]
    return ", ".join(missing) if missing else "None"

# ---------------- MAIN UI ----------------
st.title("🚀 AI Resume Ranking System")

MAX_UPLOADS = 3
if st.session_state.upload_count >= MAX_UPLOADS:
    st.error("🚫 Daily upload limit reached")
    st.stop()

st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Resumes")
    # Mobile par image uploader ko block na kare isliye width adjust ki hai
    if os.path.exists("resumeupload.png"):
        st.image("resumeupload.png", use_container_width=True)
    
    uploaded_files = st.file_uploader(
        "Upload PDF resumes", 
        type=["pdf"], 
        accept_multiple_files=True,
        key="resume_uploader" # Unique key for better state management
    )

with col2:
    st.header("📝 Job Description")
    job_description = st.text_area("Enter Job Description", height=250)

# ---------------- ANALYSIS ----------------
if st.button("🚀 Analyze & Rank Resumes"):
    if uploaded_files and job_description:
        with st.spinner("Analyzing resumes..."):
            resumes_text = [extract_text_from_pdf(f) for f in uploaded_files]
            scores = rank_resumes(job_description, resumes_text)
            
            results_df = pd.DataFrame({
                "Resume": [f.name for f in uploaded_files],
                "Match Score (%)": (scores * 100).round(2),
                "Missing Skills": [find_missing_skills(job_description, r) for r in resumes_text]
            }).sort_values(by="Match Score (%)", ascending=False)

            st.header("📊 Results")
            st.dataframe(results_df, use_container_width=True)
            
            best_resume = results_df.iloc[0]
            st.success(f"🏆 Best Match: {best_resume['Resume']} ({best_resume['Match Score (%)']}%)")
            
            st.session_state.upload_count += 1
            st.balloons()
    else:
        st.warning("⚠️ Please upload files and enter a job description.")
