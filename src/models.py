from pydantic import BaseModel, Field


class ModelResponse(BaseModel):
    model_response: str = Field(description="The content of the response")
