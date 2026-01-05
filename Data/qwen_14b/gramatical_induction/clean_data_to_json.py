import csv
import json
import os
import glob
import re
import itertools

def expand_parentheses(text):
    """
    Expands text with parentheses like "(A) B" into ["A B", "B"].
    """
    pattern = r'\(([^()]+)\)'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return [text]
    
    all_segments = []
    last_end = 0
    for match in matches:
        start, end = match.span()
        all_segments.append([text[last_end:start]])
        
        content = match.group(1)
        
        # Heuristic: If content looks like an explanation (contains +, =, vs, or is very long?), 
        # treat it as PURELY removed in one variant, and maybe kept in another?
        # Actually, "Adult student (adult + school-person)" -> we probably just want "Adult student".
        # The explanation is likely not part of the target translation we want to score against.
        # But maybe we keep it just in case? 
        # User said: "parenthesis to properly address what was implied".
        # "In order to ensure (it)" -> "In order to ensure it" is good.
        # "Adult student (adult + school-person)" -> "Adult student" is good.
        
        is_explanation = any(x in content for x in ['+', '=', 'vs.', 'vs '])
        
        if is_explanation:
            # If explanation, strictly remove it? Or keep it as optional?
            # If we keep it as optional, we get "Adult student" and "Adult student (adult + school-person)".
            # The latter might be noisy. Let's try to keep both for safety, but maybe clean the explanation one?
            # Actually, `expand_parentheses` returns the expanded string.
            # If we pass `content` and `""`, we get "Adult student adult + school-person" (missing parens).
            # We probably want to keep the parens if we include it?
            # Current logic strips parens when including content.
            # If it's an explanation, let's skip it (only "")?
            # Wait, `(Many) people` -> `Many people` (no parens).
            # `(adult + school-person)` -> `adult + school-person`.
            # If I exclude it, I get `Adult student`.
            # I think for scoring, we want the cleanest output. "Adult student" is better.
            # So if explanation, force empty?
            if is_explanation:
                all_segments.append([""]) 
            else:
                all_segments.append([content, ""])
        else:
             all_segments.append([content, ""])
             
        last_end = end
    all_segments.append([text[last_end:]])
    
    results = set()
    for combination in itertools.product(*all_segments):
        full_str = "".join(combination)
        # Normalize whitespace
        full_str = re.sub(r'\s+', ' ', full_str).strip()
        # Clean punctuation artifacts like " ." -> "."
        full_str = full_str.replace(' .', '.').replace(' ,', ',').replace(' ?', '?').replace(' !', '!')
        if full_str:
            results.add(full_str)
            
    return list(results)

def clean_target(target_raw):
    # Remove outer quotes
    cleaned = target_raw.replace('"""', '').replace('"', '').strip()
    if cleaned.lower().startswith('target output:'):
        cleaned = cleaned[len('target output:'):].strip()
        
    # Split by slash
    alternatives = [x.strip() for x in cleaned.split('/') if x.strip()]
    
    final_targets = []
    for alt in alternatives:
        # Expand parens
        expanded = expand_parentheses(alt)
        final_targets.extend(expanded)
        
    # Remove duplicates and empty strings
    return sorted(list(set([t for t in final_targets if t])))

def clean_actual(actual_raw):
    cleaned = actual_raw.replace('"""', '').replace('"', '').strip()
    
    # Markers to look for
    markers = ['Translation:', 'Answer:', 'Target Output:']
    
    # Lowercase check
    lower_cleaned = cleaned.lower()
    
    best_candidate = cleaned
    
    # Priority: Translation:
    if 'translation:' in lower_cleaned:
        idx = lower_cleaned.find('translation:')
        candidate = cleaned[idx + len('translation:'):].strip()
        # If result is not empty, take it
        if candidate:
            best_candidate = candidate
            
    # Check for "Yes, ..." pattern which is common conversational filler
    # If starts with "Yes," or "No," or "The sentence is grammatical"
    # We want to remove that part if there is a translation part.
    # If we already extracted translation, we are good.
    # If "Translation:" wasn't there, but it looks like "Yes, it is grammatical. The cat sat."
    elif cleaned.startswith("Yes,") or cleaned.startswith("No,") or "grammatical" in lower_cleaned:
         # Try to split by first period?
         parts = cleaned.split('.', 1)
         if len(parts) > 1:
             potential = parts[1].strip()
             if potential:
                 best_candidate = potential
    
    # Final cleanup
    return best_candidate

def process_files():
    input_dir = '/home/ninin/projects/Research/Data/qwen_14b/gramatical_induction'
    output_dir = os.path.join(input_dir, 'cleaned_data')
    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(input_dir, '*.csv'))
    
    for filepath in files:
        filename = os.path.basename(filepath)
        print(f"Processing {filename}...")
        
        output_data = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for i, row in enumerate(reader):
                prompt = row.get('Prompt', '')
                target_raw = row.get('Target Output', '')
                actual_raw = row.get('Actual Output', '')
                
                targets = clean_target(target_raw)
                actual = clean_actual(actual_raw)
                
                output_data.append({
                    "file": filename,
                    "row": i + 2, # CSV header is row 1
                    "prompt": prompt,
                    "targets": targets,
                    "actual": actual,
                    "raw_target": target_raw, # Keep for debugging
                    "raw_actual": actual_raw  # Keep for debugging
                })
        
        # Save to JSON
        json_filename = filename.replace('.csv', '.json')
        output_path = os.path.join(output_dir, json_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
    print(f"Cleaning complete. Files saved to {output_dir}")

if __name__ == "__main__":
    process_files()
