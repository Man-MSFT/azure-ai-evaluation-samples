from dotenv import load_dotenv
import os

load_dotenv()


from openai import AzureOpenAI

endpoint = "https://mafong-1rp-resource.cognitiveservices.azure.com/"
model_name = "gpt-4o"
deployment = "gpt-4o"

subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        },
    ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model=deployment,
)

print(response.choices[0].message.content)

from azure.ai.evaluation.simulator import Simulator


async def callback(
    messages: Dict,
    stream: bool = False,
    session_state: Any = None,  # noqa: ANN401
    context: Optional[Dict[str, Any]] = None,
) -> dict:
    return {
        "messages": "hi",
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
        text="hey whats up",
        num_queries=1,  # Minimal number of queries.
    )
    return outputs


if __name__ == "__main__":
    outputs = asyncio.run(main())
    print("Simulation completed!")
    print(f"Outputs: {outputs}")
