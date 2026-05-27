import os
import shutil
import tempfile
from git import Repo

ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.go', '.cpp', '.c', '.cs', '.rb', '.php'}
MAX_FILE_SIZE = 50_000  # 50KB per file
MAX_FILES = 50

def clone_and_read(repo_url: str) -> dict:
    tmp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(repo_url, tmp_dir, depth=1)
        files = {}
        count = 0

        for root, dirs, filenames in os.walk(tmp_dir):
            dirs[:] = [d for d in dirs if d not in {
                '.git', 'node_modules', '__pycache__', 
                'venv', '.venv', 'dist', 'build'
            }]

            for filename in filenames:
                if count >= MAX_FILES:
                    break
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, tmp_dir)

                try:
                    size = os.path.getsize(filepath)
                    if size > MAX_FILE_SIZE:
                        continue
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    files[rel_path] = content
                    count += 1
                except Exception:
                    continue

        return {
            "files": files,
            "file_count": len(files),
            "repo_url": repo_url
        }

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)