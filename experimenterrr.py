# Do shit here

# Model Names           EXPERIMENT_TYPE             SUBTYPES (for few_shot only)
# qwen2.5:14b           zero_shot                   WORD
# phi3:14b              few_shot                    TRANSLATION
# mistral:latest        gramatical_induction
# llama3:8b             morphological_induction
# phi3:3.8b             
# llama3.2:1b

import argparse

# Configs will be loaded from args
MODEL_TO_USE = "qwen2.5:14b"
EXPERIMENT_TYPE = "zero_shot" 
EXPERIMENT_SUBTYPE = "WORD"
EXPERIMENT_NUMBER = "1"

import requests
import json
import csv
import os

OLLAMA_URL = "http://localhost:11434/api/generate"

def run_ollama(
    model: str,
    prompt: str,
    temperature: float = 0.0,
    max_tokens: int = 512,
):
    payload = {
        "model": model,
        "prompt": prompt,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
        "stream": False,  # IMPORTANT for experiments
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama: {e}")
        return f"ERROR: {str(e)}"


# Mappings
MODEL_DIR_MAP = {
    "qwen2.5:14b": "qwen_14b",
    "phi3:14b": "phi3_14b",
    "phi3:3.8b": "phi3_8b",
    "mistral:latest": "mistral",
    "llama3:8b": "llama3_8b",
    "llama3.2:1b": "llama3_1b",
}

SUBTYPE_DIR_MAP = {
    "WORD": "word_question",
    "TRANSLATION": "translation_question",
}

def get_csv_path(model, exp_type, subtype, number):
    model_dir = MODEL_DIR_MAP.get(model)
    if not model_dir:
        raise ValueError(f"Unknown model directory for model: {model}")

    base_path = os.path.join("Data", model_dir)
    
    if exp_type == "zero_shot":
        return os.path.join(base_path, "zero_shot", f"{number}.csv")
    elif exp_type == "few_shot":
        subtype_dir = SUBTYPE_DIR_MAP.get(subtype)
        if not subtype_dir:
             raise ValueError(f"Unknown subtype directory for subtype: {subtype}")
        return os.path.join(base_path, "few_shot", subtype_dir, f"{number}.csv")
    else:
        # Fallback for others if they follow simple structure or need more mapping
        return os.path.join(base_path, exp_type, f"{number}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLM experiments.")
    parser.add_argument("--model", type=str, default=MODEL_TO_USE, help="Model to use (e.g., qwen2.5:14b)")
    parser.add_argument("--type", type=str, default=EXPERIMENT_TYPE, help="Experiment type (e.g., zero_shot, few_shot)")
    parser.add_argument("--subtype", type=str, default=EXPERIMENT_SUBTYPE, help="Experiment subtype (e.g., WORD, TRANSLATION)")
    parser.add_argument("--number", type=str, default=EXPERIMENT_NUMBER, help="Experiment number (e.g., 1)")
    
    args = parser.parse_args()
    
    MODEL_TO_USE = args.model
    EXPERIMENT_TYPE = args.type
    EXPERIMENT_SUBTYPE = args.subtype
    EXPERIMENT_NUMBER = args.number

    try:
        csv_file_path = get_csv_path(MODEL_TO_USE, EXPERIMENT_TYPE, EXPERIMENT_SUBTYPE, EXPERIMENT_NUMBER)
    except ValueError as e:
        print(e)
        exit(1)
    
    print(f"Using Config: Model={MODEL_TO_USE}, Type={EXPERIMENT_TYPE}, Subtype={EXPERIMENT_SUBTYPE}, Number={EXPERIMENT_NUMBER}")
    print(f"Target File: {csv_file_path}")

    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: File not found at {csv_file_path}")
        exit(1)

    rows = []
    fieldnames = []

    # Read the CSV
    with open(csv_file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"Loaded {len(rows)} rows from {csv_file_path}")

    # Process each row
    for i, row in enumerate(rows):
        prompt = row.get("Prompt", "").strip()
        
        # Clean prompt quotes if necessary
        if prompt.startswith('"') and prompt.endswith('"'):
             prompt = prompt[1:-1]

        if not prompt:
            continue

        print(f"\n[{i+1}/{len(rows)}] Processing Prompt: {prompt}") # Truncate log

        response_text = run_ollama(
            model=MODEL_TO_USE, 
            prompt="""
            You must rely exclusively on the information provided in the prompt
            and our current chat history.
            Do not use any prior knowledge, world knowledge, or external
            assumptions.
            If a rule or word is not explicitly defined in the prompt, treat it as
            unknown.

            Answer as concisely as possible. Do not add any additional information
            or explanation.

            The prompt is:
            """ + prompt
        )
        print(f"Result: {response_text}") # Truncate log
        
        row["Actual Output"] = response_text

    # Write back to CSV
    with open(csv_file_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nUpdated {csv_file_path} with results.")
