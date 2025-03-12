import os
import json
from azure.ai.evaluation import GroundednessEvaluator

file_name = '../../data/qa_with_context_new.jsonl'

model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY")'',
    "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    "api_version": os.environ.get("AZURE_OPENAI_API_VERSION"),
}

groundedness_eval = GroundednessEvaluator(model_config)

with open(file=file_name, mode='r') as reader:
    for line in reader:
        line = line.strip()
        a = json.loads(line)
        query_response = dict(
            query= a['query'],
            context= a['context'],
            response= a['response']
        )
        groundedness_score = groundedness_eval(
            **query_response
        )
        print(groundedness_score)
