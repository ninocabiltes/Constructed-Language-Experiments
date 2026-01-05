import csv
import sys
import sacrebleu

def main():
    if len(sys.argv) < 2:
        print("Usage: python compute_metrics.py <csv_file>")
        sys.exit(1)

    filename = sys.argv[1]
    refs = []
    hyps = []

    print(f"Reading file: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for i, row in enumerate(reader):
                target = row.get('Target Output')
                actual = row.get('Actual Output')
                
                if target is None or actual is None:
                    print(f"Warning: Missing 'Target Output' or 'Actual Output' in row {i+2}")
                    continue
                
                # Check for empty strings if necessary, but empty strings are valid in translation (rarely)
                if not target.strip():
                     # If target is empty, we can't evaluate typical metrics well, but let's keep it if consistent
                     pass
                
                refs.append(target)
                hyps.append(actual)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print(f"Loaded {len(refs)} samples.")
    if len(refs) == 0:
        print("No samples found.")
        sys.exit(0)

    # SacreBLEU expects references as a list of lists of strings
    # Outer list: one list per reference (we have 1 reference)
    # Inner list: strings, one per sample
    references = [refs]

    # chrF
    # default parameters: char_order=6, word_order=0, beta=2
    score_chrf = sacrebleu.corpus_chrf(hyps, references)
    print(f"chrF: {score_chrf.score:.2f}")

    # chrF++
    # word_order=2 (includes bigrams)
    score_chrf_pp = sacrebleu.corpus_chrf(hyps, references, word_order=2)
    print(f"chrF++: {score_chrf_pp.score:.2f}")

    # TER
    score_ter = sacrebleu.corpus_ter(hyps, references)
    print(f"TER: {score_ter.score:.2f}")

if __name__ == "__main__":
    main()
