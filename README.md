# Collapse Logic Proof-of-Concept (T, Φ, Ψ)

This is a runnable miniature of the **Hard-Constraint Core + Learnable Edge** architecture.

## What it does
- Builds a small typed semantic graph for the prompt “After the meeting,”
- Runs **T** (hard reachability) with constraint kernels
- Applies **Φ** (nilpotent eliminator) to permanently remove non-survivors with audit reasons
- Invokes **Ψ** (small deterministic ranker) *only if* |V|>1
- Emits a deterministic chain with **H=0** at every step

## Run
```bash
python demo_runner.py
