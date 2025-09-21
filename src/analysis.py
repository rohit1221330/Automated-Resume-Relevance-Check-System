import spacy
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")


def extract_skills_from_jd(jd_text, skills_list):
    """Extracts skills from JD text using simple keyword matching."""
    found_skills = set()
    for skill in skills_list:
        if skill.lower() in jd_text.lower():
            found_skills.add(skill)
    return list(found_skills)


def calculate_hard_match_score(resume_text, required_skills):
    """Calculates a score based on how many required skills are in the resume."""
    if not required_skills:
        return 0, []

    found_skills = []
    missing_skills = []

    resume_text_lower = resume_text.lower()

    for skill in required_skills:
        if skill.lower() in resume_text_lower:
            found_skills.append(skill)
        else:
            missing_skills.append(skill)

    score = (len(found_skills) / len(required_skills)) * 100
    return score, missing_skills


def get_semantic_match_and_feedback(resume_text, jd_text, api_key):
    """
    Performs semantic analysis using an LLM and provides a score and feedback.
    """
    # 1. Initialize the LLM and Embeddings
    mbeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash-latest", google_api_key=api_key, temperature=0.2
    )

    # 2. Split documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    resume_chunks = text_splitter.split_text(resume_text)

    # 3. Create a Vector Store from resume chunks
    vector_store = Chroma.from_texts(resume_chunks, mbeddings)

    # 4. Create a prompt template for the LLM
    prompt_template = """
You are an expert HR analyst. Your task is to evaluate a resume against a job description.
Analyze the provided resume context and the job description, then answer the questions.

---
RESUME CONTEXT:
{context}
---
JOB DESCRIPTION:
{jd}
---

QUESTIONS:
1. Based on the resume, how well does the candidate fit the job description on a scale of 1 to 100? Provide only the number.
2. What are the key strengths of this candidate for this role?
3. What are the key areas for improvement or missing qualifications?
4. Provide 2-3 specific, actionable suggestions for the candidate to improve their resume for this kind of role.

Answer in the following format, and nothing else:
SCORE: [Your score from 1-100]
STRENGTHS: [Your answer]
WEAKNESSES: [Your answer]
SUGGESTIONS: [Your answer]
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "jd"])

    # 5. Set up the LangChain QA Chain
    chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

    # 6. Run the chain
    # We use the JD as the "question" to find relevant resume chunks
    response = chain(
        {
            "input_documents": vector_store.similarity_search(jd_text, k=4),
            "jd": jd_text,
        },
        return_only_outputs=True,
    )

    return response["output_text"]


def calculate_final_score(hard_match_score, semantic_score, weights=(0.5, 0.5)):
    """Calculates the final weighted score."""
    final_score = (hard_match_score * weights[0]) + (semantic_score * weights[1])
    return final_score


def get_verdict(score):
    """Provides a verdict based on the final score."""
    if score >= 80:
        return "High Suitability"
    elif score >= 60:
        return "Medium Suitability"
    else:
        return "Low Suitability"
