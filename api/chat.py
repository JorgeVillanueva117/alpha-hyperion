import requests
from fastapi import Request
from fastapi.responses import JSONResponse

# ← PEGA TU URL DE PINGGY AQUÍ (luego)
OLLAMA_TUNNEL = "https://abc123.a.pinggy.io"

async def chat(request: Request):
    data = await request.json()
    query = data.get("query", "")
    try:
        res = requests.post(f"{OLLAMA_TUNNEL}/route", json={"query": query}, timeout=60)
        res.raise_for_status()
        return JSONResponse(res.json())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
