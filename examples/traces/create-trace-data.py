"""
Following instructions on https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/trace-application
with goal of creating example trace data into your Foundry project
"""

print("start")

from dotenv import load_dotenv
import os

load_dotenv()

# Set OpenTelemetry environment variable to capture message content
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

connection_string = project_client.telemetry.get_connection_string()

print(connection_string)

from azure.monitor.opentelemetry import configure_azure_monitor

# this line fails
# logging_formatter: Formatter = configurations[LOGGING_FORMATTER_ARG]  # type: ignore
configure_azure_monitor(connection_string=connection_string)


print("done")
