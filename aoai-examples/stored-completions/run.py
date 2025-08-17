import os
from openai import AzureOpenAI

# Use API key authentication
from dotenv import load_dotenv

load_dotenv()

# if using AAD
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# token_provider = get_bearer_token_provider(
#     DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
# )

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"), # if using api key
  # azure_ad_token_provider=token_provider, # if using AAD
  api_version="2025-02-01-preview"
)

completion = client.chat.completions.create(
    
    model="gpt-4o", # replace with model deployment name
    store= True,
    metadata =  {
    "user": "admin",
    "category": "docs-test",
  },
    messages=[
    {"role": "system", "content": "Provide a clear and concise summary of the technical content, highlighting key concepts and their relationships. Focus on the main ideas and practical implications."},
    {"role": "user", "content": "Ensemble methods combine multiple machine learning models to create a more robust and accurate predictor. Common techniques include bagging (training models on random subsets of data), boosting (sequentially training models to correct previous errors), and stacking (using a meta-model to combine base model predictions). Random Forests, a popular bagging method, create multiple decision trees using random feature subsets. Gradient Boosting builds trees sequentially, with each tree focusing on correcting the errors of previous trees. These methods often achieve better performance than single models by reducing overfitting and variance while capturing different aspects of the data."}
    ]   
)

print(completion.choices[0].message)
