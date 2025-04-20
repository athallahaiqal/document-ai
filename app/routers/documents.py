from http import HTTPStatus
from typing import Annotated

import ollama
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, database, config
from app.config import get_settings
from app.ingest import read_pdf, read_docx

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_documents(db: Session = Depends(database.get_db)):
    docs = crud.list_documents(db=db)
    return docs


class SummaryOutput(BaseModel):
    summary: str


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


@router.post("/")
async def upload_document(db: Session = Depends(database.get_db),
                          file: UploadFile = File(...)):
    """Upload a document and summarise it.

    :param db: Database session
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
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Unsupported file type: {file.filename}. Only PDF and DOCX are supported.",
            )

        crud.create_document(db=db, document_content=text, document_name=file.filename)
        return {"message": "Document created"}

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {str(e)} ",
        )


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


class AskQuestionOutput(BaseModel):
    answer: str


class AskQuestionInput(BaseModel):
    question: str


@router.post("/{document_id}/question")
async def ask_question(settings: Annotated[config.Settings, Depends(get_settings)],
                       document_id: int,
                       ask_question_input: AskQuestionInput,
                       db: Session = Depends(database.get_db),
                       ) -> AskQuestionOutput:
    """
    Ask a question about an uploaded document.

    :param db: Database session
    :param document_id: Document ID
    :param ask_question_input: Free text question
    :param settings: Settings object
    :return
    """
    try:
        document = crud.get_document(db=db, document_id=document_id)

        if document is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Document not found",
            )

        # Answer the question based on the document
        answer = answer_question(settings.model_name, ask_question_input.question, document.text_content)
        return AskQuestionOutput(answer=answer)

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {str(e)} ",
        )


@router.get("/{document_id}/summarise")
async def summarise(settings: Annotated[config.Settings, Depends(get_settings)],
                    document_id: int,
                    db: Session = Depends(database.get_db)) -> SummaryOutput:
    """Summarise an uploaded document.

    :param settings: Settings object
    :param db: Database session
    :param document_id: Document ID
    :param db: Database session
    :return:
    """
    try:
        document = crud.get_document(db=db, document_id=document_id)

        if document is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Document not found",
            )

        # Summarize the document
        summary = summarize_text(settings.model_name, document.text_content)
        return SummaryOutput(summary=summary)

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the request: {str(e)} ",
        )
