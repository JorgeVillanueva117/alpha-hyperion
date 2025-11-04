from fastapi import FastAPI
from hyperion.core_system import AlphaHyperionSystem
import uvicorn

app = FastAPI()
system = AlphaHyperionSystem()

@app.post("/route")
def route(data: dict):
    return system.route_query(data["query"])

if __name__ == "__main__":
    print("Hyperion Router en http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
