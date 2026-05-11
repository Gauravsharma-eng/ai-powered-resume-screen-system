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

# ---------------- CUSTOM CSS (MOBILE & WEBVIEW FIX) ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    /* Mobile WebView click fix */
    [data-testid="stFileUploader"] {
        width: 100%;
        z-index: 999;
        position: relative;
    }
    h1 {
        text-align: center;
        color: #4CAF50;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .stDataFrame {
        background-color: #262730;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(file):
    try:
        pdf = PdfReader(file)
        text = "".join([page.extract_text() or "" for page in pdf.pages])
        return text.strip()
    except Exception as e:
        return ""

def rank_resumes(job_description, resumes):
    documents = [job_description] + resumes
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    job_desc_vector = vectors[0]
    resume_vectors = vectors[1:]
    return cosine_similarity([job_desc_vector], resume_vectors).flatten()

def find_missing_skills(job_description, resume_text):
    common_skills = ["python", "sql", "machine learning", "deep learning", "nlp", "tensorflow", "excel", "power bi", "data analysis"]
    job_desc = job_description.lower()
    resume_t = resume_text.lower()
    missing = [s for s in common_skills if s in job_desc and s not in resume_t]
    return ", ".join(missing) if missing else "None"

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
                st.success("✅ Account Created! Now please Login.")
            except:
                st.error("❌ Signup Failed. Check email format or password length.")
    else:
        if st.button("Login"):
            try:
                auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.rerun()
            except:
                st.error("❌ Invalid Email or Password")
    st.stop()

# ---------------- MAIN UI ----------------
st.title("🚀 AI Resume Ranking System")

# Sidebar
with st.sidebar:
    st.header("👨‍💻 Profile")
    st.info("Developed by Gaurav")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Daily Limit Check
MAX_UPLOADS = 10 
if st.session_state.upload_count >= MAX_UPLOADS:
    st.error("🚫 Daily upload limit reached!")
    st.stop()

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.header("📤 Upload Resumes")
    if os.path.exists("resumeupload.png"):
        st.image("resumeupload.png", use_container_width=True)
    
    uploaded_files = st.file_uploader(
        "Upload PDF resumes", 
        type=["pdf"], 
        accept_multiple_files=True,
        key="main_res_uploader" # Unique key for WebView stability
    )

with col2:
    st.header("📝 Job Description")
    job_description = st.text_area("Enter Job Description", height=250, placeholder="Paste the job requirements here...")

# ---------------- ANALYSIS & GRAPH ----------------
if st.button("🚀 Analyze & Rank Resumes"):
    if uploaded_files and job_description:
        with st.spinner("Processing Resumes..."):
            # 1. Text Extraction
            resumes_text = [extract_text_from_pdf(f) for f in uploaded_files]
            
            # 2. Ranking Logic
            scores = rank_resumes(job_description, resumes_text)
            
            # 3. Create Results Table
            results_df = pd.DataFrame({
                "Resume": [f.name for f in uploaded_files],
                "Match Score (%)": (scores * 100).round(2),
                "Missing Skills": [find_missing_skills(job_description, r) for r in resumes_text]
            }).sort_values(by="Match Score (%)", ascending=False)

            # 4. Display Table
            st.header("📊 Ranking Results")
            st.dataframe(results_df, use_container_width=True)

            # 5. Best Match Card
            best_name = results_df.iloc[0]['Resume']
            best_score = results_df.iloc[0]['Match Score (%)']
            st.success(f"🏆 **Winner:** {best_name} with {best_score}% Match!")

            # 6. Bar Chart Visualization
            st.markdown("### 📈 Match Visualization")
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Color the top bar green, others gray
            colors = ['#4CAF50' if x == max(results_df["Match Score (%)"]) else '#555555' 
                      for x in results_df["Match Score (%)"]]
            
            bars = ax.bar(results_df["Resume"], results_df["Match Score (%)"], color=colors)
            plt.xticks(rotation=45, ha='right')
            ax.set_ylabel("Match Score %")
            
            # Add labels on top of bars
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval}%', ha='center', va='bottom')

            st.pyplot(fig)
            
            st.session_state.upload_count += 1
            st.balloons()
    else:
        st.warning("⚠️ Please upload at least one PDF and provide a Job Description.")
