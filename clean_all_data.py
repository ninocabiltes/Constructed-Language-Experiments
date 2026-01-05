import csv
import json
import os
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
        is_explanation = any(x in content for x in ['+', '=', 'vs.', 'vs '])
        
        if is_explanation:
            all_segments.append([""]) 
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
    elif cleaned.startswith("Yes,") or cleaned.startswith("No,") or "grammatical" in lower_cleaned:
         # Try to split by first period?
         parts = cleaned.split('.', 1)
         if len(parts) > 1:
             potential = parts[1].strip()
             if potential:
                 best_candidate = potential
    
    # Final cleanup
    return best_candidate

def process_all_data():
    base_dir = '/home/ninin/projects/Research'
    source_dir = os.path.join(base_dir, 'Data')
    dest_dir = os.path.join(base_dir, 'cleaned_data')
    
    print(f"Cleaning data from {source_dir} to {dest_dir}")
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.csv'):
                source_path = os.path.join(root, file)
                
                # Calculate relative path to maintain structure
                rel_path = os.path.relpath(root, source_dir)
                dest_subdir = os.path.join(dest_dir, rel_path)
                os.makedirs(dest_subdir, exist_ok=True)
                
                print(f"Processing {os.path.join(rel_path, file)}...")
                
                output_data = []
                
                try:
                    with open(source_path, 'r', encoding='utf-8') as f:
                        # Some files might have different delimiters or issues, catch errors
                        try:
                            # Heuristic: verify delimiter? assume ; as per request history
                            # But different models might have different formats?
                            # Let's peek at the first line
                            line = f.readline()
                            delimiter = ';' if ';' in line else ',' # Fallback or simple check?
                            f.seek(0)
                            
                            reader = csv.DictReader(f, delimiter=delimiter)
                            
                            for i, row in enumerate(reader):
                                prompt = row.get('Prompt', '')
                                target_raw = row.get('Target Output', '')
                                actual_raw = row.get('Actual Output', '')
                                
                                # Process only if we have target/actual key, flexible for other schemas?
                                # If keys missing, skip or alert?
                                if target_raw is None: 
                                    # Maybe different column names?
                                    continue
                                    
                                targets = clean_target(target_raw)
                                actual = clean_actual(actual_raw)
                                
                                output_data.append({
                                    "file": file,
                                    "row": i + 2,
                                    "prompt": prompt,
                                    "targets": targets,
                                    "actual": actual,
                                    "raw_target": target_raw,
                                    "raw_actual": actual_raw
                                })
                        except Exception as e:
                            print(f"  Error reading CSV {source_path}: {e}")
                            continue

                    # Save to JSON
                    json_filename = file.replace('.csv', '.json')
                    output_path = os.path.join(dest_subdir, json_filename)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                        
                except Exception as e:
                     print(f"  Error accessing file {source_path}: {e}")

    print("All done.")

if __name__ == "__main__":
    process_all_data()
