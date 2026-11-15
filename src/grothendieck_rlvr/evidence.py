"""Indexed source passages avoid asking small judges to reproduce mathematical typography.

This is local pointer decoding, not another model call or a semantic verifier.
Location-based citation extraction is described at
https://platform.claude.com/docs/en/build-with-claude/citations#how-citations-work.
We use no Anthropic service, model, SDK or copied implementation.
"""
from copy import deepcopy
from pathlib import Path

from .io import digest
from .schema import Assessment

MAX_PASSAGE_CHARACTERS = 320
CONTRACT = Path(__file__).with_name("prompts") / "indexed-evidence-v1.txt"


def catalog(text: str, prefix: str) -> dict[str, str]:
    """Preserve every character in order, cutting physical lines into bounded passages."""
    passages = [line[start:start+MAX_PASSAGE_CHARACTERS]
                for line in text.splitlines(keepends=True)
                for start in range(0, len(line), MAX_PASSAGE_CHARACTERS)]
    if not any(p.strip() for p in passages):
        raise ValueError("An evidence source must contain nonblank text")
    return {f"{prefix}{i}": passage for i, passage in enumerate(passages)}


def indexed_system(system: str) -> str:
    """Replace only the output contract; keep all rubric anchors and framing verbatim."""
    before, separator, rest = system.partition("Return only JSON")
    _, feedback, after = rest.partition("If validation_feedback")
    if not separator or not feedback:
        raise ValueError("Unexpected rubric contract; do not silently alter the judging prompt")
    return before + CONTRACT.read_text(encoding="utf-8").rstrip() + "\n\n" + feedback + after


def protocol_manifest() -> dict:
    """Bind the complete materialization algorithm and contract into cache/run identities."""
    return {"version": "indexed-evidence-v1", "max_passage_characters": MAX_PASSAGE_CHARACTERS,
            "implementation": digest(Path(__file__).read_text(encoding="utf-8")),
            "contract": CONTRACT.read_text(encoding="utf-8")}


def indexed_schema(schema: dict, candidate: dict, reference: dict) -> dict:
    """Constrain each source independently; blank passages remain context, never citations."""
    result = deepcopy(schema)
    candidate_ids = {"type": "string", "enum": [key for key, text in candidate.items() if text.strip()]}
    result["$defs"]["Criterion"]["properties"]["evidence"]["items"] = candidate_ids
    comparison = result["$defs"]["NoveltyComparison"]["properties"]
    comparison["reference_excerpt"] = {"type": "string", "enum": [key for key, text in reference.items() if text.strip()]}
    for field in ("addition_evidence", "use_evidence"):
        comparison[field]["items"] = candidate_ids
    return result


def materialize(output: str, candidate: dict, reference: dict) -> Assessment:
    """Resolve validated IDs to original text, retaining every score and validity opinion."""
    raw = Assessment.model_validate_json(output).model_dump()
    def extract(identifier, source):
        if identifier not in source or not source[identifier].strip():
            raise ValueError(f"Unknown or blank evidence ID {identifier!r}; select an ID from the correct source")
        return source[identifier]
    for criterion in raw["criteria"].values():
        criterion["evidence"] = [extract(key, candidate) for key in criterion["evidence"]]
    comparison = raw["novelty_comparison"]
    comparison["reference_excerpt"] = extract(comparison["reference_excerpt"], reference)
    for field in ("addition_evidence", "use_evidence"):
        comparison[field] = [extract(key, candidate) for key in comparison[field]]
    result = Assessment.model_validate(raw)
    result.validate_evidence("".join(candidate.values()))
    result.validate_reference("".join(reference.values()))
    return result
