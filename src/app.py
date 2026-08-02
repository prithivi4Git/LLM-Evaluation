from .clients import openai_client

DEFAULT_INSTRUCTIONS = (
    "Respond to the users question in a short, concise manner (one short sentence)."
)


def my_app(question: str, model: str = "gpt-4o-mini", instructions: str = DEFAULT_INSTRUCTIONS) -> str:
    return openai_client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": question},
        ],
    ).choices[0].message.content


# Wrapper function that maps dataset inputs to app outputs
def ls_target(inputs: str) -> dict:
    return {"response": my_app(inputs["question"])}
