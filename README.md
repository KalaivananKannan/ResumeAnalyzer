# 📄 JobFit: Resume Analyzer

An AI‑powered Resume Analyzer built with **Flask**, **Python**, and **EasyOCR**.  
This project extracts information from resumes (PDF, DOCX, JPG/PNG, or plain text) and converts it into structured JSON for easy analysis.

---

## 🚀 Features
- Upload resumes in multiple formats: **PDF, Word, Image (JPG/PNG)**, or paste text directly.
- Extracts key details: **Name, Job Title, Email, Phone, Location, Skills, Education, Experience**.
- Uses **EasyOCR** for image‑based resumes.
- Clean web interface with **Upload Resume** and **Analyze Resume** buttons.
- JSON output displayed neatly for further processing.

---

## 🛠️ Tech Stack
- **Python** (Flask, Pandas, Regex)
- **EasyOCR** (for image text extraction)
- **python‑docx** (Word parsing)
- **PyPDF2** (PDF parsing)
- **HTML, CSS, JavaScript** (frontend UI)

---

## 📂 Project Structure
JobFit-Resume-Analyzer/
│── resume_api.py        # Main Flask app
│── resumes_dataset.csv  # Sample dataset for matching
│── uploads/             # Uploaded resumes (auto-created)
│── README.md            # Project documentation


---

## ⚡ Getting Started

   git clone https://github.com/<your-username>/JobFit-Resume-Analyzer.git
   cd JobFit-Resume-Analyzer
   pip install flask pandas python-docx PyPDF2 pillow easyocr torch torchvision
   python resume_api.py

** ✨ Demo Screenshot**
<img width="681" height="845" alt="image" src="https://github.com/user-attachments/assets/9c2d40bf-85fc-4bae-86b8-25ff90f21de7" />
