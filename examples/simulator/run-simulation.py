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


async def main():
    azure_endpoint = os.getenv("ENDPOINT2")
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
        num_queries=1,  # Minimal number of queries.
    )
    return outputs


if __name__ == "__main__":
    outputs = asyncio.run(main())
    print("Simulation completed!")
    print(f"Outputs: {outputs}")
