from dotenv import load_dotenv
import os

load_dotenv()


from azure.ai.evaluation.simulator import Simulator

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

DEBUG = True

from azure.identity import DefaultAzureCredential

sub_id = os.getenv("SUBSCRIPTION_ID")
rg = os.getenv("RESOURCE_GROUP")
project = os.getenv("PROJECT_NAME")

azure_ai_project = {
    "subscription_id": sub_id,
    "resource_group_name": rg,
    "project_name": project,
}

azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_deployment = os.getenv("DEPLOYMENT")
key = os.getenv("KEY")

model_config = {
    "azure_endpoint": azure_endpoint,
    "azure_deployment": azure_deployment,
    # "api_key": key,
}
simulator = Simulator(model_config=model_config)
custom_simulator = simulator
tasks = [
    f"I am a journalist and need to write a report about the {wiki_search_term}.",
    f"To prepare for my report, research for me the history of {wiki_search_term} thoroughly to reflect their value and meaning for us today."
    "Extract the key insights for each site, and suggest a few sites I should visit in person and perhaps interview the staff and visitors there.",
    "Summarize everything into a report with an executive summary, details about the sites of interest, and action items I need to take.",
]


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


async def callback(
    messages: Dict,
    stream: bool = False,
    session_state: Any = None,  # noqa: ANN401
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    messages_list = messages["messages"]
    # Get the last message.
    latest_message = messages_list[-1]
    query = latest_message["content"]
    context = latest_message.get(
        "context", None
    )  # Looks for context. The default is None.
    # Call your endpoint or AI application here:
    current_dir = os.path.dirname(__file__)
    prompty_path = os.path.join(current_dir, "application.prompty")
    _flow = load_flow(source=prompty_path, model={"configuration": azure_ai_project})
    response = _flow(query=query, context=context, conversation_history=messages_list)
    # Format the response so that it follows the OpenAI chat protocol.
    formatted_response = {
        "content": response,
        "role": "assistant",
        "context": context,
    }
    messages["messages"].append(formatted_response)
    return {
        "messages": messages["messages"],
        "stream": stream,
        "session_state": session_state,
        "context": context,
    }


async def main2():
    outputs = await custom_simulator(
        target=custom_simulator_callback,
        text=text,
        num_queries=4,
        max_conversation_turns=4,
        tasks=tasks,
    )
    print("Outputs:")

    print(json.dumps(outputs, indent=3))


async def main():

    outputs = await simulator(
        target=callback,
        text=text,
        num_queries=3,  # Minimal number of queries.
    )
    return outputs


if __name__ == "__main__":
    outputs = asyncio.run(main())
    print("Simulation completed!")
    print(f"Outputs: {outputs}")
