import json
import os
import glob
import sys

def verify_cleaning():
    data_dir = '/home/ninin/projects/Research/Data/qwen_14b/gramatical_induction/cleaned_data'
    files = glob.glob(os.path.join(data_dir, '*.json'))
    
    if not files:
        print("No JSON files found in cleaned_data!")
        return
        
    for filepath in files:
        print(f"Verifying {os.path.basename(filepath)}...")
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        for item in data:
            # Check Parenthesis Expansion
            if len(item['targets']) > 1:
                # If it wasn't a slash case (check raw), then it might be parens
                if '/' not in item['raw_target'] and len(item['targets']) > 1:
                    print(f"[Row {item['row']}] Parenthesis Expansion:")
                    print(f"  Raw: {item['raw_target']}")
                    print(f"  Clean: {item['targets']}")
                    print("-" * 20)
            
            # Check Actual Output Cleaning
            raw_len = len(item['raw_actual'])
            clean_len = len(item['actual'])
            
            # If significantly shorter, show it
            if raw_len > 0 and clean_len < raw_len * 0.5:
                print(f"[Row {item['row']}] Aggressive Cleaning of Actual:")
                print(f"  Raw: {item['raw_actual']}")
                print(f"  Clean: {item['actual']}")
                print("-" * 20)

            # Check for empty actuals where raw wasn't empty
            if not item['actual'] and item['raw_actual'].strip().replace('"""', ''):
                 print(f"[WARNING] [Row {item['row']}] Actual became empty!")
                 print(f"  Raw: {item['raw_actual']}")
                 print("-" * 20)

if __name__ == "__main__":
    verify_cleaning()
