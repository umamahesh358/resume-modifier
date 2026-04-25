import httpx
from bs4 import BeautifulSoup
import re

async def scrape_jd_url(url: str) -> str:
    """
    Scrapes the text content from a given Job Description URL.
    Uses httpx to fetch the page and BeautifulSoup to parse the text.
    Handles basic bot protections by providing headers.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                script.extract()

            # Get text
            text = soup.get_text(separator=' ')

            # Clean up whitespace
            # Replace multiple spaces/newlines with a single space or newline
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r' +', ' ', text)

            return text.strip()

    except httpx.HTTPStatusError as e:
        raise Exception(f"Failed to fetch URL. HTTP Status Error: {e.response.status_code}")
    except httpx.RequestError as e:
        raise Exception(f"Failed to fetch URL. Request Error: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while scraping: {str(e)}")
