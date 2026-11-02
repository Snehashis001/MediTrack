"""MediTrack Launcher - Starts FastAPI backend and serves static frontend."""

import os
import sys

import uvicorn

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
    import database

    database.init_db()
    print("=" * 60)
    print(" MediTrack - Premium Digital Pharmacy Web Application")
    print(" Web Programming MCA Mini-Project")
    print(" Server running at: http://127.0.0.1:8080")
    print(" API Documentation: http://127.0.0.1:8080/docs")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8080, reload=True)
