from fastapi import Request
from fastapi.responses import JSONResponse
import requests

# Apunta a tu FastAPI local en lugar de Pinggy
LOCAL_ROUTER = "http://127.0.0.1:8000"

async def chat(request: Request):
    data = await request.json()
    query = data.get("query", "")
    try:
        res = requests.post(f"{LOCAL_ROUTER}/route", json={"query": query}, timeout=60)
        res.raise_for_status()
        return JSONResponse(res.json())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
