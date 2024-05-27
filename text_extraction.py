import docx
import time
import PyPDF2
import pandas as pd
from handle_error import log_error


def extract_text_from_pdf(file_path):
    text = ''
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        log_error(f"Failed to extract text from PDF {file_path}: {e}")
    return text

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        log_error(f"Failed to extract text from DOCX {file_path}: {e}")
        return ""

def extract_text_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.to_string()
    except Exception as e:
        log_error(f"Failed to extract text from CSV {file_path}: {e}")
        return ""

def extract_text_from_excel(file_path):
    try:
        df = pd.read_excel(file_path) 
        return df.to_string()
    except Exception as e:
        log_error(f"Failed to extract text from Excel {file_path}: {e}")
        return ""

def extract_text(file_path):
    try:
        if file_path.endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return extract_text_from_docx(file_path)
        elif file_path.endswith('.csv'):
            return extract_text_from_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return extract_text_from_excel(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
    except Exception as e:
        log_error(f"Failed to extract text from {file_path}: {e}")
        return ""


def save_text(content, file_name):
    """Saves text with unique file namex

    :param content: text content
    :param file_name: file name
    """
    timestamp = int(time.time())
    try:
        file_name = '_'.join(file_name.split('.'))
        if not len(content):
            return
        with open(f'documents/{file_name}_{timestamp}.txt', 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Text saved to documents/{file_name}_{timestamp}.txt")
    except Exception as e:
        log_error(f"Failed to save text to {file_name}: {e}")