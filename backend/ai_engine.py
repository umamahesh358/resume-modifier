import os
import json
from google import genai
from google.genai import types
from groq import AsyncGroq
from typing import Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Determine active AI Provider
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = None
groq_client = None

if GROQ_API_KEY:
    logger.info("Using GROQ API for AI processing.")
    groq_client = AsyncGroq(api_key=GROQ_API_KEY)
    MODEL_NAME = "llama-3.3-70b-versatile"
elif GEMINI_API_KEY:
    logger.info("Using GEMINI API for AI processing (Free Tier).")
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    MODEL_NAME = "gemini-2.0-flash"
else:
    logger.warning("Neither GROQ_API_KEY nor GEMINI_API_KEY found in environment variables. AI operations will fail.")

def safe_json_parse(text: str) -> Dict[str, Any]:
    """Safely parse JSON, stripping markdown code blocks if present."""
    if not text:
        return {}

    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())

async def run_ai_call(system_instruction: str, prompt: str) -> Dict[str, Any]:
    """Helper function to route the request to the correct AI provider and enforce JSON."""
    if groq_client:
        response = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"{system_instruction}\n\nIMPORTANT: You must return ONLY valid JSON. Do not include any explanations or markdown backticks."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_NAME,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return safe_json_parse(response.choices[0].message.content)

    elif gemini_client:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            system_instruction=system_instruction
        )
        response = await gemini_client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )
        return safe_json_parse(response.text)

    else:
        raise ValueError("No AI Provider configured. Please set GROQ_API_KEY or GEMINI_API_KEY.")


async def analyze_ats_baseline(old_resume_text: str, scraped_jd_text: str) -> Dict[str, Any]:
    """Call 1: The Baseline ATS Analyzer"""
    system_instruction = (
        "You are an expert Applicant Tracking System (ATS). Analyze the provided resume against the provided job description. "
        "Calculate a strict ATS match score out of 100 based on keyword density, skills alignment, and experience. "
        "Identify the exact critical keywords and skills missing from the resume. "
        "Return ONLY a JSON object with the keys: old_ats_score (integer) and missing_keywords (array of strings)."
    )

    prompt = f"### Resume Text:\n{old_resume_text}\n\n### Job Description:\n{scraped_jd_text}\n\n"

    try:
        return await run_ai_call(system_instruction, prompt)
    except Exception as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise

async def rewrite_resume(old_resume_text: str, scraped_jd_text: str, missing_keywords: list[str]) -> Dict[str, Any]:
    """Call 2: The Resume Rewriter & Score Booster"""
    system_instruction = (
        "You are an elite executive resume writer. Rewrite the provided resume to perfectly target the provided job description. "
        "Naturally integrate the provided missing keywords. Quantify achievements where possible. "
        "Ensure the new resume would score a 95+ on an ATS scan. "
        "IMPORTANT: You MUST extract and preserve the candidate's personal information exactly as it appears. "
        "Return ONLY a JSON object mapped perfectly to a resume structure. "
        "Keys MUST include: name (string), email (string), phone (string), linkedin_url (string, optional), "
        "github_url (string, optional), portfolio_url (string, optional), professional_summary (string), "
        "skills (array of strings), experience (array of objects containing company, title, dates, and bullet_points [array of strings]), "
        "and new_ats_score (integer)."
    )

    keywords_str = ", ".join(missing_keywords)
    prompt = (
        f"### Original Resume:\n{old_resume_text}\n\n"
        f"### Job Description:\n{scraped_jd_text}\n\n"
        f"### Missing Keywords to Integrate:\n{keywords_str}\n\n"
    )

    try:
        return await run_ai_call(system_instruction, prompt)
    except Exception as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise

async def generate_cover_letter(new_resume_json: Dict[str, Any], scraped_jd_text: str) -> Dict[str, Any]:
    """Call 3: The Cover Letter Generator"""
    system_instruction = (
        "Write a highly persuasive, professional cover letter for the provided job description, "
        "using the candidate's newly optimized resume as the source of truth. "
        "Keep it under 300 words, highly tailored to the company, and engaging. "
        "Return ONLY a JSON object with the key cover_letter_text (string broken by newline characters)."
    )

    prompt = (
        f"### Optimized Resume JSON:\n{json.dumps(new_resume_json, indent=2)}\n\n"
        f"### Job Description:\n{scraped_jd_text}\n\n"
    )

    try:
        return await run_ai_call(system_instruction, prompt)
    except Exception as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise
