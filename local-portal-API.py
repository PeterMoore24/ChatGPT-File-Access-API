# custom_gpt_file_access.py

import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pyngrok import ngrok
import uvicorn
import os.path

# The directory we want to serve
DIRECTORY_TO_SERVE = "{INSERT DIRECTORY HERE}"

# The bearer token you expect from ChatGPT or your custom GPT
# (In production, store securely in env variables/secrets manager)
EXPECTED_API_KEY = os.getenv("API_TOKEN")

app = FastAPI()

# Configure Bearer auth
bearer_scheme = HTTPBearer()

def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Validate the Authorization header using a Bearer scheme.
    e.g., Authorization: Bearer my-secret-token
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing credentials.")

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme.")

    if credentials.credentials != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")

    # If everything checks out, return True or user info
    return True

def is_within_base_dir(requested_path: str, base_dir: str) -> bool:
    return os.path.abspath(requested_path).startswith(os.path.abspath(base_dir))

@app.get("/listfiles")
def list_files(
    subdirectory: str = None,
    auth: bool = Depends(verify_bearer_token)
) -> Dict[str, Any]:
    """
    Return top-level files and subdirectories in `subdirectory`.
    If none given, uses the root DIRECTORY_TO_SERVE.
    """
    if subdirectory is None:
        abs_directory_path = DIRECTORY_TO_SERVE
    else:
        abs_directory_path = os.path.abspath(os.path.join(DIRECTORY_TO_SERVE, subdirectory))

    print(abs_directory_path)

    # # Verify the requested path is within DIRECTORY_TO_SERVE
    # if not is_within_base_dir(abs_directory_path, DIRECTORY_TO_SERVE):
    #     raise HTTPException(status_code=403, detail="Access to the requested directory is forbidden.")

    # Check if this is a real directory
    if not os.path.isdir(abs_directory_path):
        raise HTTPException(status_code=404, detail="Directory not found.")

    entries = os.listdir(abs_directory_path)
    files = []
    directories = []

    for entry in entries:
        full_path = os.path.join(abs_directory_path, entry)
        if os.path.isdir(full_path):
            directories.append(entry)
        else:
            files.append(entry)

    return {
        "requested_directory": abs_directory_path,
        "directories": directories,
        "files": files
    }

@app.get("/readfile")
def read_file(
    file_path: str,
    auth: bool = Depends(verify_bearer_token)
):
    """
    Reads and returns the content of `file_path` if it is in DIRECTORY_TO_SERVE.
    """
    abs_requested_path = os.path.abspath(os.path.join(DIRECTORY_TO_SERVE, file_path))

    print(abs_requested_path)

    # if not is_within_base_dir(abs_requested_path, DIRECTORY_TO_SERVE):
    #     raise HTTPException(status_code=403, detail="Access to the requested file is forbidden.")

    if not os.path.isfile(abs_requested_path):
        raise HTTPException(status_code=404, detail="File not found.")

    with open(abs_requested_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    return {
        "file_path": abs_requested_path,
        "content": content
    }

if __name__ == "__main__":
    # Launch ngrok tunnel on port 8000
    public_url = ngrok.connect(8000)
    print(f"Ngrok tunnel opened at {public_url}")
    print("Use the Authorization: Bearer <TOKEN> header to authenticate.")

    # Start Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
