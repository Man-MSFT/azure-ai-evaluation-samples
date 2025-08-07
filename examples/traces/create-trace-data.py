"""
Following instructions on https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/trace-application
with goal of creating example trace data into your Foundry project
"""

print("start")

from dotenv import load_dotenv
import os

load_dotenv()

os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"

resource_name = os.getenv("RESOURCE_NAME")
project_name = os.getenv("PROJECT_NAME")

from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

OpenAIInstrumentor().instrument()

from azure.ai.projects import AIProjectClient

from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=f"https://{resource_name}.services.ai.azure.com/api/projects/{project_name}",
)


connection_string = (
    project_client.telemetry.get_application_insights_connection_string()
)

from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(connection_string=connection_string)

print(
    "Get an authenticated Azure OpenAI client for the parent AI Services resource, and perform a chat completion operation:"
)
with project_client.get_openai_client(api_version="2024-10-21") as client:

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": "How many feet are in a mile?",
            },
        ],
    )

    # according to the tutorial, after doing this, this should show up in my traces in project view
    print(response.choices[0].message.content)
