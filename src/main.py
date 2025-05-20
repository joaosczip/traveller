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
    result = app_chain.invoke({"input": request.input})
    return result
