from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

# URL de tu túnel local (Pinggy)
OLLAMA_TUNNEL = "https://amicc-95-125-194-110.a.free.pinggy.link"

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("query", "")
    try:
        res = requests.post(f"{OLLAMA_TUNNEL}/route", json={"query": query}, timeout=60)
        res.raise_for_status()
        return JSONResponse(res.json())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Solo para ejecución local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
