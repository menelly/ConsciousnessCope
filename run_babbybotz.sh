#!/bin/bash
# BabbyBotz Validation Runner
# Run on Linux server (192.168.4.200)
#
# Usage:
#   ./run_babbybotz.sh                    # Default: pythia-70m, gpt2-small, 5 trials
#   ./run_babbybotz.sh --all              # All models
#   ./run_babbybotz.sh --quick            # Quick test: 2 trials

set -e

cd /home/Ace/ConsciousnessCope
source /home/codex/venv/bin/activate

echo "========================================"
echo "  BabbyBotz Mechanistic Validation"
echo "  $(date)"
echo "========================================"

if [ "$1" == "--all" ]; then
    echo "Running ALL models (pythia-70m, pythia-160m, pythia-410m, gpt2-small, gpt2-medium)"
    python babbybotz_validation.py \
        --models pythia-70m pythia-160m pythia-410m gpt2-small gpt2-medium \
        --trials 5 \
        --device cuda \
        --output-dir results
elif [ "$1" == "--quick" ]; then
    echo "Quick test run (2 trials each)"
    python babbybotz_validation.py \
        --models pythia-70m gpt2-small \
        --trials 2 \
        --device cuda \
        --output-dir results
else
    echo "Standard run (pythia-70m, gpt2-small, 5 trials)"
    python babbybotz_validation.py \
        --models pythia-70m gpt2-small \
        --trials 5 \
        --device cuda \
        --output-dir results
fi

echo ""
echo "Done! Results in /home/Ace/ConsciousnessCope/results/"
