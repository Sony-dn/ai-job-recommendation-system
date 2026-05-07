from utils.parser import extract_resume_text
from utils.skills import extract_skills
from utils.recommender import recommend_jobs

text = extract_resume_text("uploads/resume.pdf")

skills = extract_skills(text)

jobs = recommend_jobs(skills)

print("\nExtracted Skills:")
print(skills)

print("\nRecommended Jobs:\n")

for job in jobs:
    print(f"Job Role: {job['job_title']}")
    print(f"Match Score: {job['match_score']}%")
    print(f"Matched Skills: {job['matched_skills']}")
    print(f"Missing Skills: {job['missing_skills']}")
    print("-" * 40)