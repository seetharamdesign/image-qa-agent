from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

models = client.models.list()

print("\nAvailable Models:\n")

for model in models.data:
    print(model.id)
