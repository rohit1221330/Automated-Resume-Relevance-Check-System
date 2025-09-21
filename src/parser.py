import fitz  # PyMuPDF
import docx

def extract_text_from_pdf(file_path):
    """Extracts text content from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return None

def extract_text_from_docx(file_path):
    """Extracts text content from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return None

def parse_document(file_path):
    """
    Parses a document (PDF or DOCX) and returns its text content.
    """
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file format: {file_path}")
        return None