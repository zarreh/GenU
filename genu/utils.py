import re
import os
from pathlib import Path

def text_clean(text):
    text = re.sub(r"\n\n+", "\n\n", text)
    text = re.sub(r"\t+", "\t", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_text_from_file(file_path):
    file_ext = Path(file_path).suffix.lower()

    if file_ext == '.pdf':
        # For PDF files
        import PyPDF2

        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
        return text

    elif file_ext in ['.docx', '.doc']:
        # For Word documents
        import docx

        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text

    else:
        return f"Unsupported file format: {file_ext}"


# # Example usage
# file_path = "your_document.pdf"  # or "your_document.docx"
# text_content = extract_text_from_file(file_path)
# print(text_content)