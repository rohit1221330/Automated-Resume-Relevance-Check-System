import os
import re
from turtle import st
from dotenv import load_dotenv
from .parser import parse_document
from .analysis import (
    calculate_hard_match_score,
    get_semantic_match_and_feedback,
    calculate_final_score,
    get_verdict,
)
from .database import save_result
import json
from langchain_google_genai import ChatGoogleGenerativeAI


def parse_llm_response(response_text):
    """Parses the structured text response from the LLM."""
    results = {}

    # Use regex to find SCORE, STRENGTHS, WEAKNESSES, and SUGGESTIONS
    score_match = re.search(r"SCORE:\s*(\d+)", response_text)
    strengths_match = re.search(r"STRENGTHS:\s*(.*)", response_text, re.IGNORECASE)
    weaknesses_match = re.search(r"WEAKNESSES:\s*(.*)", response_text, re.IGNORECASE)
    suggestions_match = re.search(r"SUGGESTIONS:\s*(.*)", response_text, re.IGNORECASE)

    results["semantic_score"] = int(score_match.group(1)) if score_match else 0
    results["strengths"] = (
        strengths_match.group(1).strip() if strengths_match else "Not available."
    )
    results["weaknesses"] = (
        weaknesses_match.group(1).strip() if weaknesses_match else "Not available."
    )
    results["suggestions"] = (
        suggestions_match.group(1).strip() if suggestions_match else "Not available."
    )

    return results


def get_api_key():
    """
    Gets the API key from Streamlit secrets or local .env file.
    """
    # First, try to get the key from Streamlit's secrets
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]

    # If not found, fall back to the local .env file
    else:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in secrets or .env file.")
        return api_key


def process_resume(resume_path, jd_path, resume_filename, jd_filename):
    """
    The main function to process a resume against a job description.
    """
    api_key = get_api_key()


def extract_skills_with_llm(jd_text, api_key):
    """
    Uses an LLM to extract key skills from a job description.
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash-latest",
            google_api_key=api_key,
            temperature=0.0,
        )

        prompt = f"""
        Analyze the following job description and extract the most important skills.
        Return your answer as a single JSON object with one key "skills", which is a list of strings.
        Each string in the list should be a single skill. Do not include anything else in your response.

        Job Description:
        ---
        {jd_text}
        ---
        """

        response = llm.invoke(prompt)
        # The response.content is a string that we need to parse as JSON
        response_json = json.loads(response.content)

        return response_json.get("skills", [])

    except Exception as e:
        print(f"Error extracting skills with LLM: {e}")
        # Fallback to a default list if the API fails
        return [
            "Python",
            "Data Analysis",
            "Machine Learning",
            "SQL",
            "Communication",
            "Problem Solving",
        ]
