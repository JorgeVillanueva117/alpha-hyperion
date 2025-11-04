import requests
from fastapi import Request
from fastapi.responses import JSONResponse

ROUTER_URL = "https://mi-router-publico.com/route"

async def chat(request: Request):
    data = await request.json()
    query = data.get("query", "")
    
    try:
        res = requests.post(f"{ROUTER_URL}", json={"query": query}, timeout=30)
        res.raise_for_status()
        return JSONResponse(res.json())
    except requests.Timeout:
        return JSONResponse({"error": "El Router no respondió a tiempo."}, status_code=504)
    except requests.RequestException as e:
        return JSONResponse({"error": "Error conectando con el Router."}, status_code=503)
