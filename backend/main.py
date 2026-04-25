from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn
import logging

from scraper import scrape_jd_url
from pdf_parser import parse_pdf_resume

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
