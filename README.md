# 🤖 InnoHire AI: Automated Resume Relevance Engine  

InnoHire AI is an intelligent system that automates resume screening, helping recruitment teams instantly identify the best candidates for any job role. By combining keyword analysis with advanced AI-powered contextual understanding, our tool eliminates manual effort, reduces bias, and shortens the hiring cycle.

---

## 😫 Problem  

Recruitment teams at **Innomatics Research Labs** receive thousands of resumes for each job posting. The manual screening process is:  

- **Slow** → Delays in shortlisting top talent  
- **Inconsistent** → Recruiter bias & varied interpretation of requirements  
- **Overwhelming** → More time wasted on tedious screening than mentoring candidates  

---

## ✨ Solution  

InnoHire AI transforms resume screening by automating candidate evaluation.  

- Upload **one job description** + **multiple resumes**  
- AI extracts key skills & compares resumes  
- Generates **detailed analysis & suitability score**  
- Stores everything in a **centralized dashboard**  

This helps placement teams focus on the **best candidates from day one**.  

---

## 🏆 Key Features  

- **Dynamic Skill Extraction** → AI reads the JD to identify role-specific skills  
- **Hybrid Scoring Model** → Keyword match + semantic LLM analysis  
- **Actionable Insights** → Suitability verdict (High, Medium, Low) + strengths & gaps  
- **Centralized Dashboard** → Interactive view to filter & manage candidates  

---

## ⚙️ How It Works  

1. **Upload** → Job description + resumes  
2. **JD Analysis** → AI generates required skill set dynamically  
3. **Resume Evaluation** → Hard skill match + soft contextual match  
4. **Report & Store** → Detailed evaluation reports stored in dashboard  

---

## 🛠 Tech Stack  

- **Web Framework** → Streamlit  
- **AI / NLP** → LangChain, Google Gemini, Sentence-Transformers  
- **Database** → SQLite  
- **Core Libraries** → Python, Pandas, SpaCy, PyMuPDF  

---

## 🚀 Getting Started  

### 1. Clone Repository & Install Dependencies  

```bash
git clone <your-repo-url>
cd <project-folder>
pip install -r requirements.txt
python -m spacy download en_core_web_sm```


### 2. Set Up API Key 

```Create a .env file and add:
GOOGLE_API_KEY=your_api_key_here ```

### 3. Launch the App
```streamlit run app.py```