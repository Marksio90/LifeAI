from fastapi import FastAPI
from app.api import chat, timeline

app = FastAPI(title="Life AI MVP")

app.include_router(chat.router, prefix="/chat")
app.include_router(timeline.router, prefix="/timeline")

@app.get("/health")
def health():
    return {"status": "ok"}
