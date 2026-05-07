from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import os
import PyPDF2

from werkzeug.utils import secure_filename

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)

app.secret_key = "industry_level_secret_key"

# ==========================================================
# UPLOAD FOLDER
# ==========================================================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ==========================================================
# ALLOWED FILE TYPES
# ==========================================================

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================================
# DEMO USER DATABASE
# ==========================================================
users = {}

# ==========================================================
# JOB DATABASE
# ==========================================================

jobs = [

    {
        "role": "AI Engineer",

        "skills": """
        python machine learning deep learning
        tensorflow pytorch nlp artificial intelligence
        """
    },

    {
        "role": "Data Scientist",

        "skills": """
        python pandas numpy statistics
        machine learning sql data visualization
        """
    },

    {
        "role": "Web Developer",

        "skills": """
        html css javascript bootstrap react flask
        """
    },

    {
        "role": "Backend Developer",

        "skills": """
        python flask django mysql api database
        """
    },

    {
        "role": "Machine Learning Engineer",

        "skills": """
        python machine learning tensorflow
        deep learning pandas numpy scikit-learn
        """
    },

    {
        "role": "Full Stack Developer",

        "skills": """
        html css javascript react node flask
        mongodb sql bootstrap
        """
    },

    {
        "role": "Data Analyst",

        "skills": """
        excel sql power bi tableau python
        analytics statistics visualization
        """
    }

]

# ==========================================================
# HOME PAGE
# ==========================================================
@app.route('/')
def home():

    return render_template('index.html')

# ==========================================================
# ABOUT PAGE
# ==========================================================

@app.route('/about')
def about():

    if 'user' not in session:

        return redirect(url_for('login'))

    return render_template('about.html')

# ==========================================================
# DASHBOARD PAGE
# ==========================================================

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", username=session["user"])
    return redirect("/login")

# ==========================================================
# HISTORY PAGE
# ==========================================================

@app.route('/history')
def history():

    if 'user' not in session:

        return redirect(url_for('login'))

    upload_history = session.get('history', [])

    return render_template(

        'history.html',
        history=upload_history

    )
# ==========================================================
# LOGIN PAGE
# ==========================================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # CHECK REGISTERED USER

        if username in users and users[username] == password:

            # SAVE SESSION

            session['user'] = username

            flash(
                "Login Successful",
                "success"
            )

            return redirect('/')

        else:

            flash(
                "Invalid Username or Password",
                "danger"
            )

            return redirect('/login')

    return render_template('login.html')

# ==========================================================
# SIGNUP PAGE
# ==========================================================

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['name']
        password = request.form['password']

        # CHECK USER EXISTS

        if username in users:

            flash(
                "Username already exists",
                "warning"
            )

            return redirect('/signup')

        # SAVE USER

        users[username] = password

        flash(
            "Signup Successful! Please Login.",
            "success"
        )

        return redirect('/login')

    return render_template('signup.html')

# ==========================================================
# FORGOT PASSWORD PAGE
# ==========================================================

@app.route('/forgot-password')
def forgot_password():

    return render_template('forgot_password.html')

# ==========================================================
# LOGOUT
# ==========================================================

@app.route('/logout')
def logout():

    session.clear()

    flash(
        "Logged out successfully",
        "info"
    )

    return redirect(url_for('login'))

# ==========================================================
# PDF TEXT EXTRACTION
# ==========================================================

def extract_text_from_pdf(pdf_path):

    text = ""

    try:

        with open(pdf_path, "rb") as file:

            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:

                extracted = page.extract_text()

                if extracted:

                    text += extracted

    except:

        text = ""

    return text.lower()

# ==========================================================
# NLP SKILL EXTRACTION
# ==========================================================

def extract_skills(resume_text):

    skill_keywords = [

        "python",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "nlp",
        "sql",
        "mysql",
        "html",
        "css",
        "javascript",
        "bootstrap",
        "react",
        "flask",
        "django",
        "pandas",
        "numpy",
        "mongodb",
        "node",
        "statistics",
        "scikit-learn",
        "excel",
        "power bi",
        "tableau"

    ]

    extracted_skills = []

    for skill in skill_keywords:

        if skill.lower() in resume_text:

            extracted_skills.append(skill)

    return extracted_skills

# ==========================================================
# TF-IDF + COSINE SIMILARITY
# ==========================================================

def recommend_jobs(resume_text, extracted_skills):

    recommended_jobs = []

    for job in jobs:

        documents = [

            resume_text,
            job["skills"]

        ]

        tfidf = TfidfVectorizer()

        tfidf_matrix = tfidf.fit_transform(documents)

        similarity = cosine_similarity(

            tfidf_matrix[0:1],
            tfidf_matrix[1:2]

        )[0][0]

        match_score = round(similarity * 100, 2)

        # ==================================================
        # MATCHED SKILLS
        # ==================================================

        matched_skills = []

        for skill in extracted_skills:

            if skill.lower() in job["skills"].lower():

                matched_skills.append(skill)

        # ==================================================
        # MISSING SKILLS
        # ==================================================

        job_skills = job["skills"].lower().split()

        missing_skills = []

        for skill in job_skills:

            if skill not in extracted_skills:

                if skill not in missing_skills:

                    missing_skills.append(skill)

        recommended_jobs.append({

            "role": job["role"],

            "score": match_score,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills[:5]

        })

    # ======================================================
    # SORT JOBS
    # ======================================================

    recommended_jobs = sorted(

        recommended_jobs,
        key=lambda x: x["score"],
        reverse=True

    )

    return recommended_jobs

# ==========================================================
# COURSE RECOMMENDATION
# ==========================================================

def recommend_courses(skills):

    courses = []

    if "python" in skills:

        courses.append(
            "Python for Data Science"
        )

    if "machine learning" in skills:

        courses.append(
            "Machine Learning Specialization"
        )

    if "deep learning" in skills:

        courses.append(
            "Deep Learning with TensorFlow"
        )

    if "html" in skills:

        courses.append(
            "Full Stack Web Development"
        )

    if "sql" in skills:

        courses.append(
            "SQL Bootcamp"
        )

    if "nlp" in skills:

        courses.append(
            "Natural Language Processing"
        )

    if "react" in skills:

        courses.append(
            "React JS Masterclass"
        )

    if "power bi" in skills:

        courses.append(
            "Power BI Dashboard Course"
        )

    return courses

# ==========================================================
# RESUME ANALYSIS ROUTE
# ==========================================================

@app.route('/predict', methods=['POST'])
def predict():

    if 'user' not in session:

        return redirect(url_for('login'))

    # ======================================================
    # CHECK FILE
    # ======================================================

    if 'resume' not in request.files:

        flash(
            "No file uploaded",
            "danger"
        )

        return redirect(url_for('home'))

    file = request.files['resume']

    if file.filename == '':

        flash(
            "Please select a file",
            "warning"
        )

        return redirect(url_for('home'))

    if not allowed_file(file.filename):

        flash(
            "Only PDF files allowed",
            "danger"
        )

        return redirect(url_for('home'))

    # ======================================================
    # SAVE FILE
    # ======================================================

    filename = secure_filename(file.filename)

    filepath = os.path.join(

        app.config['UPLOAD_FOLDER'],
        filename

    )

    file.save(filepath)

    # ======================================================
    # EXTRACT TEXT
    # ======================================================

    resume_text = extract_text_from_pdf(filepath)

    if resume_text.strip() == "":

        flash(
            "Could not extract text from PDF",
            "danger"
        )

        return redirect(url_for('home'))

    # ======================================================
    # EXTRACT SKILLS
    # ======================================================

    skills = extract_skills(resume_text)

    # ======================================================
    # JOB RECOMMENDATIONS
    # ======================================================

    recommended_jobs = recommend_jobs(

        resume_text,
        skills

    )

    # ======================================================
    # SCORE
    # ======================================================

    score = recommended_jobs[0]['score']

    # ======================================================
    # TOP ROLE
    # ======================================================

    top_role = recommended_jobs[0]['role']

    # ======================================================
    # COURSES
    # ======================================================

    recommended_courses = recommend_courses(skills)

    # ======================================================
    # SAVE HISTORY
    # ======================================================

    history_item = {

        'top_role': top_role,
        'score': score,
        'skills': skills

    }

    if 'history' not in session:

        session['history'] = []

    history = session['history']

    history.append(history_item)

    session['history'] = history

    # ======================================================
    # SUCCESS MESSAGE
    # ======================================================

    flash(
        "Resume analyzed successfully",
        "success"
    )

    # ======================================================
    # RENDER RESULT
    # ======================================================

    return render_template(

        'index.html',

        score=score,

        skills=skills,

        top_role=top_role,

        recommended_jobs=recommended_jobs,

        recommended_courses=recommended_courses

    )

# ==========================================================
# RUN APP
# ==========================================================

if __name__ == '__main__':

    app.run(debug=True)