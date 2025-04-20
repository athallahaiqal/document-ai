import io

import PyPDF2
import docx
import ollama
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Function to read PDF file
def read_pdf(file_bytes: bytes) -> str:
    """Read a PDF file
    :param file_bytes: The file to read
    :return:
    """
    file_stream = io.BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# Function to read DOCX file
def read_docx(file):
    """Read a docx file
    :param file:
    :return:
    """
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def summarize_text(text: str) -> str:
    """Summarise the text and return it
    :param text:
    :return:
    """
    prompt = f"Summarize the following text:\n\n{text}"
    response = ollama.chat(
        model="llama3.2", messages=[{"role": "user", "content": prompt}]
    )
    return response.message.content


def answer_question(question: str, document_text: str) -> str:
    """Answer a question based on the provided file.
    :param question: Free flow question
    :param document_text: Document text
    :return:
    """
    prompt = f"Answer the following question based on the document: {document_text}\n\nQuestion: {question}\nAnswer:"
    response = ollama.chat(
        model="llama3.2", messages=[{"role": "user", "content": prompt}]
    )
    return response.message.content


class SummaryOutput(BaseModel):
    summary: str


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)) -> SummaryOutput:
    """Upload a file
    :param file
    :return:
    """
    try:
        if file.filename.endswith(".pdf"):
            file_contents = await file.read()
            text = read_pdf(file_contents)
        elif file.filename.endswith(".docx"):
            file_contents = await file.read()
            text = read_docx(file_contents)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}. Only PDF and DOCX are supported.",
            )
        # Summarize the document
        summary = summarize_text(text)
        return SummaryOutput(summary=summary)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)} ",
        )


class AnswerOutput(BaseModel):
    answer: str


@app.post("/ask/")
async def ask_question(
        question: str = Form(...), file: UploadFile = File(...)
) -> AnswerOutput:
    try:
        if file.filename.endswith(".pdf"):
            file_contents = await file.read()
            text = read_pdf(file_contents)
        elif file.filename.endswith(".docx"):
            file_contents = await file.read()
            text = read_docx(file_contents)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}. Only PDF and DOCX are supported.",
            )

        # Answer the question based on the document
        answer = answer_question(question, text)
        return AnswerOutput(answer=answer)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)} ",
        )
