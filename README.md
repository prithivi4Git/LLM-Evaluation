# langsmith-chatbot-eval

A small evaluation harness that scores a simple OpenAI-powered chatbot using [LangSmith](https://smith.langchain.com/)'s evaluation framework — an LLM-as-judge **correctness** check and a rule-based **concision** check, run against a fixed Q&A dataset.

## Overview

This project exists to exercise the LangSmith evaluation workflow end-to-end:

1. A small **dataset** of question/answer pairs is created once in LangSmith (and reused on later runs).
2. A **target function** answers each question using OpenAI's `gpt-4o-mini`or `gpt-4-turbo`.
3. Two **evaluators** score every answer — one using an LLM judge, one using a simple length rule.
4. Results are published to LangSmith as an **experiment**, with a link to view them in the UI.

## Architecture

```mermaid
graph TD
    ENV[".env"] --> CONFIG["config.py<br/>load_config()"]
    CONFIG --> CLIENTS["clients.py<br/>client (LangSmith)<br/>openai_client (traced)"]

    CLIENTS --> APP["app.py<br/>my_app() / ls_target()"]
    CLIENTS --> DATASET["dataset.py<br/>DATASET_NAME<br/>create_dataset()"]
    CLIENTS --> EVALUATORS["evaluators.py<br/>correctness() / concision()"]

    APP --> RUN["run.py<br/>main()"]
    DATASET --> RUN
    EVALUATORS --> RUN

    RUN --> LS[("LangSmith backend")]
    APP --> OPENAI[("OpenAI API<br/>gpt-4o-mini")]
    EVALUATORS --> OPENAI

    MAIN["__main__.py"] --> RUN
```

## Execution flow

```mermaid
flowchart TD
    A["python -m src"] --> B["__main__.py"]
    B --> C["run.main()"]
    C --> D["create_dataset()"]
    D --> D1{"Dataset already<br/>exists in LangSmith?"}
    D1 -- yes --> E
    D1 -- no --> D2["Create dataset +<br/>add 5 Q&A examples"]
    D2 --> E["client.evaluate(ls_target, ...)"]

    E --> F["For each dataset example"]
    F --> G["ls_target(inputs)"]
    G --> H["my_app(question)"]
    H --> I["OpenAI gpt-4o-mini<br/>chat completion"]
    I --> J["response returned as<br/>{'response': ...}"]

    J --> K["correctness(inputs, outputs,<br/>reference_outputs)"]
    K --> K1["LLM judge call to<br/>gpt-4o-mini: CORRECT/INCORRECT"]

    J --> L["concision(outputs,<br/>reference_outputs)"]
    L --> L1["len(response) < 2 * len(reference)"]

    K1 --> M["Results aggregated into<br/>a LangSmith experiment"]
    L1 --> M
    M --> N["Experiment URL printed<br/>(smith.langchain.com)"]
```

## Project structure

```
langsmith-chatbot-eval/
├── pyproject.toml          # Project metadata & dependencies (uv-managed)
├── uv.lock                 # Locked dependency versions
├── .python-version         # Pins Python 3.13
├── .env                    # Local secrets (gitignored, not committed) — you create this
├── .gitignore
├── notebooks/
│   └── chat_eval_study_guide.ipynb   # Standalone notebook version of the whole pipeline, for study/reference
└── src/
    ├── __init__.py
    ├── __main__.py          # Entry point: `python -m src` → calls run.main()
    ├── config.py            # load_config(): loads .env, sets LANGSMITH_API_KEY / OPENAI_API_KEY / LANGSMITH_TRACING
    ├── clients.py            # LangSmith `client` and LangSmith-wrapped `openai_client`
    ├── app.py                # my_app(): calls gpt-4o-mini; ls_target(): LangSmith-compatible target wrapper
    ├── dataset.py             # DATASET_NAME + create_dataset(): idempotent dataset creation with 5 Q&A examples
    ├── evaluators.py          # correctness() (LLM-as-judge) and concision() (length heuristic)
    └── run.py                 # main(): creates dataset, then runs client.evaluate(...)
```

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (dependency/lockfile management)
- A [LangSmith](https://smith.langchain.com/) account and API key
- An [OpenAI](https://platform.openai.com/) API key

## Setup

1. Clone the repo and `cd` into it.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Create a `.env` file in the project root with:
   ```
   LANGSMITH_API_KEY=your-langsmith-api-key
   OPENAI_API_KEY=your-openai-api-key
   ```

## Usage

Run the evaluation from the project root:

```bash
python -m src
```

or, using `uv`:

```bash
uv run python -m src
```

**Important:** this must be run with the `-m` flag (as a module), not by pointing Python at the file directly. The `src` package uses relative imports (`from .app import ls_target`, etc.), so running `python src/run.py` or `python src/__main__.py` directly will fail with:

```
ImportError: attempted relative import with no known parent package
```

On success, the run prints a LangSmith experiment URL (`smith.langchain.com/...`) where you can view per-example results.

## Evaluators

- **`correctness`** — LLM-as-judge. Sends the predicted answer and the reference answer to `gpt-4o-mini` (temperature `0`) and asks it to grade the response as `CORRECT` or `INCORRECT`. Returns `True` only if the judge says `CORRECT`.
- **`concision`** — Rule-based. Passes if the response is shorter than twice the length of the reference answer (`len(response) < 2 * len(reference)`).

## Model comparison: gpt-4o-mini vs gpt-4-turbo

The target model is configurable via `my_app`'s `model` parameter (see `notebooks/chat_eval_study_guide.ipynb`, which runs the same dataset/evaluators against both `gpt-4o-mini` and `gpt-4-turbo` as separate LangSmith experiments — `openai-4o-mini-chatbot-*` and `openai-4-turbo-chatbot-*`).

Results from comparing the two experiments over the 5-example dataset:

| Metric | gpt-4o-mini | gpt-4-turbo |
| --- | --- | --- |
| Correctness (avg) | 0.60 | 0.60 |
| Concision (avg) | 0.40 | 0.20 |
| Latency P50 | 0.591s | 2.45s |
| Total tokens | 252 | 283 |
| Total cost | < $0.0001 | $0.0054 |

**Conclusion:** both models tie on correctness, but `gpt-4o-mini` is more concise, ~4x faster, and roughly 50x cheaper — making it the better choice for this chatbot. This is why `gpt-4o-mini` is the default (and only) model wired into `src/app.py`; `gpt-4-turbo` was evaluated as a comparison baseline in the notebook and did not justify its added latency/cost.

## Dataset

- Name: `"Simple Chatbots  Evaluation"` (as registered in LangSmith).
- Contains 5 question/answer pairs (topics: LangChain, LangSmith, OpenAI, Google, Mistral).
- `create_dataset()` is idempotent — it checks whether the dataset already exists (`client.has_dataset(...)`) and only creates it (with its 5 examples) the first time. Later runs reuse the existing dataset.

## Notebooks

`notebooks/chat_eval_study_guide.ipynb` contains a self-contained, non-modularized walkthrough of the same pipeline (loading env vars, creating the dataset, defining evaluators and the target function, running the evaluation) — useful as a study reference alongside the modular `src/` implementation.

## Viewing results

Every run of `client.evaluate(...)` prints/returns a link to the corresponding experiment in the LangSmith UI, where you can inspect each example's input, output, reference answer, and evaluator scores.
