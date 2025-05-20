from fastapi import FastAPI
from pydantic import BaseModel

from src.chains.app import app_chain

app = FastAPI()


@app.get("/hello")
def hello_world():
    return {"message": "Hello, world!"}


class QuestionRequest(BaseModel):
    input: str


@app.post("/questions")
async def questions(request: QuestionRequest):
    result = await app_chain.ainvoke({"input": request.input})
    if hasattr(result, "model_response"):
        return {"model_response": result.model_response}
    return {"model_response": result}
