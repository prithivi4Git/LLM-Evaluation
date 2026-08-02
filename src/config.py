import os

from dotenv import load_dotenv


def load_config() -> None:
    load_dotenv()
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    os.environ["LANGSMITH_TRACING"] = "true"
