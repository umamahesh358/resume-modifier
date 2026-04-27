# ATS-Crushing Resume Generator

An AI-powered tool that analyzes your current resume against a target job description, rewrites it for a perfect ATS score, and compiles a beautifully formatted LaTeX PDF along with a targeted Cover Letter.

## Prerequisites

1.  **Python 3.10+**
2.  **Node.js 18+**
3.  **API Key**: You need EITHER a **Groq API Key** (Recommended for speed/free tier) OR a **Gemini API Key**.

## Installation

### Backend Setup

1.  Navigate to the backend folder:
    `cd backend`
2.  Install dependencies:
    `pip install -r requirements.txt`
3.  Set up your Environment Variables: Create a `.env` file in the `backend/` directory. You can use Groq (which uses `llama-3.3-70b-versatile` under the hood) or Gemini (`gemini-2.5-pro`):
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    # OR
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
4.  Install the **Tectonic** compiler:
    Run the automated setup script to download and configure Tectonic for your OS:
    ```bash
    python setup_tectonic.py
    ```

### Frontend Setup

1.  Navigate to the frontend folder:
    `cd frontend`
2.  Install dependencies:
    `npm install --legacy-peer-deps`
    *(Note: Using `--legacy-peer-deps` prevents strict peer dependency issues with Next.js 15 and React 19)*

## Running the Application

1.  Start the FastAPI backend server (from the `backend/` directory):
    `uvicorn main:app --host 127.0.0.1 --port 8000 &`
2.  Start the Next.js frontend server (from the `frontend/` directory):
    `npm run dev &`
3.  Open your browser to `http://localhost:3000`.
