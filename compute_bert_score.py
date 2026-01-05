import os
import json
import logging
from bert_score import score
import warnings

# Suppress some warnings from transformers/bert_score
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute_bert_metrics(json_file_path):
    """
    Computes BERT scores (P, R, F1) for a given JSON file
    and updates the file with the scores.
    """
    logger.info(f"Processing {json_file_path}...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading {json_file_path}: {e}")
        return

    # Collect valid entries
    entries_to_process = []
    cands = []
    refs = []
    indices = []

    for i, item in enumerate(data):
        actual = item.get('actual')
        targets = item.get('targets')

        if actual is not None and targets is not None:
            # Clean/Normalize inputs
            if not isinstance(actual, str):
                actual = str(actual)
            
            # bert_score expects a list of reference strings for each candidate
            # But the score function signature:
            # (cands: List[str], refs: List[str] or List[List[str]])
            # If we provide List[List[str]], it handles multiple references.
            
            target_list = []
            if isinstance(targets, str):
                target_list = [targets]
            elif isinstance(targets, list):
                target_list = [str(t) for t in targets]
            else:
                target_list = [str(targets)]
            
            # For BERTScore, having multiple references per candidate is supported.
            # We add to the lists
            cands.append(actual)
            refs.append(target_list)
            indices.append(i)

    if not cands:
        logger.info(f"No valid items to process in {json_file_path}")
        return

    try:
        # Compute scores
        # using default model (roberta-large for English is common, or let it decide)
        # lang='en' is usually good to specify if we know it's English, but 
        # looking at the data, it seems to involve constructed languages or definitions in English.
        # The targets are English definitions mostly.
        # I'll set lang='en' to be safe and efficient, relying on English embedding.
        P, R, F1 = score(cands, refs, lang='en', verbose=False)
        
        # Update data
        for idx, p_val, r_val, f1_val in zip(indices, P, R, F1):
            data[idx]['bert_score_p'] = float(p_val)
            data[idx]['bert_score_r'] = float(r_val)
            data[idx]['bert_score_f1'] = float(f1_val)

        # Write back
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Updated {json_file_path} with BERT scores for {len(cands)} items.")

    except Exception as e:
        logger.error(f"Error computing BERT scores for {json_file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Compute BERT scores for specified models.')
    parser.add_argument('models', nargs='*', help='List of model names (directories) to compute metrics for. If empty, computes for all.')
    args = parser.parse_args()

    cleaned_data_dir = os.path.join('/home/ninin/projects/Research', 'cleaned_data')
    
    if not os.path.exists(cleaned_data_dir):
        logger.error(f"Directory '{cleaned_data_dir}' not found.")
        return

    target_models = args.models if args.models else []
    
    if target_models:
        logger.info(f"Targeting models: {target_models}")
    else:
        logger.info("Targeting ALL models.")

    # Count files first
    files_to_process = []
    for root, dirs, files in os.walk(cleaned_data_dir):
        # Filter directories if models are specified
        rel_from_source = os.path.relpath(root, cleaned_data_dir)
        
        if rel_from_source == '.':
            if target_models:
                dirs[:] = [d for d in dirs if d in target_models]

        for file in files:
            if file.endswith('.json'):
                files_to_process.append(os.path.join(root, file))

    logger.info(f"Found {len(files_to_process)} JSON files to process.")

    for file_path in files_to_process:
        compute_bert_metrics(file_path)

if __name__ == "__main__":
    import argparse
    main()
