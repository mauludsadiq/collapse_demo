from typing import List, Tuple, Dict
from .types import SemanticGraph, CandidateSet, SurvivorSet

def k_grammar_expected(step_idx: int, tok: str, G: dict):
    expect = {
        0: {"cat": "Subject"},
        1: {"cat": "V_COMM_PAST"},
        2: {"cat": "ObjectPerson"},
        3: {"cat": "CoordinatorOrEnd"},
        4: {"cat": "V_REPORT_PAST"},
        5: {"cat": "PronounObj"},
        6: {"cat": "Complementizer"},
        7: {"cat": "Det"},
        8: {"cat": "DocNoun"},
        9: {"cat": "AuxPast"},
        10: {"cat": "Participle"},
        11: {"cat": "PunctEnd"},
    }
    sets = {
        "Subject": {"Alice","Bob"},
        "V_COMM_PAST": {"emailed","called","texted"},
        "ObjectPerson": {"Bob","Alice"},
        "CoordinatorOrEnd": {"and","."},
        "V_REPORT_PAST": {"told","informed","notified"},
        "PronounObj": {"him","her"},
        "Complementizer": {"that","because"},
        "Det": {"the","a"},
        "DocNoun": {"budget","proposal","report"},
        "AuxPast": {"was"},
        "Participle": {"approved","rejected"},
        "PunctEnd": {"."}
    }
    cat = expect[step_idx]["cat"]
    return (tok in sets[cat], f"grammar:{cat}")

def k_role_semantics(step_idx: int, tok: str, G: dict):
    # Step 0: subject must be agent
    if step_idx == 0:
        return (tok == G["plans"][0]["agent"], "role:agent_must_be_Alice")
    # Step 1: comm verb
    if step_idx == 1:
        return (tok in {"emailed","called","texted"}, "role:comm_verb")
    # Step 2: object must be recipient
    if step_idx == 2:
        return (tok == G["plans"][0]["recipient"], "role:recipient_must_be_Bob")
    # Step 3: continue plan
    if step_idx == 3:
        return (tok == "and", "role:continue_plan_with_and")
    # Step 4: reporting verb
    if step_idx == 4:
        return (tok in {"told","informed","notified"}, "role:reporting_verb")
    # Step 5: pronoun binds to Bob
    if step_idx == 5:
        return (tok == "him" and G["discourse"]["last_person_male"] == "Bob", "role:pronoun_binds_to_Bob")
    # Step 6: complementizer 'that'
    if step_idx == 6:
        return (tok == "that", "role:content_that")
    # Step 7: **PATCH** determiner must be 'the' for definite budget
    if step_idx == 7:
        return (tok == "the", "role:definite_budget")
    # Step 8: document is 'budget'
    if step_idx == 8:
        return (tok == "budget", "role:doc_is_budget")
    # Step 9: aux past
    if step_idx == 9:
        return (tok == "was", "role:aux_past")
    # Step 10: predicate approved
    if step_idx == 10:
        return (tok == "approved", "role:predicate_approved")
    return (True, "role:any")

def k_tense(step_idx: int, tok: str, G: dict):
    if G["discourse"]["time"] != "past":
        return (True, "tense:na")
    if tok in {"is","approve","approves"}:
        return (False, "tense:must_be_past")
    return (True, "tense:ok")

KERNELS = [k_grammar_expected, k_role_semantics, k_tense]

class T:
    """Hard reachability: prune candidates to survivors with boolean kernels."""
    def __init__(self, kernels=None):
        self.kernels = kernels or KERNELS

    def candidates(self, G: dict, candidates: list) -> CandidateSet:
        return CandidateSet(candidates)

    def prune(self, step_idx: int, G: dict, C: CandidateSet) -> Tuple[SurvivorSet, Dict[str, list]]:
        survivors = []
        elim_reasons: Dict[str, list] = {}
        for tok in C.tokens:
            ok_all = True
            reasons_failed = []
            for k in self.kernels:
                ok, tag = k(step_idx, tok, G)
                if not ok:
                    ok_all = False
                    reasons_failed.append(tag)
            if ok_all:
                survivors.append(tok)
            else:
                elim_reasons[tok] = reasons_failed
        return SurvivorSet(survivors), elim_reasons
