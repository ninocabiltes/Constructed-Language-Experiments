# Do shit here

# Model Names           EXPERIMENT_TYPE             SUBTYPES (for few_shot only)
# qwen2.5:14b           zero_shot                   WORD
# phi3:14b              few_shot                    TRANSLATION
# mistral:latest        gramatical_induction
# llama3:8b             morphological_induction
# phi3:3.8b             
# llama3.2:1b

#config here
MODEL_TO_USE = "llama3.2:1b"
EXPERIMENT_TYPE = "zero_shot"
EXPERIMENT_SUBTYPE = "WORD"
EXPERIMENT_NUMBER = "1"

import requests
import json

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

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    return response.json()["response"]


import csv
import os

if __name__ == "__main__":
    csv_file_path = "Data/qwen_14b/zero_shot/1.csv"
    
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
        # Remove quotes if they are extra (CSV reader handles standard quotes, but if they are part of string)
        # The file view showed explicit quotes inside the fields? 
        # CSV view: """Translate...""" which usually means the value is "Translate..."
        # We'll treat the value as is from DictReader.
        
        # Strip outer quotes if they exist in the content (unlikely with DictReader but good to be safe if the prompt explicitly has them stored as chars)
        if prompt.startswith('"') and prompt.endswith('"'):
             prompt = prompt[1:-1]

        if not prompt:
            continue

        print(f"\n[{i+1}/{len(rows)}] Processing Prompt: {prompt}")

        try:
            # Using llama3.2:1b as per previous code, or user default.
            response_text = run_ollama(
                model="llama3.2:1b", 
                prompt=prompt
            )
            print(f"Result: {response_text}")
            
            row["Actual Output"] = response_text
        except Exception as e:
            print(f"Error running prompt: {e}")
            row["Actual Output"] = f"ERROR: {str(e)}"

    # Write back to CSV
    with open(csv_file_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nUpdated {csv_file_path} with results.")
