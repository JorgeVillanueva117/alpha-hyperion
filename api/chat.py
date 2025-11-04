from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("query", "")
    if not query:
        return JSONResponse({"error": "Missing 'query'"}, status_code=400)

    try:
        response = requests.post("https://alpha-hyperion.pinggy.io/chat", json={"query": query})
        return JSONResponse(response.json())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
