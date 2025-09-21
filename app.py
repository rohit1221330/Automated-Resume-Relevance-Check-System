import streamlit as st
import os
from dotenv import load_dotenv
from src.main_processor import process_resume
from src.database import init_db

# --- Initialize Database ---
init_db()

# --- Page Configuration ---
st.set_page_config(
    page_title="Automated Resume Relevance Checker", page_icon="📄", layout="wide"
)

# --- Load API Key ---
load_dotenv()
# We are loading the key here to check if it exists, but it's used inside the processor
api_key = os.getenv("GOOGLE_API_KEY")

# --- UI Styling ---
st.markdown(
    """
<style>
    .stProgress > div > div > div > div {
        background-color: #17c3b2;
    }
    .st-emotion-cache-10trblm {
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Main Application ---
st.title("🤖 Automated Resume Relevance Checker")
st.write("Upload a resume and a job description to see the magic happen!")

if not api_key:
    st.error("Google API Key not found! Please add it to your .env file.")
else:
    # --- File Upload Columns ---
    col1, col2 = st.columns(2)
    with col1:
        st.header("Upload Resumes")
        resume_files = st.file_uploader(
            "Choose one or more resume files",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="resumes",
        )  # Allow multiple files

    with col2:
        st.header("Upload Job Description")
        jd_file = st.file_uploader("Choose a JD file", type=["pdf", "docx"], key="jd")

    # --- Analysis Button ---
    # app.py

if st.button("Analyze All Resumes ✨", use_container_width=True):
    if resume_files and jd_file:
        # Save the single JD file once
        os.makedirs("uploads", exist_ok=True)
        jd_path = os.path.join("uploads", jd_file.name)
        with open(jd_path, "wb") as f:
            f.write(jd_file.getbuffer())

        # Loop through each uploaded resume
        for resume_file in resume_files:
            st.markdown("---")
            st.subheader(f"📄 Analysis for: {resume_file.name}")

            with st.spinner(f"Analyzing {resume_file.name}..."):
                # Save the current resume file
                resume_path = os.path.join("uploads", resume_file.name)
                with open(resume_path, "wb") as f:
                    f.write(resume_file.getbuffer())

                # Process the documents
                results = process_resume(
                    resume_path, jd_path, resume_file.name, jd_file.name
                )

                # Clean up the resume file
                os.remove(resume_path)

            if "error" in results:
                st.error(
                    f"Could not process {resume_file.name}. Error: {results['error']}"
                )
            else:
                st.success(f"Analysis for {resume_file.name} complete!")

                # --- Display Results for the current resume ---
                score_col, verdict_col = st.columns(2)
                with score_col:
                    st.metric(
                        label="Relevance Score", value=f"{results['final_score']}%"
                    )
                    st.progress(results["final_score"])
                with verdict_col:
                    st.metric(label="Verdict", value=results["verdict"])

                # Detailed Feedback from LLM
                feedback = results["semantic_match_feedback"]
                st.markdown(f"**Key Strengths:** {feedback['strengths']}")
                st.markdown(f"**Areas for Improvement:** {feedback['weaknesses']}")
                st.markdown(f"**Actionable Suggestions:** {feedback['suggestions']}")

                # Missing Skills
                if results["missing_skills"]:
                    st.warning(
                        f"**Missing Skills:** {', '.join(results['missing_skills'])}"
                    )
                else:
                    st.info("All major required skills were found.")

        # Clean up the JD file after the loop is done
        os.remove(jd_path)
        st.markdown("---")
        st.info("✅ All resumes have been processed and saved to the dashboard.")

    else:
        st.warning("Please upload one job description and at least one resume.")
