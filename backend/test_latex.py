import base64
from latex_generator import generate_pdf, clean_data_for_latex, env

def test_resume():
    data = {
        "name": "John Doe",
        "professional_summary": "Expert dev $ with 10% more output & passion.",
        "skills": ["Python", "LaTeX", "C++"],
        "experience": [
            {
                "company": "Google",
                "title": "Senior Dev",
                "dates": "2020 - Present",
                "bullet_points": ["Built stuff.", "Escaped special characters like # and _."]
            }
        ]
    }

    print("Generating Resume...")
    pdf_b64 = generate_pdf("resume.tex.j2", data)
    print(f"Generated PDF base64 (first 50 chars): {pdf_b64[:50]}")
    with open("test_resume.pdf", "wb") as f:
        f.write(base64.b64decode(pdf_b64))

def test_cl():
    data = {
        "name": "John",
        "surname": "Doe",
        "cover_letter_text": "I am writing to apply for the position. Here is a paragraph.\n\nHere is another paragraph."
    }
    print("Generating Cover Letter...")
    pdf_b64 = generate_pdf("cover_letter.tex.j2", data)
    print(f"Generated PDF base64 (first 50 chars): {pdf_b64[:50]}")
    with open("test_cl.pdf", "wb") as f:
        f.write(base64.b64decode(pdf_b64))

if __name__ == "__main__":
    test_resume()
    test_cl()
