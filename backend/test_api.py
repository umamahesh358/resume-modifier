import requests
import json
from reportlab.pdfgen import canvas
import io

BASE_URL = "http://127.0.0.1:8000"

def create_sample_pdf():
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 100, "Hello, this is a sample resume.")
    p.drawString(100, 80, "I am a Full-Stack Developer.")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def test_parse_jd():
    url = f"{BASE_URL}/api/parse-jd"
    payload = {"url": "https://example.com"}
    response = requests.post(url, json=payload)
    print("JD Parse Response:")
    print(response.status_code)
    try:
        print(response.json()['text'][:100] + "...")
    except:
        print(response.text)
    print("-" * 40)

def test_upload_resume():
    url = f"{BASE_URL}/api/upload-resume"
    pdf_buffer = create_sample_pdf()
    files = {"file": ("resume.pdf", pdf_buffer, "application/pdf")}
    response = requests.post(url, files=files)
    print("Resume Upload Response:")
    print(response.status_code)
    try:
        print(response.json())
    except:
        print(response.text)
    print("-" * 40)

if __name__ == "__main__":
    test_parse_jd()
    test_upload_resume()
