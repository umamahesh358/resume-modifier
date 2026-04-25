import asyncio
from fastapi.testclient import TestClient
from main import app
import io
from reportlab.pdfgen import canvas
import ai_engine

# Need to also patch the actual app's reference to ai_engine if it's imported
# But since main.py does `from ai_engine import ...`, we need to mock at the main.py level

import main
async def mock_analyze_ats_baseline(*args, **kwargs):
    return {
        "old_ats_score": 45,
        "missing_keywords": ["React", "FastAPI", "Docker"]
    }

async def mock_rewrite_resume(*args, **kwargs):
    return {
        "professional_summary": "A highly skilled developer.",
        "skills": ["Python", "React", "FastAPI", "Docker"],
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Software Engineer",
                "dates": "2020-Present",
                "bullet_points": ["Did things with Docker."]
            }
        ],
        "new_ats_score": 98
    }

async def mock_generate_cover_letter(*args, **kwargs):
    return {
        "cover_letter_text": "Dear Hiring Manager,\n\nI am great.\n\nSincerely, Me"
    }

main.analyze_ats_baseline = mock_analyze_ats_baseline
main.rewrite_resume = mock_rewrite_resume
main.generate_cover_letter = mock_generate_cover_letter

client = TestClient(app)

def create_sample_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 100, "Hello, this is a sample resume.")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def test_optimize_endpoint():
    pdf_buffer = create_sample_pdf()

    # Needs to be sent as form data
    data = {
        "jd_url": "https://example.com"
    }
    files = {
        "resume_file": ("resume.pdf", pdf_buffer, "application/pdf")
    }

    response = client.post("/api/optimize-resume", data=data, files=files)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        res_json = response.json()
        print("Success! Orchestration output:")
        print(f"Scores: {res_json['scores']}")
        print(f"Missing Keywords Found: {res_json['missing_keywords_found']}")
        print("Pipeline works!")
    else:
        print("Failed!")
        print(response.text)

if __name__ == "__main__":
    test_optimize_endpoint()
