COURSES = {

    "excel": "Excel for Data Analytics - Coursera",

    "machine learning":
    "Machine Learning by Andrew Ng - Coursera",

    "deep learning":
    "Deep Learning Specialization - Coursera",

    "nlp":
    "NLP Specialization - Coursera",

    "tensorflow":
    "TensorFlow Developer Course - Udemy",

    "opencv":
    "OpenCV Bootcamp - Udemy",

    "power bi":
    "Power BI Data Analyst Course - Microsoft",

    "tableau":
    "Tableau for Beginners - Udemy",

    "flask":
    "Flask Web Development - Udemy",

    "sql":
    "SQL for Data Science - Coursera"
}


def recommend_courses(missing_skills):

    recommended = []

    for skill in missing_skills:

        if skill.lower() in COURSES:

            recommended.append({
                "skill": skill,
                "course": COURSES[skill.lower()]
            })

    return recommended