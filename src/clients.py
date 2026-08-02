import openai
from langsmith import Client, wrappers

from .config import load_config

load_config()

client = Client()
openai_client = wrappers.wrap_openai(openai.OpenAI())
