import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model_name = "meta/Llama-3.3-70B-Instruct"
token = 

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)


def ask_llm(query, context):

    prompt = f"""
You are a legal assistant.

Rules:
- Use ONLY the provided legal context
- Do NOT hallucinate
- Cite clauses if possible
- If answer unavailable say:
  Information not found in provided documents.

Context:
{context}

Question:
{query}
"""


    response = client.complete(
    messages=[
        SystemMessage("You are a legal assistant."),
        UserMessage(prompt),
        ],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )

    print(response.choices[0].message.content)

    return response.choices[0].message.content