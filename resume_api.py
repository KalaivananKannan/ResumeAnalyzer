import os, re
import pandas as pd
import docx, PyPDF2
import easyocr
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

# Load dataset once
df = pd.read_csv("resumes_dataset.csv")

# Initialize EasyOCR reader (English)
reader = easyocr.Reader(['en'])

# Helper function: analyze text
def analyze_text(resume_text):
    match = df[df["name"].apply(lambda n: n.lower() in resume_text.lower())]
    if not match.empty:
        row_dict = match.iloc[0].to_dict()
        return {
            "Name": row_dict.get("name", "Unknown"),
            "Job Title": row_dict.get("job_title") or row_dict.get("designation") or "Unknown",
            "Phone": row_dict.get("phone", "Unknown"),
            "Email": row_dict.get("email", "Unknown"),
            "Location": row_dict.get("location", "Unknown"),
            "Skills": row_dict.get("skills", []),
            "Education": row_dict.get("education", "Unknown"),
            "Experience": row_dict.get("experience") or row_dict.get("work_experience") or "Unknown"
        }
    else:
        email = re.search(r'[\w\.-]+@[\w\.-]+', resume_text)
        phone = re.search(r'(\+?\d[\d\s-]{8,})', resume_text)
        lines = resume_text.splitlines()
        name = lines[0].strip() if lines else "Unknown"
        job_title = next((line for line in lines if any(word in line for word in ["Executive","Designer","Engineer"])), "Unknown")
        location = next((line for line in lines if any(loc in line for loc in ["Uttar Pradesh","Kolkata","Bengaluru","Hyderabad","Chennai"])), "Unknown")

        edu_match = re.search(r'(Education.*?)(Experience|Skills|$)', resume_text, re.S|re.I)
        exp_match = re.search(r'(Experience.*?)(Education|Skills|$)', resume_text, re.S|re.I)
        skills_match = re.search(r'(Skills.*?)(Experience|Education|$)', resume_text, re.S|re.I)

        education = edu_match.group(1).strip() if edu_match else "Unknown"
        experience = exp_match.group(1).strip() if exp_match else "Unknown"
        skills = []
        if skills_match:
            skills_text = skills_match.group(1).replace("Skills", "").strip()
            skills = [s.strip() for s in re.split(r'[,\n;]', skills_text) if s.strip()]

        return {
            "Name": name,
            "Job Title": job_title,
            "Phone": phone.group(0) if phone else "Unknown",
            "Email": email.group(0) if email else "Unknown",
            "Location": location,
            "Skills": skills,
            "Education": education,
            "Experience": experience
        }

# HTML page
html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JobFit: Resume Analyzer</title>
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body { font-family:'Open Sans',sans-serif; background:#f4f6f8; margin:0; padding:0; }
    header { background:#2c3e50; color:white; padding:20px; text-align:center; font-size:1.5em; font-weight:600; box-shadow:0 2px 6px rgba(0,0,0,0.2); }
    .container { max-width:900px; margin:30px auto; padding:20px; }
    .card { background:white; border-radius:8px; padding:20px; margin-bottom:20px; box-shadow:0 2px 6px rgba(0,0,0,0.1); }
    textarea { width:100%; height:180px; padding:12px; border-radius:6px; border:1px solid #ccc; font-size:14px; resize:vertical; }
    button { background:#3498db; color:white; padding:12px 24px; border:none; border-radius:6px; cursor:pointer; font-size:14px; margin-top:10px; }
    button:hover { background:#2980b9; }
    pre, textarea[readonly] { background:#f9fafb; padding:15px; border-radius:6px; font-size:13px; overflow-x:auto; white-space:pre-wrap; word-wrap:break-word; }
    .footer { text-align:center; padding:15px; font-size:12px; color:#777; }
  </style>
</head>
<body>
  <header>JobFit: Resume Analyzer</header>
  <div class="container">
    <div class="card">
      <h2>Paste Resume</h2>
      <textarea id="resumeInput" placeholder="Paste resume text here..."></textarea><br>
      <button onclick="analyzeResume()">Analyze Resume</button>
    </div>
    <div class="card">
      <h2>Upload Resume</h2>
      <form id="uploadForm" enctype="multipart/form-data">
        <input type="file" name="resume" accept=".pdf,.docx,.jpg,.jpeg,.png">
        <br><br>
        <button type="button" onclick="uploadResume()">Analyze Resume</button>
      </form>
    </div>
    <div class="card">
      <h2>Analysis Output</h2>
      <textarea id="output" readonly style="width:100%;height:200px;"></textarea>
    </div>
  </div>
  <div class="footer">© 2026 JobFit AI | Powered by Flask</div>
  <script>
    async function analyzeResume() {
      const resumeText = document.getElementById("resumeInput").value;
      const response = await fetch("/analyze", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ text: resumeText })
      });
      const data = await response.json();
      document.getElementById("output").textContent = JSON.stringify(data,null,4);
    }
    async function uploadResume() {
      const formData = new FormData(document.getElementById("uploadForm"));
      const response = await fetch("/upload", { method:"POST", body:formData });
      const data = await response.json();
      document.getElementById("output").textContent = JSON.stringify(data,null,4);
    }
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html_page)

@app.route("/analyze", methods=["POST"])
def analyze():
    resume_text = request.json.get("text","")
    result = analyze_text(resume_text)
    return jsonify(result)

@app.route("/upload", methods=["POST"])
def upload_resume():
    file = request.files["resume"]
    filename = secure_filename(file.filename)
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    text = ""
    if filename.endswith(".pdf"):
        reader_pdf = PyPDF2.PdfReader(filepath)
        text = " ".join([page.extract_text() or "" for page in reader_pdf.pages])
    elif filename.endswith(".docx"):
        doc = docx.Document(filepath)
        text = " ".join([para.text for para in doc.paragraphs])
    elif filename.lower().endswith((".jpg",".jpeg",".png")):
        result_ocr = reader.readtext(filepath)
        text = " ".join([res[1] for res in result_ocr])

    result = analyze_text(text)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)