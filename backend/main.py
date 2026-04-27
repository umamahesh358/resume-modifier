from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn
import logging

from scraper import scrape_jd_url
from pdf_parser import parse_pdf_resume
from ai_engine import analyze_ats_baseline, rewrite_resume, generate_cover_letter
from latex_generator import generate_pdf



# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ATS-Crushing Resume Generator API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDRequest(BaseModel):
    url: HttpUrl

class JDResponse(BaseModel):
    text: str

class ResumeResponse(BaseModel):
    text: str

@app.post("/api/parse-jd", response_model=JDResponse)
async def parse_jd(request: JDRequest):
    """
    Endpoint to scrape and extract text from a Job Description URL.
    """
    logger.info(f"Received request to parse JD URL: {request.url}")
    try:
        scraped_text = await scrape_jd_url(str(request.url))
        return {"text": scraped_text}
    except Exception as e:
        logger.error(f"Error scraping JD: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/upload-resume", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Endpoint to upload and parse a PDF resume.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    logger.info(f"Received resume upload: {file.filename}")

    try:
        content = await file.read()
        parsed_text = parse_pdf_resume(content)
        return {"text": parsed_text}
    except Exception as e:
        logger.error(f"Error parsing resume PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/optimize-resume")
async def optimize_resume(
    jd_url: HttpUrl = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Orchestration endpoint:
    1. Scrapes the JD URL.
    2. Parses the uploaded Resume PDF.
    3. Runs the AI Pipeline (Baseline Analysis -> Rewriting -> Cover Letter).
    """
    if resume_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # 1. & 2. Ingestion
        logger.info(f"Scraping JD from: {jd_url}")
        jd_text = await scrape_jd_url(str(jd_url))

        logger.info(f"Parsing resume: {resume_file.filename}")
        resume_bytes = await resume_file.read()
        old_resume_text = parse_pdf_resume(resume_bytes)

        # 3. AI Pipeline
        logger.info("Running Call 1: Baseline ATS Analyzer")
        baseline_analysis = await analyze_ats_baseline(old_resume_text, jd_text)
        old_ats_score = baseline_analysis.get("old_ats_score", 0)
        missing_keywords = baseline_analysis.get("missing_keywords", [])

        logger.info("Running Call 2: Resume Rewriter & Score Booster")
        new_resume_json = await rewrite_resume(old_resume_text, jd_text, missing_keywords)

        logger.info("Running Call 3: Cover Letter Generator")
        cover_letter_json = await generate_cover_letter(new_resume_json, jd_text)

        logger.info("Running Call 4: Generating LaTeX PDFs")
        resume_pdf_b64 = generate_pdf("resume.tex.j2", new_resume_json)

        # Format data for cover letter template
        full_name = new_resume_json.get("name", "Professional Candidate")
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else "Professional"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Candidate"

        cl_data = {
            "cover_letter_text": cover_letter_json.get("cover_letter_text", ""),
            "name": first_name,
            "surname": last_name,
            "email": new_resume_json.get("email", ""),
            "phone": new_resume_json.get("phone", ""),
            "linkedin_url": new_resume_json.get("linkedin_url", "")
        }
        cover_letter_pdf_b64 = generate_pdf("cover_letter.tex.j2", cl_data)

        # Return the aggregated results
        return {
            "status": "success",
            "scores": {
                "old_ats_score": old_ats_score,
                "new_ats_score": new_resume_json.get("new_ats_score", 100),
            },
            "missing_keywords_found": missing_keywords,
            "resume_pdf": resume_pdf_b64,
            "cover_letter_pdf": cover_letter_pdf_b64
        }

    except Exception as e:
        logger.error(f"Error during optimization pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
