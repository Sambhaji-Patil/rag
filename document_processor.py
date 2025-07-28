import requests
import PyPDF2
import io
from typing import List

def convert_google_docs_url(url: str) -> str:
    """Convert Google Docs URL to PDF export URL"""
    if "docs.google.com" in url:
        # Extract document ID from various Google Docs URL formats
        if "/document/d/" in url:
            doc_id = url.split("/document/d/")[1].split("/")[0]
            return f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"
        elif "id=" in url:
            doc_id = url.split("id=")[1].split("&")[0]
            return f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"
        # Handle URLs like the one you provided with complex parameters
        elif "?usp=drive_link" in url or "rtpof=true" in url:
            # Extract doc ID from the full URL
            if "/d/" in url:
                doc_id = url.split("/d/")[1].split("/")[0]
                return f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"
    return url

def extract_text_from_pdf(url: str) -> List[str]:
    """Extract text from PDF URL using PyPDF2"""
    # Convert Google Docs URL to PDF export URL if needed
    pdf_url = convert_google_docs_url(url)
    
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        pdf_bytes = response.content
        pdf_file = io.BytesIO(pdf_bytes)
        
        # Use PyPDF2 to extract text
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pages = []
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            pages.append(text)
        
        if not pages or all(not page.strip() for page in pages):
            raise ValueError("No text content found in the PDF")
            
        return pages
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to download PDF from URL: {e}")
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")

def chunk_text(pages: List[str], chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """Chunk text with overlap"""
    all_text = "\n".join(pages)
    tokens = all_text.split()
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = " ".join(tokens[i:i + chunk_size])
        if len(chunk.strip()) > 0:  # Only add non-empty chunks
            chunks.append(chunk)
    return chunks
