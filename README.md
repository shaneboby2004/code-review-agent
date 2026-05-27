# AI Code Review Agent

An autonomous AI agent that clones any GitHub repository, analyzes every code file for quality and security issues, and produces a structured report — all in one click.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
![React](https://img.shields.io/badge/React-Vite-purple)

## What it does

- Clones any public GitHub repo automatically
- Analyzes each file for code quality — complexity, bad patterns, dead code
- Scans for security vulnerabilities — hardcoded secrets, injection risks, insecure patterns
- Synthesizes findings into a structured report with file-by-file breakdown and top 5 priority fixes
- Streams the analysis status live to the frontend

## Tech Stack

**Backend:** Python, FastAPI, LangGraph, LangChain, Groq (Llama 3), GitPython  
**Frontend:** React, Vite

## Running Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Add a `.env` file in `/backend`:

GROQ_API_KEY=your_groq_key_here

Open `http://localhost:5173`, paste any public GitHub repo URL, and click Start Review.

## Architecture
GitHub URL → Clone repo → Filter code files → Per-file analysis (quality + security tools)
→ LLM synthesis → Streamed structured report