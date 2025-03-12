'''
conda activate evaluation
pip install azure-ai-evaluation
pip install azure-storage-file-datalake azure-identity
'''

import os
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient,
    DataLakeFileClient
)
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

# whatever name of file exists in OneLake
# for sake of this example, we assume that the name of the file that exists in OneLake
# is the name you want to persist to disk
file_name = 'qa_with_context_new.jsonl'

force_download = False

onelake_account_name = 'REPLACE_ME'
name = 'REPLACE_ME'

def get_service_client_token_credential(account_name) -> DataLakeServiceClient:
    # Replace guids or this entire string with the actual account URL
    account_url = f'https://{onelake_account_name}.dfs.fabric.microsoft.com/00000000-0000-0000-0000-000000000000/00000000-0000-0000-0000-000000000000'
    token_credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(account_url, credential=token_credential)
    return service_client

ol_client = get_service_client_token_credential(name)

# Files is typically the name of this folder on OneLake but change this as needed
file_client = ol_client.get_file_client("Files", file_name)

if force_download or not os.path.exists(file_name):
    with open(file=file_name, mode="wb") as local_file:
        download = file_client.download_file()
        local_file.write(download.readall())
        local_file.close()
else:
    print("file already downloaded")


model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY")'',
    "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    "api_version": os.environ.get("AZURE_OPENAI_API_VERSION"),
}


from azure.ai.evaluation import GroundednessEvaluator
import json

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
