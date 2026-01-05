import csv
import glob
import re

def analyze_file(filepath):
    print(f"Analyzing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        # Detect delimiter? assume semicolon based on view_file
        reader = csv.DictReader(f, delimiter=';')
        
        targets_with_slash = []
        parens_examples = []
        long_actuals = []
        
        for i, row in enumerate(reader):
            target = row.get('Target Output', '').strip()
            actual = row.get('Actual Output', '').strip()
            
            # Clean up quotes for analysis
            target = target.replace('"""', '').strip()
            actual = actual.replace('"""', '').strip()
            
            # Check for slash
            if '/' in target:
                targets_with_slash.append(f"Row {i+2}: {target}")
                
            # Check for parens
            if '(' in target or ')' in target or '(' in actual or ')' in actual:
                parens_examples.append(f"Row {i+2}: Target='{target}' | Actual='{actual}'")
                
            # Check for long actuals
            if len(actual) > len(target) * 2 and len(target) > 5:
                long_actuals.append(f"Row {i+2}: Target='{target}' | Actual='{actual}'")

        print(f"Found {len(targets_with_slash)} targets with '/'")
        for x in targets_with_slash[:3]: print(f"  - {x}")
            
        print(f"Found {len(parens_examples)} rows with parens")
        for x in parens_examples[:3]: print(f"  - {x}")
            
        print(f"Found {len(long_actuals)} verbose actuals")
        for x in long_actuals[:3]: print(f"  - {x}")
        print("-" * 40)

files = glob.glob('/home/ninin/projects/Research/Data/qwen_14b/gramatical_induction/*.csv')
for f in files:
    analyze_file(f)
