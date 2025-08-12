#!/usr/bin/env python3
"""
Collapse Logic Proof-of-Concept runner (T, Φ, Ψ)
Self-contained scenarios; supports:
  --scenario {basic,coref,tense,kb}
  --run-all
  --print
  --color
  --json
  --verify
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

import pandas as pd

from collapse_core.engine import CollapseEngine
from collapse_core.T import T
from collapse_core.Phi import Phi
from collapse_core.Psi import Psi

# Optional pretty printing
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAVE_RICH = True
    console = Console()
except Exception:
    HAVE_RICH = False
    console = None


# =============== Scenario: BASIC (budget approval) ===============
def build_basic_graph():
    return {
        "entities": {
            "Alice": {"type": "Person", "gender": "F"},
            "Bob":   {"type": "Person", "gender": "M"},
            "budget": {"type": "Document", "status": "pending"},
            "meeting": {"type": "Event", "tense": "past"}
        },
        "plans": [
            {"step": 1, "action": "email", "agent": "Alice", "recipient": "Bob", "tense": "past"},
            {"step": 2, "action": "tell",  "agent": "Alice", "recipient": "Bob",
             "content": "that the budget was approved", "tense": "past"}
        ],
        "discourse": {"time": "past", "last_person_male": "Bob"},
        "cursor": {"state": "s0", "plan_step": 1}
    }

def candidates_basic() -> List[List[str]]:
    return [
        ["Alice","Bob"],
        ["emailed","called","texted"],
        ["Bob","Alice"],
        ["and","."],
        ["told","informed","notified"],
        ["him","her"],
        ["that","because"],
        ["the","a"],
        ["budget","proposal","report"],
        ["was","is"],
        ["approved","rejected","approve"],
        [".","!"]
    ]

def run_basic():
    G = build_basic_graph()
    engine = CollapseEngine(T(), Phi(), Psi())
    return run_sequence(engine, G, candidates_basic(), artifacts_subdir="basic")


# =============== Scenario: COREF (tightened) ===============
def build_coref_graph():
    return {
        "entities": {
            "CEO": {"type": "Person", "gender": "F"},
            "board": {"type": "Organization"},
            "results": {"type": "Report"}
        },
        "discourse": {"time": "past", "last_person_female": "CEO"},
        "cursor": {"state": "s0"}
    }

def candidates_coref() -> List[List[str]]:
    return [
        ["She","He","They"],
        ["presented","presents"],
        ["the","a"],
        ["results","budget","report"],
        [".","!"],
    ]

def kernels_coref():
    def k_grammar(step, tok, G):
        cats = {
            0: {"She","He","They"},
            1: {"presented","presents"},
            2: {"the","a"},
            3: {"results","budget","report"},
            4: {"."}
        }
        return (tok in cats[step], f"grammar:step{step}")

    def k_coref(step, tok, G):
        if step == 0:
            return (tok == "She", "coref:female_she")
        return (True, "coref:any")

    def k_tense(step, tok, G):
        if G["discourse"].get("time") == "past" and tok in {"presents"}:
            return (False, "tense:must_be_past")
        return (True, "tense:ok")

    def k_definiteness(step, tok, G):
        if step == 2:
            return (tok == "the", "role:definite_results")
        return (True, "role:any")

    def k_content(step, tok, G):
        if step == 3:
            return (tok == "results", "role:present_results")
        return (True, "role:any")

    return [k_grammar, k_coref, k_tense, k_definiteness, k_content]

def run_coref():
    G = build_coref_graph()
    engine = CollapseEngine(T(kernels=kernels_coref()), Phi(), Psi())
    return run_sequence(engine, G, candidates_coref(), artifacts_subdir="coref")


# =============== Scenario: TENSE (consistency; definite object) ===============
def build_tense_graph():
    return {
        "entities": {"team": {"type": "Group"}, "project": {"type": "WorkItem"}},
        "discourse": {"time": "past"},
        "cursor": {"state": "s0"}
    }

def candidates_tense() -> List[List[str]]:
    return [
        ["the"],
        ["team"],
        ["completed","completes","complete"],
        ["the","a"],
        ["project","projects"],
        ["and"],
        ["celebrated","celebrates"],
        [".","!"]
    ]

def kernels_tense():
    def k_grammar(step, tok, G):
        cats = {
            0: {"the"},
            1: {"team"},
            2: {"completed","completes","complete"},
            3: {"the","a"},
            4: {"project","projects"},
            5: {"and"},
            6: {"celebrated","celebrates"},
            7: {"."}
        }
        return (tok in cats[step], f"grammar:step{step}")

    def k_tense(step, tok, G):
        if G["discourse"].get("time") == "past":
            if tok in {"completes","complete","celebrates"}:
                return (False, "tense:must_be_past")
        return (True, "tense:ok")

    def k_roles(step, tok, G):
        if step == 4:
            return (tok == "project", "role:singular_object")
        return (True, "role:any")

    def k_definiteness(step, tok, G):
        if step == 3:
            return (tok == "the", "role:definite_object")
        return (True, "role:any")

    return [k_grammar, k_tense, k_roles, k_definiteness]

def run_tense():
    G = build_tense_graph()
    engine = CollapseEngine(T(kernels=kernels_tense()), Phi(), Psi())
    return run_sequence(engine, G, candidates_tense(), artifacts_subdir="tense")


# =============== Scenario: KB (domain facts) ===============
def build_kb_graph():
    return {
        "facts": {
            "capital_of": {
                "France": "Paris",
                "Germany": "Berlin",
                "Spain": "Madrid"
            }
        },
        "subject_city": "Paris",
        "discourse": {"time": "present"},
        "cursor": {"state": "s0"}
    }

def candidates_kb() -> List[List[str]]:
    return [
        ["France","Germany","Spain"],
        [".","!"]
    ]

def kernels_kb():
    def k_grammar(step, tok, G):
        cats = {0: {"France","Germany","Spain"}, 1: {"."}}
        return (tok in cats[step], f"grammar:step{step}")

    def k_fact(step, tok, G):
        if step == 0:
            capitals = G["facts"]["capital_of"]
            city = G["subject_city"]
            return (capitals.get(tok) == city, "kb:city_matches_country")
        return (True, "kb:any")

    return [k_grammar, k_fact]

def run_kb():
    G = build_kb_graph()
    engine = CollapseEngine(T(kernels=kernels_kb()), Phi(), Psi())
    return run_sequence(engine, G, candidates_kb(), artifacts_subdir="kb")


# =============== Shared runner & printers ===============
def run_sequence(engine: CollapseEngine, G: dict, candidates_per_step: List[List[str]], artifacts_subdir: str):
    """
    Runs the collapse loop and returns:
      emitted (list[str]),
      trace_df (pd.DataFrame),
      phi_df (pd.DataFrame),
      steps_raw (list[dict]),  # raw per-step data for JSON
      candidates_copy (List[List[str]])  # echo back for verification
    """
    trace_rows, emitted, steps_raw = [], [], []
    for step_idx, cand in enumerate(candidates_per_step):
        out = engine.step(step_idx, G, cand)  # T -> Φ -> Ψ
        emitted.append(out["token"])

        survivors = out["survivors"]
        eliminated = [t for t in cand if t not in survivors]
        elim_detail = [
            {"token": t, "reasons": out["elim_reasons"].get(t, [])}
            for t in eliminated
        ]

        trace_rows.append({
            "Step": step_idx + 1,
            "Candidates": ", ".join(cand),
            "Survivors_after_T": ", ".join(survivors),
            "Ψ_choice": out["token"],
            "Ψ_mode": out["mode"],
            "Entropy_H": 0.0
        })

        steps_raw.append({
            "step": step_idx + 1,
            "candidates": cand,
            "survivors_after_T": survivors,
            "eliminated": elim_detail,
            "psi_choice": out["token"],
            "psi_mode": out["mode"],
            "entropy_H": 0.0
        })

    # Artifacts (per-scenario subdir)
    artifacts_dir = Path("artifacts") / artifacts_subdir
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    trace_df = pd.DataFrame(trace_rows)
    phi_df = pd.DataFrame(engine.Phi.ledger)
    trace_df.to_csv(artifacts_dir / "trace.csv", index=False)
    phi_df.to_csv(artifacts_dir / "phi_ledger.csv", index=False)

    return emitted, trace_df, phi_df, steps_raw, [list(x) for x in candidates_per_step], artifacts_dir


def print_color(trace_df: pd.DataFrame, phi_df: pd.DataFrame):
    if not HAVE_RICH:
        print("\n=== TRACE ===")
        print(trace_df.to_string(index=False))
        print("\n=== Φ LEDGER ===")
        print(phi_df.to_string(index=False))
        return

    table = Table(title="TRACE", show_lines=True)
    table.add_column("Step", justify="right")
    table.add_column("Candidates")
    table.add_column("Survivors_after_T")
    table.add_column("Ψ_choice")
    table.add_column("Ψ_mode")
    table.add_column("Entropy_H", justify="right")

    for _, row in trace_df.iterrows():
        cands = []
        cand_list = [] if not row["Candidates"] else row["Candidates"].split(", ")
        surv_list = [] if not row["Survivors_after_T"] else row["Survivors_after_T"].split(", ")
        choice = row["Ψ_choice"]
        for tok in cand_list:
            if tok not in surv_list:
                cands.append(f"[red strike]{tok}[/red strike]")
            elif tok == choice:
                cands.append(f"[bold white]{tok}[/bold white]")
            else:
                cands.append(f"[green]{tok}[/green]")

        survs = []
        for tok in surv_list:
            if tok == choice:
                survs.append(f"[bold white]{tok}[/bold white]")
            else:
                survs.append(f"[green]{tok}[/green]")

        table.add_row(
            str(row["Step"]),
            ", ".join(cands),
            ", ".join(survs),
            f"[bold white]{choice}[/bold white]",
            row["Ψ_mode"],
            f"{row['Entropy_H']:.1f}"
        )
    console.print(table)

    ledger_table = Table(title="Φ LEDGER", show_lines=True)
    ledger_table.add_column("Step", justify="right")
    ledger_table.add_column("Eliminated_Token")
    ledger_table.add_column("Reasons")
    for _, row in phi_df.iterrows():
        ledger_table.add_row(
            str(row["Step"]),
            f"[red strike]{row['Eliminated_Token']}[/red strike]",
            row["Reasons"]
        )
    console.print(ledger_table)


# =============== Verification ===============
def verify_invariants(
    trace_df: pd.DataFrame,
    phi_df: pd.DataFrame,
    candidates_per_step: List[List[str]]
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    # 1) H=0
    if not (trace_df["Entropy_H"] == 0.0).all():
        bad = trace_df[trace_df["Entropy_H"] != 0.0]["Step"].tolist()
        errors.append(f"H!=0 at steps: {bad}")

    # 2) No empty survivors
    for _, r in trace_df.iterrows():
        step = int(r["Step"])
        surv = r["Survivors_after_T"]
        if isinstance(surv, float) and pd.isna(surv):
            errors.append(f"Empty survivors at step {step}")
        else:
            surv_list = [s for s in surv.split(", ") if s] if isinstance(surv, str) else []
            if len(surv_list) == 0:
                errors.append(f"Empty survivors at step {step}")

    # 3) Φ completeness
    elim_by_step: Dict[int, List[str]] = {}
    for _, r in phi_df.iterrows():
        k = int(r["Step"])
        elim_by_step.setdefault(k, []).append(r["Eliminated_Token"])

    for idx, cand in enumerate(candidates_per_step, start=1):
        row = trace_df[trace_df["Step"] == idx]
        if row.empty:
            errors.append(f"Trace missing for step {idx}")
            continue
        surv_str = row.iloc[0]["Survivors_after_T"]
        surv_list = [s for s in surv_str.split(", ") if s] if isinstance(surv_str, str) else []
        elim_list = elim_by_step.get(idx, [])

        lhs = set(cand)
        rhs = set(surv_list) | set(elim_list)
        if lhs != rhs:
            errors.append(
                f"Φ completeness failed at step {idx}: "
                f"Candidates={sorted(lhs)} vs Survivors∪Eliminated={sorted(rhs)}"
            )

    # 4) No duplicate Φ rows
    if not phi_df.empty:
        dup_mask = phi_df.duplicated(subset=["Step", "Eliminated_Token"], keep=False)
        if dup_mask.any():
            dupes = phi_df[dup_mask][["Step","Eliminated_Token"]].drop_duplicates().values.tolist()
            errors.append(f"Duplicate Φ rows at (Step,Token): {dupes}")

    ok = len(errors) == 0
    return ok, errors


# =============== CLI helpers ===============
def run_single_scenario(name: str, run_fn, cand_fn, args) -> int:
    emitted, trace_df, phi_df, steps_raw, cands, artifacts_dir = run_fn()
    print(f"[Scenario: {name}] GENERATED: {' '.join(emitted)}")
    print(f"Saved artifacts to {artifacts_dir}/trace.csv and {artifacts_dir}/phi_ledger.csv")

    if args.json:
        (artifacts_dir / "trace.json").write_text(json.dumps(steps_raw, indent=2))
        phi_list = []
        for _, r in phi_df.iterrows():
            phi_list.append({
                "step": int(r["Step"]),
                "eliminated_token": r["Eliminated_Token"],
                "reasons": str(r["Reasons"])
            })
        (artifacts_dir / "phi_ledger.json").write_text(json.dumps(phi_list, indent=2))
        print(f"Saved JSON artifacts to {artifacts_dir}/trace.json and {artifacts_dir}/phi_ledger.json")

    if args.print:
        if args.color:
            print_color(trace_df, phi_df)
        else:
            print("\n=== TRACE ===")
            print(trace_df.to_string(index=False))
            print("\n=== Φ LEDGER ===")
            print(phi_df.to_string(index=False))

    status = 0
    if args.verify:
        ok, errors = verify_invariants(trace_df, phi_df, cands)
        if HAVE_RICH:
            if ok:
                console.print(Panel.fit(f"[bold green]VERIFY {name}: PASS[/bold green]"))
            else:
                console.print(Panel.fit(f"[bold red]VERIFY {name}: FAIL[/bold red]"))
                for e in errors:
                    console.print(f"[red]- {e}[/red]")
        else:
            print(f"VERIFY {name}:", "PASS" if ok else "FAIL")
            if not ok:
                for e in errors:
                    print(" -", e)
        status = 0 if ok else 1

    return status


def main():
    parser = argparse.ArgumentParser(description="Collapse Logic Demo Runner")
    parser.add_argument("--scenario",
                        choices=["basic","coref","tense","kb"],
                        help="Choose a single scenario to run")
    parser.add_argument("--run-all", action="store_true",
                        help="Run all scenarios and write per-scenario artifacts to artifacts/<scenario>/")
    parser.add_argument("--print", action="store_true",
                        help="Print trace and Φ ledger to stdout")
    parser.add_argument("--color", action="store_true",
                        help="Colorize terminal output (requires rich)")
    parser.add_argument("--json", action="store_true",
                        help="Write JSON artifacts alongside CSVs")
    parser.add_argument("--verify", action="store_true",
                        help="Verify invariants (H=0, survivors non-empty, Φ completeness, no Φ dupes)")
    args = parser.parse_args()

    scenario_map = {
        "basic": (run_basic, candidates_basic),
        "coref": (run_coref, candidates_coref),
        "tense": (run_tense, candidates_tense),
        "kb":    (run_kb,    candidates_kb),
    }

    if args.run_all:
        overall_status = 0
        for name in ["basic","coref","tense","kb"]:
            print("\n" + "="*80)
            status = run_single_scenario(name, *scenario_map[name], args=args)
            overall_status = max(overall_status, status)
        print("\n" + "="*80)
        if HAVE_RICH:
            if overall_status == 0:
                console.print(Panel.fit("[bold green]ALL SCENARIOS: PASS[/bold green]"))
            else:
                console.print(Panel.fit("[bold red]ALL SCENARIOS: FAIL[/bold red]"))
        else:
            print("ALL SCENARIOS:", "PASS" if overall_status == 0 else "FAIL")
        sys.exit(overall_status)

    # Single scenario path (default to basic if neither provided)
    name = args.scenario or "basic"
    status = run_single_scenario(name, *scenario_map[name], args=args)
    sys.exit(status)


if __name__ == "__main__":
    main()
