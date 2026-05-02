import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import time
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 🎨 Custom CSS for a Beautiful UI
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
    }
    .stApp {
        background-color: #1E1E1E;
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
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 255, 0, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# 📌 Page Title
st.title("🚀 Resume Ranking System")

# 📸 Add Banner Image
st.image("upload.png", use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.header("📤 Upload Resumes")

    # 📸 Resume Upload Image
    st.image("resumeupload.png", width=250)

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

with col2:
    st.header("📝 Job Description")

    # 📸 Screening Image
    st.image("screening.png", width=250)

    job_description = st.text_area("Enter the job description...")

# 📌 Extract Text from PDF Resumes

    st.pyplot(fig)
