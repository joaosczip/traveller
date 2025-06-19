from fastapi import FastAPI
from pydantic import BaseModel
from src.graph.traveller import build_graph

app = FastAPI()

DEBUG = True


@app.get("/healthz")
def health_check():
    from datetime import datetime, timezone

    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


class QuestionRequest(BaseModel):
    input: str


@app.post("/questions")
async def questions(request: QuestionRequest):
    traveller_graph = build_graph().compile()

    result = traveller_graph.invoke({"trip_details": request.input})

    if DEBUG:
        print(f"Result: {result}")

    return {"model_response": result}
