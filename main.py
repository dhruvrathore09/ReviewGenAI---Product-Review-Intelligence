"""Root entrypoint to run the FastAPI application."""

import uvicorn
from src.api.main import app

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)

