# backend/app/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import agents, calls

app = FastAPI(
    title="AI Voice Agent Backend",
    description="FastAPI backend for Retell AI webhooks, call triggering, and LLM post-processing.",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(agents.router, prefix="/api/v1")
app.include_router(calls.router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "AI Voice Agent Backend is running. Access /docs for API documentation."}