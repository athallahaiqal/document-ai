import io

import PyPDF2
import docx


def read_pdf(file_bytes: bytes) -> str:
    """Read a PDF file.

    :param file_bytes: The file to read
    :return:
    """
    file_stream = io.BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def read_docx(file):
    """Read a docx file.

    :param file:
    :return:
    """
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text
