# 📄 AI Resume Analyzer

An AI-powered resume analysis system that evaluates resumes based on skills, experience, ATS compatibility, and semantic understanding.
It helps candidates improve their resumes by providing actionable insights into strengths, weaknesses, and job readiness.

---
## 🚀 Features

- 📊 ATS Score Calculation – Evaluates how well a resume performs in Applicant Tracking Systems
- 🧠 Semantic Analysis – Understands context using NLP instead of just keyword matching
- 🏆 Skill Extraction & Matching – Identifies key skills and compares them with job requirements
- 📈 Experience Analysis – Evaluates relevance and quality of work experience
- ⚖️ Fairness Module – Reduces bias in resume evaluation
- 🔒 Anonymization – Removes personal identifiers for unbiased analysis
- 📄 Resume Parsing – Extracts structured data from resumes (PDF, DOCX, etc.)
- 🌐 Frontend Interface – Simple UI to upload and analyze resumes

---
## 🏗️ Project Structure

```text 
AI-Resume-Analyzer/
│
├── backend/
│   ├── anonymizer/
│   ├── ats/
│   ├── auth/
│   ├── core/
│   ├── experience/
│   ├── fairness/
│   ├── model/
│   ├── models/
│   ├── parser/
│   ├── routes/
│   ├── semantic/
│   ├── skills/
│   ├── utils/
│   ├── main.py
│   └── test_db.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── create_tables.py
├── requirements.txt
├── .gitignore
└── README.md

```
⚠️ Note: venv/, uploads/, and __pycache__/ are excluded via .gitignore.

---
## ⚙️ Installation & Setup
### Clone the Repository

git clone https://github.com/sapna181204/AI-Resume-Analyzer.git

cd AI-Resume-Analyzer

### Create Virtual Environment

python -m venv venv

Activate it:
Windows → venv\Scripts\activate
Mac/Linux → source venv/bin/activate

### Install Dependencies

pip install -r requirements.txt

### Setup Database

python create_tables.py

### Run Backend Server

python backend/main.py

### Run Frontend

Open in browser: frontend/index.html

---
## 🔄 Workflow
1. User uploads resume
2. Resume is parsed
3. Personal data is anonymized
4. Skills & experience are extracted
5. Semantic analysis is performed
6. ATS score is calculated
7. Final evaluation report is generated

---
## 🧠 Technologies Used
- Python
- JavaScript
- HTML, CSS
- Natural Language Processing (NLP)
- Machine Learning
- Database Systems (SQLite/MySQL/PostgreSQL)

---
## 📌 Use Cases
- Students improving resumes
- Job seekers optimizing ATS score
- Recruiters screening candidates
- Academic projects

---
## ⚠️ Limitations
- Parsing accuracy depends on resume format
- ATS scoring is an approximation of real systems
- Limited domain-specific customization

---
## 🔮 Future Improvements
- LinkedIn integration
- Advanced AI/LLM-based scoring
- Analytics dashboard
- Multi-language support
- Full deployment

---
## 🤝 Contributing

Fork → Clone → Create Branch → Commit → Push → Pull Request

---
## 📜 License

This project is intended for educational purposes.

---
## 👨‍💻 Author

Sapna

---
## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
