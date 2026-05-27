import os
import json
import asyncio
from functools import partial
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from clone import clone_and_read
from tools import analyze_code_quality, scan_security

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering best practices and security vulnerabilities. 

You will be given a list of files from a GitHub repository. For each file, you will analyze it for:
1. Code quality issues — complexity, bad patterns, dead code, maintainability
2. Security vulnerabilities — hardcoded secrets, injection risks, insecure patterns

After analyzing all files, produce a structured report with:
- An overall severity score (LOW/MEDIUM/HIGH/CRITICAL)
- A summary of the most important findings
- File-by-file breakdown
- Top 5 priority fixes

Be specific and actionable. Reference line numbers where possible."""


async def run_agent(repo_url: str):
    loop = asyncio.get_event_loop()
    print("DEBUG: Starting run_agent", flush=True)

    yield f"data: {json.dumps({'status': 'cloning', 'message': 'Cloning repository...'})}\n\n"

    try:
        repo_data = await loop.run_in_executor(
            None,
            partial(clone_and_read, repo_url)
        )
    except Exception as e:
        yield f"data: {json.dumps({'status': 'error', 'message': f'Failed to clone repository: {str(e)}'})}\n\n"
        return

    files = repo_data["files"]
    file_count = repo_data["file_count"]
    print(f"DEBUG: Cloned {file_count} files from {repo_url}", flush=True)

    if file_count == 0:
        yield f"data: {json.dumps({'status': 'error', 'message': 'No supported code files found in repository'})}\n\n"
        return

    yield f"data: {json.dumps({'status': 'analyzing', 'message': f'Found {file_count} files. Starting analysis...'})}\n\n"

    file_results = {}

    for i, (file_path, code) in enumerate(files.items(), 1):
        print(f"DEBUG: Analyzing file {i}/{file_count}: {file_path}", flush=True)
        yield f"data: {json.dumps({'status': 'analyzing', 'message': f'Analyzing {file_path} ({i}/{file_count})...'})}\n\n"

        quality_result = await loop.run_in_executor(
            None,
            partial(analyze_code_quality.invoke, {"file_path": file_path, "code": code})
        )

        security_result = await loop.run_in_executor(
            None,
            partial(scan_security.invoke, {"file_path": file_path, "code": code})
        )

        file_results[file_path] = {
            "quality": quality_result,
            "security": security_result
        }

        await asyncio.sleep(4)

    yield f"data: {json.dumps({'status': 'synthesizing', 'message': 'Synthesizing findings...'})}\n\n"

    findings_text = ""
    for file_path, results in file_results.items():
        findings_text += f"\n\n=== {file_path} ===\n"
        findings_text += f"QUALITY:\n{results['quality']}\n"
        findings_text += f"SECURITY:\n{results['security']}\n"

    synthesis_prompt = f"""You have analyzed {file_count} files from {repo_url}.

Here are the findings:
{findings_text[:8000]}

Now produce a final structured report in this exact format:

# Code Review Report

## Overall Assessment
SEVERITY: [LOW/MEDIUM/HIGH/CRITICAL]
SUMMARY: [2-3 sentence overview of the codebase health]

## Key Statistics
- Files analyzed: {file_count}
- Critical issues: [count]
- High severity issues: [count]
- Medium severity issues: [count]

## Top 5 Priority Fixes
1. [Most critical fix needed]
2. [Second most critical]
3. [Third]
4. [Fourth]
5. [Fifth]

## File-by-File Breakdown
[For each file, one paragraph summarizing findings]

## Security Summary
[Overall security posture and main vulnerabilities found]

## Code Quality Summary
[Overall code quality assessment and main patterns found]"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=synthesis_prompt)
    ]

    yield f"data: {json.dumps({'status': 'generating', 'message': 'Generating final report...'})}\n\n"

    response = await loop.run_in_executor(
        None,
        partial(llm.invoke, messages)
    )
    report = response.content

    print("DEBUG: Yielding complete message", flush=True)
    yield f"data: {json.dumps({'status': 'complete', 'report': report, 'file_count': file_count})}\n\n"