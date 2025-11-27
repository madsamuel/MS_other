import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import gradio as gr

# 1. Load config
load_dotenv()

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ["MODEL_DEPLOYMENT"]
OPENAI_API_VERSION = os.environ.get("OPENAI_API_VERSION", "2024-10-21")

# 2. Create AIProjectClient (same as the lab, just not in Cloud Shell)
project_client = AIProjectClient(
    credential=DefaultAzureCredential(
        # tweak these if you want to use specific auth flows
        exclude_environment_credential=False,
        exclude_managed_identity_credential=True,
    ),
    endpoint=PROJECT_ENDPOINT,
)

# 3. Get an authenticated AzureOpenAI client from the project
# This is the same pattern the docs and the lab use (get_openai_client). :contentReference[oaicite:7]{index=7}
openai_client = project_client.get_openai_client(
    api_version=OPENAI_API_VERSION
)


def chat_fn(message, history):
    """
    Gradio ChatInterface passes:
      - message: latest user message (str)
      - history: list of [user, assistant] pairs
    We rebuild the OpenAI-style messages list and call the model.
    """

    # Build messages with system prompt + full history
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant that answers questions.",
        }
    ]

    for user_msg, assistant_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})

    # Add current user message
    messages.append({"role": "user", "content": message})

    # Call the model via the project OpenAI client
    response = openai_client.chat.completions.create(
        model=MODEL_DEPLOYMENT,
        messages=messages,
    )

    completion = response.choices[0].message.content
    return completion


# 4. Simple Gradio UI
demo = gr.ChatInterface(
    fn=chat_fn,
    title="Azure AI Foundry Chat (local Gradio)",
    description=(
        "Chat with a model deployed in your Azure AI Foundry project, "
        "using azure-ai-projects + Gradio."
    ),
)

if __name__ == "__main__":
    demo.launch()
