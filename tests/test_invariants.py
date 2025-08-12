# tests/test_invariants.py
import pytest
import demo_runner as demo

# Scenario map: expected string, run_fn, candidates_fn
SCENARIOS = {
    "basic": (
        "Alice emailed Bob and told him that the budget was approved .",
        demo.run_basic,
        demo.candidates_basic,
    ),
    "coref": (
        "She presented the results .",
        demo.run_coref,
        demo.candidates_coref,
    ),
    "tense": (
        "the team completed the project and celebrated .",
        demo.run_tense,
        demo.candidates_tense,
    ),
    "kb": (
        "France .",
        demo.run_kb,
        demo.candidates_kb,
    ),
}

@pytest.mark.parametrize("name", ["basic", "coref", "tense", "kb"])
def test_invariants_and_exact_output(name):
    expected, run_fn, cand_fn = SCENARIOS[name]
    # Run the scenario directly (no artifact files needed)
    emitted, trace_df, phi_df, steps_raw, cands, _ = run_fn()

    # 1) Exact output string
    generated = " ".join(emitted)
    assert generated == expected, f"{name}: got {generated!r}, expected {expected!r}"

    # 2) Invariants via the same verifier used by the CLI
    ok, errors = demo.verify_invariants(trace_df, phi_df, cands)
    assert ok, f"{name} invariants failed:\n- " + "\n- ".join(errors)

def test_entropy_is_zero_every_step_coref():
    # Quick sanity: the trace reports H=0.0 at every step
    _, trace_df, _, _, _, _ = SCENARIOS["coref"][1]()  # run_coref
    assert (trace_df["Entropy_H"] == 0.0).all(), "Entropy_H should be 0.0 at every step"

def test_phi_completeness_basic():
    # Explicitly check Φ completeness on one scenario in addition to verify()
    _, trace_df, phi_df, _, cands, _ = SCENARIOS["basic"][1]()  # run_basic
    # Build elimination index per step from Φ ledger
    elim_by_step = {}
    for _, r in phi_df.iterrows():
        k = int(r["Step"])
        elim_by_step.setdefault(k, set()).add(r["Eliminated_Token"])

    for step_idx, cand in enumerate(cands, start=1):
        row = trace_df[trace_df["Step"] == step_idx].iloc[0]
        surv = row["Survivors_after_T"]
        surv_set = set(surv.split(", ")) if isinstance(surv, str) and surv else set()
        elim_set = elim_by_step.get(step_idx, set())
        assert set(cand) == surv_set | elim_set, (
            f"Φ completeness failed at step {step_idx}: "
            f"Candidates={sorted(set(cand))} vs Survivors∪Eliminated={sorted(surv_set | elim_set)}"
        )
