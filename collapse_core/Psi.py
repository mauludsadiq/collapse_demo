from typing import List, Tuple
from .types import SurvivorSet

PSI_PREF = {
    "emailed": 0.9, "called": 0.6, "texted": 0.5,
    "told": 0.9, "informed": 0.7, "notified": 0.65
}

class Psi:
    """Tiny ranker over V (k ≤ ~5); deterministic tie-break."""
    def score(self, G: dict, tok: str) -> float:
        return float(PSI_PREF.get(tok, 0.0))

    def select(self, G: dict, V: SurvivorSet) -> Tuple[str, str]:
        if len(V.tokens) == 1:
            return V.tokens[0], "unique"
        scored = [(tok, self.score(G, tok)) for tok in V.tokens]
        scored.sort(key=lambda p: (-p[1], p[0]))
        return scored[0][0], "ranker"
