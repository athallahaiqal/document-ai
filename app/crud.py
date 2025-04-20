from . import models
from sqlalchemy.orm import Session


def get_document(db: Session, document_id: int):
    """Get a document by its ID.

    :param db: Database session
    :param document_id: Document ID
    :return:
    """
    return db.query(models.Document).filter(models.Document.id == document_id).first()


def list_documents(db: Session):
    """List all documents in the database.
    :param db: Database session

    """
    return db.query(models.Document).all()


def create_document(db: Session, document_content: str, document_name: str):
    """Create a new document in the database.

    :param db: Database session
    :param document_content: Document content
    :param document_name: Document name
    :return:
    """
    db_doc = models.Document(filename=document_name, text_content=document_content)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc
