import os
import json
import sacrebleu

def compute_metrics(json_file_path):
    """
    Computes BLEU, chrF, chrF++, and TER scores for a given JSON file
    and updates the file with the scores.
    """
    print(f"Processing {json_file_path}...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON from {json_file_path}: {e}")
        return
    except Exception as e:
        print(f"Error opening {json_file_path}: {e}")
        return

    updated_count = 0
    for item in data:
        actual = item.get('actual')
        targets = item.get('targets')

        if actual is None or targets is None:
            continue
        
        # sacrebleu expects a list of references for each hypothesis locally, 
        # but the library functions usually take [hyp] and [[ref1, ref2]] (list of list of refs) for corpus level.
        # For sentence level:
        # sacrebleu.sentence_bleu(hypothesis: str, references: List[str])
        # sacrebleu.sentence_chrf(hypothesis: str, references: List[str], order=6, beta=2, remove_whitespace=True)
        # sacrebleu.sentence_ter(hypothesis: str, references: List[str])
        
        # Ensure actual is a string
        if not isinstance(actual, str):
            actual = str(actual)
            
        # Ensure targets is a list of strings
        if not isinstance(targets, list):
            # If it's a string, wrap it
            if isinstance(targets, str):
                targets = [targets]
            else:
                # If it's something else, try to cast or skip
                targets = [str(t) for t in targets]

        try:
            # BLEU
            bleu = sacrebleu.sentence_bleu(actual, targets)
            item['bleu_score'] = bleu.score

            # chrF (character n-gram F-score) - default is 6-grams
            chrf = sacrebleu.sentence_chrf(actual, targets)
            item['chrF_score'] = chrf.score

            # chrF++ (word n-grams included) - typically word_order=2
            chrf_plus = sacrebleu.sentence_chrf(actual, targets, word_order=2)
            item['chrF_plus_score'] = chrf_plus.score

            # TER (Translation Edit Rate)
            ter = sacrebleu.sentence_ter(actual, targets)
            item['ter_test'] = ter.score
            
            updated_count += 1
            
        except Exception as e:
            print(f"Error computing metrics for row {item.get('row', 'unknown')} in {json_file_path}: {e}")

    if updated_count > 0:
        try:
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Updated {json_file_path} with metrics for {updated_count} items.")
        except Exception as e:
            print(f"Error writing updates to {json_file_path}: {e}")
    else:
        print(f"No items updated in {json_file_path}.")

def main():
    cleaned_data_dir = 'cleaned_data'
    
    if not os.path.exists(cleaned_data_dir):
        print(f"Directory '{cleaned_data_dir}' not found.")
        return

    for root, dirs, files in os.walk(cleaned_data_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                compute_metrics(file_path)

if __name__ == "__main__":
    main()
