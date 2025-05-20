from fastapi import FastAPI
from pydantic import BaseModel
from src.chains.app import app_chain

app = FastAPI()


@app.get("/healthz")
def health_check():
    return {"status": "ok", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}


class QuestionRequest(BaseModel):
    input: str


@app.post("/questions")
async def questions(request: QuestionRequest):
    result = await app_chain.ainvoke({"input": request.input})
    if hasattr(result, "model_response"):
        return {"model_response": result.model_response}
    return {"model_response": result}
