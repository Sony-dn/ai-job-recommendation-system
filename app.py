from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

import os

from utils.parser import extract_resume_text
from utils.skills import extract_skills
from utils.recommender import recommend_jobs
from utils.courses import recommend_courses

# =========================================
# Flask App Configuration
# =========================================

app = Flask(__name__)

# Secret Key
app.config["SECRET_KEY"] = "mysecretkey"

# Upload Folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db = SQLAlchemy(app)

# =========================================
# Login Manager Setup
# =========================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


# =========================================
# User Model
# =========================================

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), nullable=False)

    password = db.Column(db.String(100), nullable=False)


# =========================================
# Resume History Model
# =========================================

class ResumeHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    filename = db.Column(db.String(200))

    resume_score = db.Column(db.Integer)

    recommended_jobs = db.Column(db.Text)


# =========================================
# User Loader
# =========================================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# =========================================
# Home Route
# =========================================

@app.route("/", methods=["GET", "POST"])
def index():

    # Default Values
    skills = []
    jobs = []
    courses = []
    resume_score = 0

    if request.method == "POST":

        # Get Uploaded File
        file = request.files.get("resume")

        if file and file.filename != "":

            # Create Upload Path
            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            # Save File
            file.save(filepath)

            # Extract Resume Text
            text = extract_resume_text(filepath)

            # Extract Skills
            skills = extract_skills(text)

            # Calculate Resume Score
            resume_score = min(len(skills) * 6, 100)

            # Recommend Jobs
            jobs = recommend_jobs(skills)

            # Collect Missing Skills
            all_missing_skills = []

            for job in jobs:

                if "missing_skills" in job:

                    all_missing_skills.extend(
                        job["missing_skills"]
                    )

            # Remove Duplicates
            all_missing_skills = list(
                set(all_missing_skills)
            )

            # Recommend Courses
            courses = recommend_courses(
                all_missing_skills
            )

            # =========================================
            # Save Upload History
            # =========================================

            job_titles = []

            for job in jobs:

                job_titles.append(
                    job["job_title"]
                )

            history = ResumeHistory(

                username=current_user.username
                if current_user.is_authenticated
                else "Guest",

                filename=file.filename,

                resume_score=resume_score,

                recommended_jobs=", ".join(job_titles)
            )

            db.session.add(history)

            db.session.commit()

    return render_template(
        "index.html",
        skills=skills,
        jobs=jobs,
        courses=courses,
        resume_score=resume_score
    )


# =========================================
# About Page Route
# =========================================

@app.route("/about")
def about():

    return render_template("about.html")


# =========================================
# Signup Route
# =========================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        # Create New User
        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)

        db.session.commit()

        return redirect(
            url_for("login")
        )

    return render_template("signup.html")


# =========================================
# Login Route
# =========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            login_user(user)

            return redirect(
                url_for("index")
            )

    return render_template("login.html")


# =========================================
# Logout Route
# =========================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# =========================================
# History Route
# =========================================

@app.route("/history")
@login_required
def history():

    user_history = ResumeHistory.query.filter_by(
        username=current_user.username
    ).all()

    return render_template(
        "history.html",
        history=user_history
    )

# =========================================
# Dashboard Route
# =========================================

@app.route("/dashboard")
@login_required
def dashboard():

    # Total Uploads
    total_uploads = ResumeHistory.query.filter_by(
        username=current_user.username
    ).count()

    # Get All User History
    user_history = ResumeHistory.query.filter_by(
        username=current_user.username
    ).all()

    # Calculate Average Score
    total_score = 0

    for item in user_history:

        total_score += item.resume_score

    average_score = 0

    if total_uploads > 0:

        average_score = round(
            total_score / total_uploads,
            2
        )

    # Latest Uploads
    latest_uploads = ResumeHistory.query.filter_by(
        username=current_user.username
    ).order_by(
        ResumeHistory.id.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        total_uploads=total_uploads,
        average_score=average_score,
        latest_uploads=latest_uploads
    )

# =========================================
# Run Application
# =========================================

if __name__ == "__main__":

    # Create Database Tables
    with app.app_context():

        db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)