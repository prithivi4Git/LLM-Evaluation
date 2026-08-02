from .clients import openai_client

EVAL_INSTRUCTIONS = "You are an expert professor specialized in grading students' answers to questions."


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    user_content = f"""You are grading the following question:
    {inputs['question']}
    Here is the real answer:
    {reference_outputs['answer']}
    You are grading the following predicted answer:
    {outputs['response']}
    Respond with CORRECT or INCORRECT:
    Grade:
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": EVAL_INSTRUCTIONS},
            {"role": "user", "content": user_content},
        ],
    ).choices[0].message.content

    grade = response.strip().upper()
    if "INCORRECT" in grade:
        return False
    return "CORRECT" in grade


## Concisions - chekcs whether the actual output is less than 2X the length of th eexpected result.
def concision(outputs: dict, reference_outputs: dict) -> bool:
    return int(
        len(outputs["response"]) < 2 * len(reference_outputs["answer"])
    )
