# ATS-Crushing Resume Generator

An AI-powered tool that analyzes your current resume against a target job description, rewrites it for a perfect ATS score, and compiles a beautifully formatted LaTeX PDF along with a targeted Cover Letter.

## Prerequisites

1.  **Python 3.10+**
2.  **Node.js 18+**
3.  **Gemini API Key** (Set as `GEMINI_API_KEY` in `backend/.env`)

## Installation

### Backend Setup

1.  Navigate to the backend folder:
    `cd backend`
2.  Install dependencies:
    `pip install -r requirements.txt`
3.  Download the **Tectonic** binary for LaTeX compilation. You can download the latest standalone binary for your OS from the [Tectonic Releases](https://github.com/tectonic-typesetting/tectonic/releases) page. Place the extracted `tectonic` executable directly inside the `backend/` directory.

### Frontend Setup

1.  Navigate to the frontend folder:
    `cd frontend`
2.  Install dependencies:
    `npm install`

## Running the Application

1.  Start the FastAPI backend server (from the `backend/` directory):
    `uvicorn main:app --host 127.0.0.1 --port 8000 &`
2.  Start the Next.js frontend server (from the `frontend/` directory):
    `npm run dev &`
3.  Open your browser to `http://localhost:3000`.
