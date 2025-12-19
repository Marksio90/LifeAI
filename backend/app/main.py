from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, timeline

app = FastAPI(title="Life AI MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat")
app.include_router(timeline.router, prefix="/timeline")

@app.get("/health")
def health():
    return {"status": "ok"}
