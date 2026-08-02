from .app import ls_target
from .clients import client
from .dataset import DATASET_NAME, create_dataset
from .evaluators import concision, correctness


def main():
    create_dataset()

    return client.evaluate(
        ls_target,
        data=DATASET_NAME,
        evaluators=[correctness, concision],
        experiment_prefix="openai-4o-mini-chatbot",
    )
