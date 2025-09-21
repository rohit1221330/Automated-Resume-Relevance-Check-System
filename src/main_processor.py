import os
import re
from dotenv import load_dotenv
from .parser import parse_document
from .analysis import (
    calculate_hard_match_score,
    get_semantic_match_and_feedback,
    calculate_final_score,
    get_verdict
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

    results['semantic_score'] = int(score_match.group(1)) if score_match else 0
    results['strengths'] = strengths_match.group(1).strip() if strengths_match else "Not available."
    results['weaknesses'] = weaknesses_match.group(1).strip() if weaknesses_match else "Not available."
    results['suggestions'] = suggestions_match.group(1).strip() if suggestions_match else "Not available."
    
    return results

def process_resume(resume_path, jd_path, resume_filename, jd_filename):
    """
    The main function to process a resume against a job description.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")

    # Step 1: Parse documents
    resume_text = parse_document(resume_path)
    jd_text = parse_document(jd_path)

    if not resume_text or not jd_text:
        return {"error": "Failed to parse one or both documents."}

    # Step 2: Dynamically Extract Skills from JD
    print("Extracting key skills from JD...")
    required_skills = extract_skills_with_llm(jd_text, api_key)
    print(f"Extracted Skills: {required_skills}")
    
    # Step 3: Hard Match Analysis
    hard_match_score, missing_skills = calculate_hard_match_score(resume_text, required_skills)

    # Step 4: Semantic Match Analysis
    llm_feedback_raw = get_semantic_match_and_feedback(resume_text, jd_text, api_key)
    llm_feedback_parsed = parse_llm_response(llm_feedback_raw)
    
    # Step 5: Final Scoring and Verdict
    final_score = calculate_final_score(hard_match_score, llm_feedback_parsed['semantic_score'])
    verdict = get_verdict(final_score)

     # Step 6: Consolidate results
    results = {
        "final_score": round(final_score),
        "verdict": verdict,
        "hard_match_score": round(hard_match_score),
        "missing_skills": missing_skills,
        "semantic_match_feedback": llm_feedback_parsed
    }
    
    # Step 7: Save to database
    save_result(resume_filename, jd_filename, results) 
    
    return results


def extract_skills_with_llm(jd_text, api_key):
    """
    Uses an LLM to extract key skills from a job description.
    """
    try:
        llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", google_api_key=api_key, temperature=0.0)
        
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
            "Python", "Data Analysis", "Machine Learning", "SQL",
            "Communication", "Problem Solving"
        ]