from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json

app = FastAPI(title="Eco Spa Elite | Hydra Engine")

# CORS Middleware for Vercel Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SHEET_API_URL = os.getenv("SHEET_API_URL", "https://script.google.com/macros/s/AKfycbzJ1te5UUZWk9pPwoHAXKiPgg5Y74jPtRSHXXCGXVj24QaWNWol50eELLsp50EAaz78/exec")

@app.get("/api/leads")
async def get_leads():
    """
    Fetch all leads from the Google Sheets bridge.
    """
    try:
        response = requests.get(SHEET_API_URL, timeout=10)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/leads")
async def add_lead(request: Request):
    """
    Forward incoming lead JSON to the Google Sheets bridge.
    """
    try:
        data = await request.json()
        # Payload structure: name, phone, voltage, model
        response = requests.post(SHEET_API_URL, json=data, timeout=10)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "Hydra Core Online", "bridge": SHEET_API_URL[:20] + "..."}
