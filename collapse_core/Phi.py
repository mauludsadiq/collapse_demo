from typing import Dict, List
from .types import SemanticGraph, CandidateSet, SurvivorSet

class Phi:
    """Nilpotent eliminator: permanently removes non-survivors and logs reasons."""
    def __init__(self):
        self.ledger: List[dict] = []

    def apply(self, step_idx: int, G: dict, C: CandidateSet, V: SurvivorSet, elim_reasons: Dict[str, list]) -> dict:
        for tok in C.tokens:
            if tok not in V.tokens:
                self.ledger.append({
                    "Step": step_idx + 1,
                    "Eliminated_Token": tok,
                    "Reasons": ";".join(elim_reasons.get(tok, []))
                })
        # Example state mutation: advance plan step after email object
        if step_idx == 2:
            G["cursor"]["plan_step"] = 2
        return G
