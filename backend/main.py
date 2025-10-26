from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from routers import (conversationsRouter as conversations, 
                    filesRouter as files, 
                    notebookRouter as notebooks,
                    noteRouter as notes
                    )
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from config.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    collection = db["conversations"]
    indexes = await collection.index_information()
    if "expireAt_1" not in indexes:
        await collection.create_index("expireAt", expireAfterSeconds=0)
    yield
    
app = FastAPI(
    lifespan=lifespan,
    title="NoteFlow",
    version="1.0",
    description="Chatbot hỗ trợ học tập",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router, tags=["conversations"])
app.include_router(files.router, tags=["files"])
app.include_router(notebooks.router, tags=["notebooks"])
app.include_router(notes.router, tags=["notes"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)