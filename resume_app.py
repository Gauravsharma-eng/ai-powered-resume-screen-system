import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import time
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- ⚙️ CONFIG ----------------
st.set_page_config(page_title="📄 Resume Ranker AI", layout="wide", page_icon="🎯")

# 🎨 **Custom CSS for Branding**
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .title-text { font-size:45px; color:#00f7ff; text-shadow:0 0 20px #00f7ff; font-weight: bold; text-align: center; }
    .stDataFrame { border-radius: 10px; box-shadow: 0px 0px 15px rgba(0, 247, 255, 0.3); }
    </style>
""", unsafe_allow_html=True)

# 🚀 **Header with Mascot**
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("project images.jpeg", use_container_width=True)
    st.markdown('<p class="title-text">Resume Screening AI</p>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #b0b0b0;'>Rank resumes based on Job Descriptions instantly! 🎯</p>", unsafe_allow_html=True)

st.markdown("---")

# 📥 **Inputs Section**
c1, c2 = st.columns(2)
with c1:
    st.header("📤 Upload Resumes")
    uploaded_files = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)

with c2:
    st.header("📝 Job Description")
    job_description = st.text_area("Paste the JD here...", height=150)

# 📌 **Functions**
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = "".join([page.extract_text() or "" for page in pdf.pages])
    return text.strip()

def rank_resumes(jd, resumes):
    documents = [jd] + resumes
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()
    return cosine_similarity([vectors[0]], vectors[1:]).flatten()

def generate_tips(score):
    if score > 80: return "🔥 Excellent match! Solid profile."
    elif score > 60: return "✅ Good match! Add more JD keywords."
    else: return "⚡ Low match! Update skills section."

# 🚀 **Ranking Process**
if st.button("🚀 Start Ranking") and uploaded_files and job_description:
    resumes = [extract_text_from_pdf(file) for file in uploaded_files]
    
    with st.status("🔍 Analyzing Documents...", expanded=True) as status:
        st.write("Extracting text...")
        time.sleep(1)
        st.write("Calculating vector similarity...")
        scores = rank_resumes(job_description, resumes)
        status.update(label="✅ Analysis Complete!", state="complete")

    # Data Processing
    results_df = pd.DataFrame({
        "Resume": [file.name for file in uploaded_files],
        "Score": (scores * 100).round(2),
        "Suggestion": [generate_tips(s * 100) for s in scores]
    }).sort_values(by="Score", ascending=False)

    # 📊 **Visualization & Table**
    st.header("📊 Results")
    st.dataframe(results_df, use_container_width=True)

    # Simple Chart for extra 'Wow' factor
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    results_df.plot(kind='barh', x='Resume', y='Score', ax=ax, color='#00f7ff')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    st.pyplot(fig)

    st.balloons()
