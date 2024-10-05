from flask import Flask, request, render_template
import joblib
import sqlite3
from sqlite3 import Error
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfFileReader
from docx import Document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/govind.pdf'

# Load pre-trained model, vectorizer, and label encoder
model = joblib.load('model.pkl')
vectorizer = joblib.load('vectorizer.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Define your predefined lists
skills_list = ['python', 'java', 'sql', 'machine learning', 'deep learning', 'data analysis']

def extract_skills(resume_text):
    skills = [skill for skill in skills_list if skill.lower() in resume_text.lower()]
    return skills

def calculate_experience_score(resume_text):
    keywords = ['years of experience', 'worked for', 'experience']
    score = sum(1 for word in keywords if word in resume_text.lower())
    return min(score * 20, 100)

def calculate_education_score(resume_text):
    education_keywords = ['bachelor', 'master', 'phd', 'graduate', 'diploma']
    score = sum(1 for word in education_keywords if word in resume_text.lower())
    return min(score * 20, 100)

def create_database():
    conn = sqlite3.connect('resume_classification.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_text TEXT,
            predicted_category TEXT,
            skills TEXT,
            experience_score INTEGER,
            education_score INTEGER,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_resume_info(resume_text, category, skills, experience_score, education_score, feedback):
    try:
        conn = sqlite3.connect('resume_classification.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO resumes (resume_text, predicted_category, skills, experience_score, education_score, feedback)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (resume_text, category, ", ".join(skills), experience_score, education_score, feedback))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        conn.close()

def allowed_file(filename):
    allowed_extensions = {'pdf', 'docx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def ensure_upload_folder_exists():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['POST'])
def upload():
    feedback = request.form.get('feedback', '')
    resume_text = request.form.get('resume_text', '')

    file = request.files.get('file')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        ensure_upload_folder_exists()  # Ensure the uploads folder exists
        file.save(file_path)
        
        # Extract text from the file
        resume_text = ""

        if filename.endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PdfFileReader(f)
                resume_text = "\n".join([page.extract_text() for page in reader.pages])
        elif filename.endswith('.docx'):
            doc = Document(file_path)
            resume_text = "\n".join([para.text for para in doc.paragraphs])
        elif filename.endswith('.txt'):
            with open(file_path, 'r') as f:
                resume_text = f.read()
    elif not resume_text:
        return render_template('upload.html', message='No resume text or file provided')

    # Predict category
    resume_vec = vectorizer.transform([resume_text])
    category_encoded = model.predict(resume_vec)[0]
    category = label_encoder.inverse_transform([category_encoded])[0]

    # Calculate experience score
    experience_score = calculate_experience_score(resume_text)
    
    # Calculate education score
    education_score = calculate_education_score(resume_text)
    
    # Extract skills
    skills = extract_skills(resume_text)
    
    # Save resume information and feedback to the database
    insert_resume_info(resume_text, category, skills, experience_score, education_score, feedback)
    
    return render_template('result.html', category=category, 
                           experience_score=experience_score, 
                           education_score=education_score,
                           skills=skills,
                           feedback=feedback)

if __name__ == '__main__':
    create_database()  # Ensure the database is created when the app starts
    ensure_upload_folder_exists()  # Ensure the uploads folder exists when the app starts
    app.run(debug=True)
