# LLM Experiment Runner

This project runs a series of linguistic experiments on various LLMs using Ollama.

## Prerequisites

- Python 3.x
- [Ollama](https://ollama.com/) running locally (port 11434)
- Dependencies installed in `.venv`

## Usage

Use the `run_experiments.sh` script to run the full suite of experiments for a specific model.

```bash
# Run with default model (qwen2.5:14b)
./run_experiments.sh

# Run with a specific model
./run_experiments.sh "<model_name>"
```

Example:
```bash
./run_experiments.sh "llama3:8b"
```

## Supported Models

The following models are supported (configured in `experimenterrr.py`):

| Model Name | Directory Map |
| :--- | :--- |
| `qwen2.5:14b` | `Data/qwen_14b` |
| `phi3:14b` | `Data/phi3_14b` |
| `phi3:3.8b` | `Data/phi3_8b` |
| `mistral:latest` | `Data/mistral` |
| `llama3:8b` | `Data/llama3_8b` |
| `llama3.2:1b` | `Data/llama3_1b` |

## Experiment Types

The script runs the following experiments:
1.  **Zero Shot**: Word translation (Experiment 1)
2.  **Few Shot (WORD)**: Word understanding (Experiments 1-5)
3.  **Few Shot (TRANSLATION)**: Sentence translation (Experiments 1-5)
4.  **Grammatical Induction**: Grammar rule learning (Experiments 1-5)
5.  **Morphological Induction**: Morphology rule learning (Experiment 1)
