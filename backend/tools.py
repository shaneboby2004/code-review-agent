from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

@tool
def analyze_code_quality(file_path: str, code: str) -> str:
    """Analyzes a code file for quality issues like complexity, bad patterns, and dead code."""
    prompt = f"""You are a senior software engineer reviewing code for quality issues.

Analyze this file: {file_path}

```
{code[:3000]}
```

Review for:
1. Code complexity — overly complex functions, deep nesting, long functions
2. Bad patterns — code duplication, magic numbers, poor naming
3. Dead code — unused variables, unreachable code, commented-out blocks
4. Maintainability — missing error handling, poor structure

Respond in this exact format:
SEVERITY: [LOW/MEDIUM/HIGH]
ISSUES:
- [issue description and line reference if possible]
SUGGESTIONS:
- [specific actionable fix]
"""
    response = llm.invoke(prompt)
    return response.content


@tool
def scan_security(file_path: str, code: str) -> str:
    """Scans a code file for security vulnerabilities."""
    prompt = f"""You are a security engineer performing a vulnerability assessment.

Analyze this file: {file_path}

```
{code[:3000]}
```

Scan for:
1. Hardcoded secrets — API keys, passwords, tokens in code
2. Injection risks — SQL injection, command injection, XSS
3. Insecure patterns — eval(), pickle, shell=True, weak crypto
4. Authentication issues — missing auth checks, insecure session handling
5. Dependency risks — importing known insecure libraries

Respond in this exact format:
SEVERITY: [LOW/MEDIUM/HIGH/CRITICAL]
VULNERABILITIES:
- [vulnerability description and location]
FIXES:
- [specific fix with code example if relevant]
"""
    response = llm.invoke(prompt)
    return response.content