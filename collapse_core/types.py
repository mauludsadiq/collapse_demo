from typing import Dict, List, Tuple, Any

Token = str

class SemanticGraph:
    def __init__(self, nodes: Dict, edges: List[Tuple], meta: Dict):
        self.nodes = nodes
        self.edges = edges
        self.meta = meta
        self.cursor = {"state": "s0", "plan_step": 1}

class CandidateSet:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

class SurvivorSet(CandidateSet):
    pass
