from pydantic import BaseModel, Field


class ModelResponse(BaseModel):
    model_response: str | dict | list = Field(description="The content of the response")


class ToolCall(BaseModel):
    id: str = Field(description="The unique identifier for the tool call")
    name: str = Field(description="The name of the tool")
    args: dict = Field(description="The arguments for the tool")
    type: str | None = "tool_call"
