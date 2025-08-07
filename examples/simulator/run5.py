# flake8: noqa
# type: ignore

import os

from dotenv import load_dotenv

load_dotenv()


import json

# required imports
from azure.ai.evaluation.simulator import Simulator
import requests

# sample-specific imports
import wikipedia
from typing import Any, Dict, List, Optional

from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

project_scope = {
    "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
    "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
    "project_name": os.environ.get("AZURE_PROJECT_NAME"),
}

model_config = {
    "azure_endpoint": os.environ.get("AZURE_ENDPOINT"),
    "azure_deployment": os.environ.get("AZURE_DEPLOYMENT_NAME"),
}

from openai import AzureOpenAI

from typing import List, Dict, Optional, Any


def call_ollama(query: str) -> str:
    print(f"Query: {query}")
    # url = "http://localhost:11434/api/generate"
    # payload = {"model": "llama2-uncensored", "prompt": query, "stream": False}

    # response = requests.post(url, json=payload)

    # return response.json()["response"]
    return "I dont know"


async def custom_simulator_callback(
    messages: List[Dict],
    stream: bool = False,
    session_state: Any = None,
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    messages_list = messages["messages"]
    # get last message
    latest_message = messages_list[-1]
    application_input = latest_message["content"]
    context = None
    # call your endpoint or ai application here
    response = call_ollama(application_input)
    # we are formatting the response to follow the openAI chat protocol format
    message = {
        "content": response,
        "role": "assistant",
        "context": {
            "citations": None,
        },
    }
    messages["messages"].append(message)
    return {
        "messages": messages["messages"],
        "stream": stream,
        "session_state": session_state,
        "context": context,
    }


# change the subject into other terms for example
wiki_search_term = "Public gardens in the US"
wiki_title = wikipedia.search(wiki_search_term)[0]
wiki_page = wikipedia.page(wiki_title)
text = wiki_page.summary[:10000]

# a list of tasks
tasks = [
    f"I am a journalist and need to write a report about the {wiki_search_term}.",
    f"To prepare for my report, research for me the history of {wiki_search_term} thoroughly to reflect their value and meaning for us today."
    "Extract the key insights for each site, and suggest a few sites I should visit in person and perhaps interview the staff and visitors there.",
    "Summarize everything into a report with an executive summary, details about the sites of interest, and action items I need to take.",
]

print(f"Found wikipedia summary:\n{text}")
custom_simulator = Simulator(model_config=model_config)


async def main():
    outputs = await custom_simulator(
        target=custom_simulator_callback,
        text=text,
        num_queries=4,
        max_conversation_turns=4,
        tasks=tasks,
    )
    print("Outputs:")

    print(json.dumps(outputs, indent=3))

    outputs_in_eval_format = ""
    file_name = "sim_sim_sim_output.jsonl"
    for output in outputs:
        json_conv_obj = {"conversation": output}
        outputs_in_eval_format += json.dumps(json_conv_obj) + "\n"
    with open(file_name, "w") as f:
        f.write(outputs_in_eval_format)


async def conv_complete_sim():
    outputs = await custom_simulator(
        target=custom_simulator_callback,
        conversation_turns=[
            [
                "What should I know about the public gardens in the US?",
                "What about the public garden in Boston?",
            ],
            [
                "What does Nagkumar know about simulations?",
                "Tell me more",
            ],
        ],
        max_conversation_turns=3,
    )
    print("Outputs:")
    print(json.dumps(outputs, indent=3))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
    asyncio.run(conv_complete_sim())
