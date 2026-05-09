import streamlit as st
import pyrebase
from PyPDF2 import PdfReader
import pandas as pd
import time
import os
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- ⚙️ CONFIG ----------------

st.set_page_config(
    page_title="🚀 Resume Ranking System",
    layout="wide",
    page_icon="🎯"
)

# ---------------- 🔐 FIREBASE LOGIN ----------------

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

st.title("🔐 Login / Signup")

choice = st.selectbox(
    "Select Option",
    ["Login", "Sign Up"]
)

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

authentication = False

# ---------------- SIGNUP ----------------

if choice == "Sign Up":

    if st.button("Create Account"):

        try:
            auth.create_user_with_email_and_password(
                email,
                password
            )

            st.success("✅ Account Created Successfully!")

        except:
            st.error("❌ Signup Failed")

# ---------------- LOGIN ----------------

else:

    if st.button("Login"):

        try:
            user = auth.sign_in_with_email_and_password(
                email,
                password
            )

            authentication = True

            st.success("✅ Login Successful!")

        except:
            st.error("❌ Invalid Email or Password")

# Stop app if not logged in

if not authentication:
    st.stop()

# ---------------- 🎨 CUSTOM CSS ----------------

st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }

    h1 {
        text-align: center;
        color: #4CAF50;
        font-size: 36px;
        font-weight: bold;
    }

    .stTextArea, .stFileUploader {
        border-radius: 10px;
        box-shadow: 0 0 10px #4CAF50;
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 18px;
        font-size: 18px;
        border-radius: 8px;
        border: none;
        transition: 0.3s;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 📌 FUNCTIONS ----------------

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

    return cosine_similarity(
        [job_desc_vector],
        resume_vectors
    ).flatten()

def generate_resume_tips(score):

    if score > 80:
        return "🔥 Excellent match! Your resume is well-optimized."

    elif score > 60:
        return "✅ Good match! Consider adding more relevant keywords."

    else:
        return "⚡ Low match! Try improving your skills section."

# ---------------- 🚀 DAILY LIMIT ----------------

if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0

MAX_UPLOADS = 3

if st.session_state.upload_count >= MAX_UPLOADS:
    st.error("🚫 Daily upload limit reached")
    st.stop()

# ---------------- 🚀 MAIN UI ----------------

st.title("🚀 Resume Ranking System")

if os.path.exists("upload.png"):
    st.image("upload.png", use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    st.header("📤 Upload Resumes")

    if os.path.exists("resumeupload.png"):
        st.image(
            "resumeupload.png",
            caption="Supported: PDF format",
            width=300
        )

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    # File Size Limit

    if uploaded_files:

        for file in uploaded_files:

            if file.size > 5 * 1024 * 1024:
                st.error(
                    f"❌ {file.name} exceeds 5 MB"
                )
                st.stop()

with col2:

    st.header("📝 Job Description")

    job_description = st.text_area(
        "Enter the job description...",
        height=200
    )

# ---------------- 🚀 ANALYZE ----------------

if st.button("🚀 Analyze & Rank Resumes"):

    if uploaded_files and job_description:

        st.header("📊 Resume Rankings")

        if os.path.exists("screening.png"):
            st.image(
                "screening.png",
                caption="AI Analysis in Progress",
                use_container_width=True
            )

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

        results_df = pd.DataFrame({
            "Resume": [file.name for file in uploaded_files],

            "Match Score (%)":
            (scores * 100).round(2),

            "AI Suggestion":
            [
                generate_resume_tips(score * 100)
                for score in scores
            ]
        }).sort_values(
            by="Match Score (%)",
            ascending=False
        )

        st.dataframe(
            results_df.style.format({
                "Match Score (%)": "{:.2f}"
            }),
            use_container_width=True
        )

        st.success(
            f"✅ Ranking Complete! 🎯 Top Match: "
            f"**{results_df.iloc[0]['Resume']}**"
        )

        st.balloons()

        st.session_state.upload_count += 1

    else:
        st.warning(
            "⚠️ Please upload resumes AND enter a job description first!"
        )

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("👨‍💻 Project Details")

    st.info("Developed by Gaurav")

    st.write("📍 Gwalior, India")

    st.markdown("---")

    st.write("🚀 Tech Stack:")

    st.write("""
    - Streamlit
    - NLP (TF-IDF)
    - Scikit-Learn
    """)
