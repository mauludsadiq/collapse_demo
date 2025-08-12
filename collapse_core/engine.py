from typing import List, Dict
from .types import CandidateSet
from .T import T
from .Phi import Phi
from .Psi import Psi

class CollapseEngine:
    def __init__(self, T_op: T, Phi_op: Phi, Psi_op: Psi):
        self.T = T_op; self.Phi = Phi_op; self.Psi = Psi_op

    def step(self, step_idx: int, G: dict, candidates: List[str]) -> Dict:
        C = self.T.candidates(G, candidates)
        V, elim_reasons = self.T.prune(step_idx, G, C)  # T
        G = self.Phi.apply(step_idx, G, C, V, elim_reasons)  # Φ
        tok, mode = self.Psi.select(G, V)  # Ψ
        # Simple discourse update
        if tok == "Bob":
            G["discourse"]["last_person_male"] = "Bob"
        return {"token": tok, "mode": mode, "survivors": V.tokens, "elim_reasons": elim_reasons}
