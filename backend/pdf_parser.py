import pdfplumber
import io

def parse_pdf_resume(file_bytes: bytes) -> str:
    """
    Extracts text and embedded hyperlinks from a PDF resume using pdfplumber.
    """
    try:
        text_content = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                # Extract embedded hyperlinks
                links = page.hyperlinks
                if links:
                    page_text += "\n\n[Extracted Hyperlinks from this page]:\n"
                    for link in links:
                        uri = link.get("uri")
                        if uri:
                            page_text += f"- {uri}\n"

                if page_text:
                    text_content.append(page_text)

        full_text = "\n".join(text_content)

        if not full_text.strip():
            raise Exception("No text could be extracted from the PDF. It might be an image-based PDF.")

        return full_text.strip()

    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")
