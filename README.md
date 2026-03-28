# 📄 AI Resume Analyzer

An intelligent resume analysis system that evaluates resumes based on skills, experience, ATS compatibility, and semantic understanding. This project helps candidates improve their resumes and provides insights into strengths, weaknesses, and job readiness.

---

## 🚀 Features

### 📊 ATS Score Calculation
Evaluates resume compatibility with Applicant Tracking Systems.

### 🧠 Semantic Analysis
Understands context, not just keywords.

### 🏆 Skill Extraction & Matching
Identifies key skills and compares them with job requirements.

### 📈 Experience Analysis
Analyzes work experience relevance and quality.

### ⚖️ Fairness Module
Reduces bias in resume evaluation.

### 🔒 Anonymization
Removes personal identifiers for unbiased analysis.

### 📄 Resume Parsing
Extracts structured data from resumes (PDF, DOCX, etc.).

### 🌐 Simple Frontend Interface
Upload and analyze resumes easily.

---

## 🏗️ Project Structure

```text

AI Resume Analyzer/
│
├── backend/
│   ├── anonymizer/       # Removes personal details for fair analysis
│   ├── ats/              # ATS scoring logic
│   ├── auth/             # Authentication (if implemented)
│   ├── core/             # Core backend logic
│   ├── experience/       # Experience evaluation
│   ├── fairness/         # Bias detection & fairness checks
│   ├── model/            # ML/AI model logic
│   ├── models/           # Data models / schemas
│   ├── parser/           # Resume parsing (PDF/DOCX)
│   ├── routes/           # API endpoints
│   ├── semantic/         # NLP & semantic analysis
│   ├── skills/           # Skill extraction & matching
│   ├── utils/            # Helper functions
│   │
│   ├── __init__.py
│   ├── main.py           # Entry point of backend
│   └── test_db.py        # Database testing script
│
├── frontend/
│   ├── index.html        # Main UI
│   ├── script.js         # Frontend logic
│   └── style.css         # Styling
│
├── uploads/              # Uploaded resumes
├── venv/                 # Virtual environment
├── create_tables.py      # Database setup
├── requirements.txt      # Dependencies
└── README.md             # Project documentation

```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
git clone https://github.com/your-username/ai-resume-analyzer.git

cd ai-resume-analyzer


### 2. Create Virtual Environment
python -m venv venv

Activate it:

**Windows**
venv\Scripts\activate


**Mac/Linux**
source venv/bin/activate


### 3. Install Dependencies
pip install -r requirements.txt


### 4. Setup Database
python create_tables.py


### 5. Run Backend Server
python backend/main.py


### 6. Run Frontend

Open:
frontend/index.html


---

## 🔄 Workflow

1. User uploads resume  
2. Resume is parsed  
3. Personal data is anonymized  
4. Skills & experience are extracted  
5. Semantic analysis is performed  
6. ATS score is calculated  
7. Final report is generated  

---

## 🧠 Technologies Used

- Python  
- JavaScript  
- HTML  
- CSS  
- NLP Techniques  
- Machine Learning  
- Database (SQLite/MySQL/PostgreSQL)  

---

## 📌 Use Cases

- Students improving resumes  
- Job seekers optimizing ATS score  
- Recruiters screening candidates  
- Academic projects  

---

## ⚠️ Limitations

- Parsing accuracy may vary  
- ATS scoring is approximate  
- Limited domain-specific evaluation  

---

## 🔮 Future Improvements

- LinkedIn integration  
- Advanced AI scoring  
- Analytics dashboard  
- Multi-language support  
- Full deployment  

---

## 🤝 Contributing

Fork → Clone → Create Branch → Commit → Push → Pull Request  

---

## 📜 License

This project is for educational purposes.

---

## 👨‍💻 Author

Sapna

---

## ⭐ Acknowledgment

If you found this useful, consider giving it a star.