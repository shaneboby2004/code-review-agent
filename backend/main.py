import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Code Review Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewRequest(BaseModel):
    repo_url: str

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/review")
async def review(req: ReviewRequest):
    if not req.repo_url.startswith("https://github.com/"):
        raise HTTPException(
            status_code=400,
            detail="Only GitHub URLs are supported."
        )

    from agent import run_agent

    async def generate():
        async for chunk in run_agent(req.repo_url):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )