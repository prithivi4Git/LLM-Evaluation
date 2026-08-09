from .app import my_app
from .clients import client
from .dataset import DATASET_NAME, create_dataset
from .evaluators import concision, correctness

MODELS = ["gpt-4o-mini", "gpt-4-turbo"]


def main():
    create_dataset()

    results = {}
    for model in MODELS:
        def ls_target(inputs: str, model: str = model) -> dict:
            return {"response": my_app(inputs["question"], model=model)}

        results[model] = client.evaluate(
            ls_target,
            data=DATASET_NAME,
            evaluators=[correctness, concision],
            experiment_prefix=f"{model}-chatbot",
        )

    return results
