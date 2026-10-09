import pandas as pd
import re
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Load your dataset once at startup
df = pd.read_csv("resumes_dataset.csv")

html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JobFit: Resume Analyzer</title>
  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Open Sans', sans-serif;
      background: #f4f6f8;
      margin: 0;
      padding: 0;
    }
    header {
      background: #2c3e50;
      color: white;
      padding: 20px;
      text-align: center;
      font-size: 1.5em;
      font-weight: 600;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .container {
      max-width: 900px;
      margin: 30px auto;
      padding: 20px;
    }
    .card {
      background: white;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    textarea {
      width: 100%;
      height: 180px;
      padding: 12px;
      border-radius: 6px;
      border: 1px solid #ccc;
      font-size: 14px;
      resize: vertical;
    }
    button {
      background: #3498db;
      color: white;
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      margin-top: 10px;
    }
    button:hover {
      background: #2980b9;
    }
    pre {
      background: #f9fafb;
      padding: 15px;
      border-radius: 6px;
      font-size: 13px;
      overflow-x: auto;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
    .footer {
      text-align: center;
      padding: 15px;
      font-size: 12px;
      color: #777;
    }
  </style>
</head>
<body>
  <header>JobFit: Resume Analyzer</header>
  <div class="container">
    <div class="card">
      <h2>Paste Resume</h2>
      <textarea id="resumeInput" placeholder="Paste resume text here..."></textarea>
      <br>
      <button onclick="analyzeResume()">Analyze Resume</button>
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
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: resumeText })
      });
      const data = await response.json();
      document.getElementById("output").textContent = JSON.stringify(data, null, 4);
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
    resume_text = request.json.get("text", "")

    # Try to match against dataset
    match = df[df["name"].apply(lambda n: n.lower() in resume_text.lower())]

    if not match.empty:
        row_dict = match.iloc[0].to_dict()  # convert row to dictionary

        # Build result dynamically, checking if each column exists
        result = {
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
    # Fallback parser for new resumes
        email = re.search(r'[\w\.-]+@[\w\.-]+', resume_text)
        phone = re.search(r'(\+?\d[\d\s-]{8,})', resume_text)
        lines = resume_text.splitlines()
        name = lines[0].strip() if lines else "Unknown"
        job_title = next((line for line in lines if "Executive" in line or "Designer" in line or "Engineer" in line), "Unknown")
        location = next((line for line in lines if any(loc in line for loc in ["Uttar Pradesh","Kolkata","Bengaluru","Hyderabad","Chennai"])), "Unknown")

    # Regex blocks for sections
        edu_match = re.search(r'(Education.*?)(Experience|Skills|$)', resume_text, re.S|re.I)
        exp_match = re.search(r'(Experience.*?)(Education|Skills|$)', resume_text, re.S|re.I)
        skills_match = re.search(r'(Skills.*?)(Experience|Education|$)', resume_text, re.S|re.I)

        education = edu_match.group(1).strip() if edu_match else "Unknown"
        experience = exp_match.group(1).strip() if exp_match else "Unknown"

    # Split skills into a list
        skills = []
        if skills_match:
            skills_text = skills_match.group(1).replace("Skills", "").strip()
            skills = [s.strip() for s in re.split(r'[,\n;]', skills_text) if s.strip()]

        result = {
            "Name": name,
            "Job Title": job_title,
            "Phone": phone.group(0) if phone else "Unknown",
            "Email": email.group(0) if email else "Unknown",
            "Location": location,
            "Skills": skills,
            "Education": education,
            "Experience": experience
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)