import re

SKILLS_DB = [
    "python", "java", "sql", "flask",
    "machine learning", "deep learning",
    "nlp", "opencv", "tensorflow",
    "html", "css", "power bi", "tableau", "mysql"
]

def extract_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS_DB:
        if skill in text:
            found.append(skill)

    return sorted(list(set(found)))