import io
from typing import Annotated

import PyPDF2
import docx
import ollama
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from pydantic import BaseModel

from app import config
from app.config import get_settings

app = FastAPI()


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


def summarize_text(model_name: str, text: str) -> str:
    """Summarise the text and return it.
    :param model_name: The model name running locally on Ollama
    :param text: The text to summarise
    :return:
    """
    prompt = f"Summarize the following text:\n\n{text}"
    response = ollama.chat(
        model=model_name, messages=[{"role": "user", "content": prompt}]
    )
    return response.message.content


def answer_question(model_name: str, question: str, document_text: str) -> str:
    """Answer a question based on the provided file.

    :param model_name: The model name running locally on Ollama
    :param question: Free flow question
    :param document_text: Document text
    :return:
    """
    prompt = f"Answer the following question based on the document: {document_text}\n\nQuestion: {question}\nAnswer:"
    response = ollama.chat(
        model=model_name, messages=[{"role": "user", "content": prompt}]
    )
    return response.message.content


class SummaryOutput(BaseModel):
    summary: str


@app.post("/upload/")
async def upload_file(settings: Annotated[config.Settings, Depends(get_settings)],
                      file: UploadFile = File(...)) -> SummaryOutput:
    """Upload a file and summarise it.

    :param settings: Settings object
    :param file: The file to be uploaded
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
        summary = summarize_text(settings.model_name, text)
        return SummaryOutput(summary=summary)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)} ",
        )


class AnswerOutput(BaseModel):
    answer: str


@app.post("/ask/")
async def ask_question(settings: Annotated[config.Settings, Depends(get_settings)],
                       question: str = Form(...), file: UploadFile = File(...)
                       ) -> AnswerOutput:
    """
    Ask a question about the uploaded document.

    :param question: Free text question
    :param settings: Settings object
    :param file: The file to be uploaded
    :return
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

        # Answer the question based on the document
        answer = answer_question(settings.model_name, question, text)
        return AnswerOutput(answer=answer)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)} ",
        )
