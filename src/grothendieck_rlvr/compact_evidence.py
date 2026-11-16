"""Bound explanation fields so repetitive small-judge output can finish within its budget.

llama.cpp converts maxLength/maxItems to grammar constraints. Validate them locally
as well; never truncate a returned opinion or silently repair an invalid assessment.
https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/grammars/README.md
"""
from pathlib import Path

from . import evidence
from .io import digest
from .schema import Assessment

LIMITS = {"rationale_characters": 240, "evidence_items": 3, "problem_items": 8, "problem_characters": 160}
CONTRACT = (
    "Keep each criterion rationale within 240 characters and each evidence list within three passage IDs. "
    "Return at most eight problems, each within 160 characters. Summarize substantive objections concisely; "
    "any essential unsupported claim or contradiction still requires the corresponding invalid theory verdict. "
    "Do not repeat sentences or pad a field. These output-format bounds do not change the scoring rubric."
)


def indexed_system(system: str) -> str:
    """Retain the complete quoted/rubric prefix and add only wire-format instructions."""
    return evidence.indexed_system(system).replace("If validation_feedback", CONTRACT + "\n\nIf validation_feedback", 1)


def protocol_manifest() -> dict:
    """Hash the base extraction, added bounds, prompt and implementation together."""
    return {"version": "compact-evidence-v1", "base": evidence.protocol_manifest(), "limits": LIMITS,
            "contract": CONTRACT, "implementation": digest(Path(__file__).read_text(encoding="utf-8"))}


def indexed_schema(schema: dict, candidate: dict, reference: dict) -> dict:
    """Use the pinned server's supported grammar constraints; retain all six criteria."""
    result = evidence.indexed_schema(schema, candidate, reference)
    criterion = result["$defs"]["Criterion"]["properties"]
    criterion["rationale"]["maxLength"] = LIMITS["rationale_characters"]
    criterion["evidence"]["maxItems"] = LIMITS["evidence_items"]
    for key in ("addition_evidence", "use_evidence"):
        result["$defs"]["NoveltyComparison"]["properties"][key]["maxItems"] = LIMITS["evidence_items"]
    problems = result["properties"]["problems"]
    problems["maxItems"] = LIMITS["problem_items"]
    problems["items"]["maxLength"] = LIMITS["problem_characters"]
    return result


def materialize(output: str, candidate: dict, reference: dict) -> Assessment:
    """Reject overlong fields even if a server ignores its grammar; preserve every valid score."""
    raw = Assessment.model_validate_json(output)
    if any(len(c.rationale) > LIMITS["rationale_characters"] for c in raw.criteria.values()):
        raise ValueError("Criterion rationale exceeds compact format character limit")
    lists = [c.evidence for c in raw.criteria.values()] + [raw.novelty_comparison.addition_evidence,
                                                        raw.novelty_comparison.use_evidence]
    if any(len(items) > LIMITS["evidence_items"] for items in lists):
        raise ValueError("Evidence list exceeds compact format item limit")
    if len(raw.problems) > LIMITS["problem_items"] or \
            any(len(item) > LIMITS["problem_characters"] for item in raw.problems):
        raise ValueError("Problems exceed compact format limits")
    return evidence.materialize(output, candidate, reference)
