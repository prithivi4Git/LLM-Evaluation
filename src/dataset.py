from .clients import client

DATASET_NAME = "Simple Chatbots  Evaluation"


def create_dataset() -> None:
    if client.has_dataset(dataset_name=DATASET_NAME):
        return

    dataset = client.create_dataset(DATASET_NAME)

    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {"question": "What is LangChain?"},
                "outputs": {"answer": "A framework for building LLM applications"},
            },
            {
                "inputs": {"question": "What is LangSmith?"},
                "outputs": {
                    "answer": "A platform for observing and evaluating LLM applications"
                },
            },
            {
                "inputs": {"question": "What is OpenAI?"},
                "outputs": {
                    "answer": "A company that creates Large Language Models"
                },
            },
            {
                "inputs": {"question": "What is Google?"},
                "outputs": {
                    "answer": "A technology company known for search"
                },
            },
            {
                "inputs": {"question": "What is Mistral?"},
                "outputs": {
                    "answer": "A company that creates Large Language Models"
                },
            },
        ],
    )
