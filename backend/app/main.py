from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.timeline import router as timeline_router

app = FastAPI(title="Life AI MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(chat_router)
app.include_router(timeline_router)


@app.get("/health")
def health():
    return {"status": "ok"}
