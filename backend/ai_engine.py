import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Configure the API client
API_KEY = os.getenv("GEMINI_API_KEY")

# The new google-genai library uses a Client object, but requires a key.
# We will initialize it lazily or provide a dummy key if not set.
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables. AI operations will fail.")

# The user requested Gemini version 3
MODEL_NAME = 'gemini-3.0-pro'

def get_generation_config(system_instruction: str):
    """Returns a config enforcing JSON output and setting system instructions."""
    return types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.2, # Low temperature for more deterministic, professional output
        system_instruction=system_instruction
    )

def safe_json_parse(text: str) -> Dict[str, Any]:
    """Safely parse JSON, stripping markdown code blocks if present."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return json.loads(text.strip())

async def analyze_ats_baseline(old_resume_text: str, scraped_jd_text: str) -> Dict[str, Any]:
    """
    Call 1: The Baseline ATS Analyzer
    Analyzes the old resume against the JD to calculate a strict ATS match score and identify missing keywords.
    """
    if not client:
        raise ValueError("API key must be set when using the Google AI API.")

    system_instruction = (
        "You are an expert Applicant Tracking System (ATS). Analyze the provided resume against the provided job description. "
        "Calculate a strict ATS match score out of 100 based on keyword density, skills alignment, and experience. "
        "Identify the exact critical keywords and skills missing from the resume. "
        "Return ONLY a JSON object with the keys: old_ats_score (integer) and missing_keywords (array of strings)."
    )

    prompt = f"### Resume Text:\n{old_resume_text}\n\n### Job Description:\n{scraped_jd_text}\n\n"

    # Use the asynchronous client wrapper
    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=get_generation_config(system_instruction)
    )

    try:
        return safe_json_parse(response.text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}\nRaw response: {response.text}")
        raise Exception(f"Failed to parse Gemini response as JSON: {e}")

async def rewrite_resume(old_resume_text: str, scraped_jd_text: str, missing_keywords: list[str]) -> Dict[str, Any]:
    """
    Call 2: The Resume Rewriter & Score Booster
    Rewrites the resume to target the JD, integrating missing keywords.
    """
    if not client:
        raise ValueError("API key must be set when using the Google AI API.")

    system_instruction = (
        "You are an elite executive resume writer. Rewrite the provided resume to perfectly target the provided job description. "
        "Naturally integrate the provided missing keywords. Quantify achievements where possible. "
        "Ensure the new resume would score a 95+ on an ATS scan. "
        "Return ONLY a JSON object mapped perfectly to a resume structure. "
        "Keys must include: professional_summary (string), skills (array of strings), and experience "
        "(array of objects containing company, title, dates, and bullet_points [array of strings]). "
        "Include a key called new_ats_score with the projected new score."
    )

    keywords_str = ", ".join(missing_keywords)
    prompt = (
        f"### Original Resume:\n{old_resume_text}\n\n"
        f"### Job Description:\n{scraped_jd_text}\n\n"
        f"### Missing Keywords to Integrate:\n{keywords_str}\n\n"
    )

    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=get_generation_config(system_instruction)
    )

    try:
        return safe_json_parse(response.text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}\nRaw response: {response.text}")
        raise Exception(f"Failed to parse Gemini response as JSON: {e}")

async def generate_cover_letter(new_resume_json: Dict[str, Any], scraped_jd_text: str) -> Dict[str, Any]:
    """
    Call 3: The Cover Letter Generator
    Generates a cover letter using the newly optimized resume and the JD.
    """
    if not client:
        raise ValueError("API key must be set when using the Google AI API.")

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

    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=get_generation_config(system_instruction)
    )

    try:
        return safe_json_parse(response.text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}\nRaw response: {response.text}")
        raise Exception(f"Failed to parse Gemini response as JSON: {e}")
