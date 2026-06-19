"""
main.py - Entry point for Maya AI Sales Engine

Start the server:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

    Production:
        uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
        """

from webhook.server import app  # noqa: F401

__all__ = ["app"]
