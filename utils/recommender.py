import requests

# =========================================
# Adzuna API Credentials
# =========================================

APP_ID = "2e2f3bf5"

APP_KEY = "85163f0c37d5f434236ff3790f140575"


# =========================================
# Job Recommendation Function
# =========================================

def recommend_jobs(user_skills):

    query = " ".join(user_skills)

    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=6&what={query}"

    response = requests.get(url)

    data = response.json()

    recommendations = []

    jobs = data.get("results", [])

    for job in jobs:

        recommendations.append({

            "job_title": job.get("title"),

            "company": job.get("company", {}).get("display_name"),

            "location": job.get("location", {}).get("display_name"),

            "redirect_url": job.get("redirect_url"),

            "match_score": 85

        })

    return recommendations