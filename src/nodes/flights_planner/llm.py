from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3:14b",
    temperature=0,
)
