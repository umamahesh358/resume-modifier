import base64
from latex_generator import generate_pdf

def test_resume():
    data = {
        "name": "Jane Developer",
        "email": "jane@example.com",
        "phone": "+1-555-123-4567",
        "linkedin_url": "https://linkedin.com/in/jane",
        "github_url": "https://github.com/jane",
        "professional_summary": "Expert dev with 10% more output & passion.",
        "skills": ["Python", "LaTeX", "C++"],
        "experience": [
            {
                "company": "Google",
                "title": "Senior Dev",
                "dates": "2020 - Present",
                "bullet_points": ["Built stuff."]
            }
        ]
    }

    print("Generating Resume...")
    pdf_b64 = generate_pdf("resume.tex.j2", data)
    print("Resume generated successfully.")

def test_cl():
    data = {
        "name": "Jane",
        "surname": "Developer",
        "email": "jane@example.com",
        "phone": "+1-555-123-4567",
        "linkedin_url": "https://linkedin.com/in/jane",
        "cover_letter_text": "I am writing to apply for the position."
    }
    print("Generating Cover Letter...")
    pdf_b64 = generate_pdf("cover_letter.tex.j2", data)
    print("Cover Letter generated successfully.")

if __name__ == "__main__":
    test_resume()
    test_cl()
