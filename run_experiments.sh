#!/bin/bash
PYTHON_EXEC=".venv/bin/python"

# Default to qwen2.5:14b if not provided
MODEL_NAME="${1:-qwen2.5:14b}"

echo "Using Model: $MODEL_NAME"

# Zero Shot
echo "========================================"
echo "Running Zero Shot 1..."
$PYTHON_EXEC experimenterrr.py --model "$MODEL_NAME" --type "zero_shot" --number "1"

# Few Shot WORD
for i in {1..5}
do
   echo "========================================"
   echo "Running Few Shot WORD $i..."
   $PYTHON_EXEC experimenterrr.py --model "$MODEL_NAME" --type "few_shot" --subtype "WORD" --number "$i"
done

# Few Shot TRANSLATION
for i in {1..5}
do
   echo "========================================"
   echo "Running Few Shot TRANSLATION $i..."
   $PYTHON_EXEC experimenterrr.py --model "$MODEL_NAME" --type "few_shot" --subtype "TRANSLATION" --number "$i"
done

# Gramatical Induction
for i in {1..5}
do
   echo "========================================"
   echo "Running Gramatical Induction $i..."
   $PYTHON_EXEC experimenterrr.py --model "$MODEL_NAME" --type "gramatical_induction" --number "$i"
done

# Morphological Induction
for i in {1..1}
do
   echo "========================================"
   echo "Running Morphological Induction $i..."
   $PYTHON_EXEC experimenterrr.py --model "$MODEL_NAME" --type "morphological_induction" --number "$i"
done
