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

    choice = st.selectbox(
        "Select Option",
        ["Login", "Sign Up"]
    )

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    # Signup

    if choice == "Sign Up":

        if st.button("Create Account"):

            try:
                auth.create_user_with_email_and_password(
                    email,
                    password
                )

                st.success("✅ Account Created Successfully")

            except:
                st.error("❌ Signup Failed")

    # Login

    else:

        if st.button("Login"):

            try:
                user = auth.sign_in_with_email_and_password(
                    email,
                    password
                )

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

    st.write("""
    - Streamlit
    - NLP (TF-IDF)
    - Firebase Auth
    - Scikit-Learn
    - Python
    """)

    st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background-color: #1E1E1E;
    color: white;
}

h1 {
    text-align: center;
    color: #4CAF50;
    font-size: 40px;
    font-weight: bold;
}

.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
}

.stButton>button:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------

def extract_text_from_pdf(file):

    pdf = PdfReader(file)

    text = "".join([
        page.extract_text() or ""
        for page in pdf.pages
    ])

    return text.strip()

# Resume Ranking

def rank_resumes(job_description, resumes):

    documents = [job_description] + resumes

    vectorizer = TfidfVectorizer().fit_transform(documents)

    vectors = vectorizer.toarray()

    job_desc_vector = vectors[0]

    resume_vectors = vectors[1:]

    return cosine_similarity(
        [job_desc_vector],
        resume_vectors
    ).flatten()

# Resume Tips

def generate_resume_tips(score):

    if score > 80:
        return "🔥 Excellent match!"

    elif score > 60:
        return "✅ Good resume. Add more keywords."

    else:
        return "⚡ Improve skills and experience section."

# ATS Score

def calculate_ats_score(score):

    return min(round(score * 100), 100)

# Missing Skills Detector

def find_missing_skills(job_description, resume_text):

    common_skills = [
        "python",
        "sql",
        "machine learning",
        "deep learning",
        "nlp",
        "tensorflow",
        "communication",
        "leadership",
        "excel",
        "power bi",
        "data analysis"
    ]

    job_description = job_description.lower()
    resume_text = resume_text.lower()

    required_skills = [
        skill for skill in common_skills
        if skill in job_description
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_text
    ]

    return ", ".join(missing_skills)

# ---------------- DAILY LIMIT ----------------

if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0

MAX_UPLOADS = 3

if st.session_state.upload_count >= MAX_UPLOADS:

    st.error("🚫 Daily upload limit reached")

    st.stop()

# ---------------- MAIN UI ----------------

st.title("🚀 AI Resume Ranking System")

if os.path.exists("upload.png"):
    st.image("upload.png", use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

# Upload Section

with col1:

    st.header("📤 Upload Resumes")

    if os.path.exists("resumeupload.png"):
        st.image(
            "resumeupload.png",use_container_width=True
            width=300
        )

    uploaded_files = st.file_uploader(
        "Upload PDF resumes",
        type=["pdf"],
        accept_multiple_files=True
        key="resume_uploader"
    )

    # File Size Limit

    if uploaded_files:

        for file in uploaded_files:

            if file.size > 5 * 1024 * 1024:
                st.error(
                    f"❌ {file.name} exceeds 5 MB"
                )
                st.stop()

# Job Description

with col2:

    st.header("📝 Job Description")

    job_description = st.text_area(
        "Enter Job Description",
        height=220
    )

# ---------------- ANALYZE BUTTON ----------------

if st.button("🚀 Analyze & Rank Resumes"):

    if uploaded_files and job_description:

        st.header("📊 Resume Ranking Results")

        resumes = [
            extract_text_from_pdf(file)
            for file in uploaded_files
        ]

        progress_bar = st.progress(0)

        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        scores = rank_resumes(
            job_description,
            resumes
        )

        # Results DataFrame

        results_df = pd.DataFrame({

            "Resume": [
                file.name
                for file in uploaded_files
            ],

            "Match Score (%)": (
                scores * 100
            ).round(2),

            "ATS Score": [
                calculate_ats_score(score)
                for score in scores
            ],

            "Missing Skills": [
                find_missing_skills(
                    job_description,
                    resume
                )
                for resume in resumes
            ],

            "AI Suggestion": [
                generate_resume_tips(score * 100)
                for score in scores
            ]

        }).sort_values(
            by="Match Score (%)",
            ascending=False
        )

        # Display Results

        st.dataframe(
            results_df,
            use_container_width=True
        )

        # Top Resume Card

        st.markdown(f"""
        <div style='padding:20px;
        background-color:#4CAF50;
        border-radius:12px;
        text-align:center;
        color:white;
        font-size:24px;'>
        🏆 Best Resume: {results_df.iloc[0]['Resume']}<br>
        ⭐ ATS Score: {results_df.iloc[0]['ATS Score']}
        </div>
        """, unsafe_allow_html=True)

        # Chart

        st.subheader("📈 Resume Match Score Chart")

        fig, ax = plt.subplots(figsize=(8, 4))

        ax.bar(
            results_df["Resume"],
            results_df["Match Score (%)"]
        )

        ax.set_ylabel("Score")
        ax.set_xlabel("Resume")

        plt.xticks(rotation=15)

        st.pyplot(fig)

        # Download Report

        csv = results_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Ranking Report",
            data=csv,
            file_name="resume_ranking_report.csv",
            mime="text/csv"
        )

        st.success("✅ Ranking Completed Successfully")

        st.balloons()

        st.session_state.upload_count += 1

    else:

        st.warning(
            "⚠️ Upload resumes and enter job description"
        )
