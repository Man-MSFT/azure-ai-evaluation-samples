# ------- 1. Check that required environment variables are defined
import os

from dotenv import load_dotenv

load_dotenv()

assert (
    os.environ.get("AZURE_OPENAI_API_KEY") is not None
), "Please set the AZURE_OPENAI_API_KEY environment variable"
assert (
    os.environ.get("AZURE_OPENAI_ENDPOINT") is not None
), "Please set the AZURE_OPENAI_ENDPOINT environment variable"
assert (
    os.environ.get("AZURE_OPENAI_API_VERSION") is not None
), "Please set the AZURE_OPENAI_API_VERSION environment variable"
assert (
    os.environ.get("AZURE_OPENAI_DEPLOYMENT") is not None
), "Please set the AZURE_OPENAI_DEPLOYMENT environment variable"


from azure.ai.evaluation import AzureOpenAIModelConfiguration

model_config = AzureOpenAIModelConfiguration(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
)
print(model_config)


from azure.ai.evaluation.simulator import Simulator

simulator = Simulator(model_config=model_config)

import asyncio
from azure.identity import DefaultAzureCredential
import wikipedia
import os
from typing import List, Dict, Any, Optional

# Prepare the text to send to the simulator.
wiki_search_term = "Leonardo da vinci"
wiki_title = wikipedia.search(wiki_search_term)[0]
wiki_page = wikipedia.page(wiki_title)
text = wiki_page.summary[:5000]


from typing import List, Dict, Any, Optional
from openai import AzureOpenAI


async def callback(
    messages: Dict,
    stream: bool = False,
    session_state: Any = None,
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    # Get the latest message
    messages_list = messages["messages"]
    latest_message = messages_list[-1]
    query = latest_message["content"]

    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    )

    # Generate text from the index
    context = None  # generate_text_from_index(query)

    # Call the OpenAI API
    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "user",
                "content": context,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        max_tokens=800,
        temperature=0.7,
    )

    # Extract and return the response
    response = completion.choices[0].message.content

    # Format the response
    formatted_response = {
        "content": response,
        "role": "assistant",
        "context": context,
    }

    # Add the response to messages
    messages["messages"].append(formatted_response)
    return {
        "messages": messages["messages"],
        "stream": stream,
        "session_state": session_state,
        "context": context,
    }


async def main():
    azure_endpoint = os.getenv("ENDPOINT")
    azure_deployment = os.getenv("DEPLOYMENT")
    key = os.getenv("KEY")

    model_config = {
        "azure_endpoint": azure_endpoint,
        "azure_deployment": azure_deployment,
        "api_key": key,
    }
    simulator = Simulator(model_config=model_config)

    outputs = await simulator(
        target=callback,
        text=text,
        num_queries=4,  # Number of query-response pairs to generate
        max_conversation_turns=1,  # Number of conversation turns
    )
    return outputs


if __name__ == "__main__":
    outputs = asyncio.run(main())
    print("Simulation completed!")
    print(f"Outputs: {outputs}")
