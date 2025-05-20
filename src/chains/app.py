from langchain.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from .routing import routing_chain, invoke_chain
from ..models import ModelResponse

output_parser = PydanticOutputParser(pydantic_object=ModelResponse)


def to_model_response_schema(answer):
    return ModelResponse(model_response=answer)


app_chain = (
    {"classification": routing_chain, "input": lambda x: x["input"]}
    | RunnableLambda(invoke_chain)
    | RunnableLambda(to_model_response_schema)
)
