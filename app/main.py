from fastapi import FastAPI

from app.routers import documents

app = FastAPI(title="document-ai")

app.include_router(documents.router)

