import os
from openai import OpenAI

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        _client = OpenAI(api_key=api_key)
    return _client

def call_llm(messages, needs_stream):
    openai = get_client()
    response = openai.chat.completions.create(model="gpt-4.1-mini", messages=messages, stream=needs_stream)
    if needs_stream:
        return response
    return response.choices[0].message.content