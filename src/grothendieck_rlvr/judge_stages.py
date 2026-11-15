"""Evidence-bearing specialist contracts and deterministic aggregation.

DnA-Eval motivates decomposition, not local accuracy guarantees:
https://aclanthology.org/2025.coling-main.156/. No external code is copied.
The historical Assessment remains unchanged; stage findings are archived separately.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import StrictBool

from .io import digest
from .prompts import DIRECTORY, judge_system
from .schema import Assessment, Criterion, NoveltyComparison, Record


CRITERIA = {
    "structural_understanding": "Useful objects, definitions, invariants or relationships explain the problem.",
    "justified_generality": "A valid method or statement covers a meaningful family with assumptions and boundaries.",
    "problem_as_consequence": "The requested result follows from the framework without hiding the difficult step.",
    "reuse_and_connections": "Another consequence, application or substantive mathematical connection is demonstrated.",
    "conceptual_economy": "Definitions and lemmas are motivated, understandable and functional for the mathematical work performed.",
}
PROTOCOLS = ("two-stage-v1", "specialists-v1")


class Issue(Record):
    """A substantive mathematical objection, never mere uncertainty about novelty."""
    evidence: list[str]
    rationale: str
    severity: Literal["unsupported", "contradicted"]


class ReferenceFinding(Record):
    """Isolate the addition from the conventional calculation used for the task."""
    reference_excerpt: str
    addition_evidence: list[str]
    rationale: str
    relation: Literal["within_reference", "beyond_reference", "unresolved"]
    issues: list[Issue]


class DevelopmentFinding(Record):
    """Trace applications of the addition; its own justification is not an application."""
    operation_evidence: list[str]
    dependency_rationale: str
    operation_uses_addition: StrictBool
    consequence_evidence: list[str]
    substantial_departure: StrictBool
    boundary_evidence: list[str]
    framework_evidence: list[str]
    problem_recovery_evidence: list[str]
    reusable_framework: StrictBool
    issues: list[Issue]


class ValidityFinding(Record):
    """Overall theory validity stays separate from final-answer verification."""
    evidence: list[str]
    rationale: str
    verdict: Literal["none", "supported", "unsupported", "contradicted"]
    issues: list[Issue]


class ConceptFinding(Record):
    """The first two-call stage handles reference comparison and development only."""
    reference: ReferenceFinding
    development: DevelopmentFinding


class QualityFinding(Record):
    """The second two-call stage assesses validity and conventional theory quality."""
    validity: ValidityFinding
    criteria: dict[str, Criterion]


class CriterionFinding(Record):
    """One isolated criterion judgment may also flag a substantive mathematical error."""
    rating: Criterion
    issues: list[Issue]


def validate_stage(finding: Record, candidate: str, reference: str) -> None:
    """Check source attribution and output contracts, not semantic entailment."""
    def check(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "reference_excerpt":
                    if not child.strip() or child not in reference:
                        raise ValueError("reference_excerpt must be an exact nonempty reference excerpt")
                elif key.endswith("evidence"):
                    if any(not e.strip() or e not in candidate for e in child):
                        raise ValueError(f"{key} must contain exact nonempty candidate excerpts")
                else:
                    check(child)
            if "score" in value and value["score"] and not value.get("evidence"):
                raise ValueError("Positive criterion scores require candidate evidence")
            if "severity" in value and not value.get("evidence"):
                raise ValueError("A substantive issue requires candidate evidence")
            if value.get("relation") == "beyond_reference" and not value.get("addition_evidence"):
                raise ValueError("beyond_reference requires addition_evidence")
            if value.get("operation_uses_addition") and not value.get("operation_evidence"):
                raise ValueError("operation_uses_addition requires operation_evidence")
            if value.get("verdict") == "supported" and not value.get("evidence"):
                raise ValueError("Supported theory requires candidate evidence")
            if value.get("verdict") in ("unsupported", "contradicted") and not value.get("issues"):
                raise ValueError("Unsupported or contradicted theory requires a substantive issue")
        elif isinstance(value, list):
            for child in value:
                check(child)
    if isinstance(finding, QualityFinding) and set(finding.criteria) != set(CRITERIA):
        raise ValueError("Quality stage requires exactly the five non-novelty criteria")
    check(finding.model_dump())


def novelty_level(reference: ReferenceFinding, development: DevelopmentFinding) -> int:
    """Map evidence-bearing declarations to fixed ordinal anchors, without score voting."""
    if reference.relation != "beyond_reference" or not reference.addition_evidence:
        return 0
    if not development.operation_uses_addition or not development.operation_evidence:
        return 1
    if not (development.substantial_departure and development.consequence_evidence
            and development.boundary_evidence):
        return 2
    return 4 if (development.reusable_framework and development.framework_evidence
                 and development.problem_recovery_evidence) else 3


def aggregate(findings: dict[str, Record]) -> Assessment:
    """Combine all required opinions; one mathematical objection vetoes the bonus."""
    if set(findings) == {"concepts", "quality"}:
        reference, development = findings["concepts"].reference, findings["concepts"].development
        validity, criteria = findings["quality"].validity, dict(findings["quality"].criteria)
        issues = reference.issues + development.issues + validity.issues
    elif set(findings) == {"validity", "reference", "development", *CRITERIA}:
        reference, development, validity = (findings[k] for k in ("reference", "development", "validity"))
        criteria = {key: findings[key].rating for key in CRITERIA}
        issues = reference.issues + development.issues + validity.issues
        issues += [issue for key in CRITERIA for issue in findings[key].issues]
    else:
        raise ValueError("Incomplete or unknown judge stage set")
    verdicts = {validity.verdict, *(issue.severity for issue in issues)}
    verdict = "contradicted" if "contradicted" in verdicts else (
        "unsupported" if "unsupported" in verdicts else validity.verdict)
    level = novelty_level(reference, development)
    use = development.operation_evidence if development.operation_uses_addition else []
    criteria["constructive_novelty"] = Criterion(
        evidence=reference.addition_evidence + use,
        rationale=f"Derived level {level}. {reference.rationale} {development.dependency_rationale}",
        score=level,
    )
    return Assessment(theory_validity=verdict, criteria=criteria,
                      novelty_comparison=NoveltyComparison(
                          reference_excerpt=reference.reference_excerpt,
                          addition_evidence=reference.addition_evidence,
                          use_evidence=use, relation=reference.relation),
                      problems=list(dict.fromkeys(f"{i.severity}: {i.rationale}" for i in issues)))


@dataclass(frozen=True)
class StageSpec:
    """The stage's complete inference contract participates in the judge identity."""
    name: str
    record: type[Record]
    system: str
    max_tokens: int
    reasoning_tokens: int
    dependencies: tuple[str, ...] = ()

    def schema(self) -> dict:
        """Constrain five criterion keys explicitly for the server's JSON grammar."""
        schema = self.record.model_json_schema()
        if self.record is QualityFinding:
            schema["properties"]["criteria"] = {
                "type": "object", "properties": {k: {"$ref": "#/$defs/Criterion"} for k in CRITERIA},
                "required": list(CRITERIA), "additionalProperties": False,
            }
        return schema

    def manifest(self) -> dict:
        """Preserve schema field ordering as well as its values in the content hash."""
        import json
        return {"name": self.name, "system": self.system, "schema": json.dumps(self.schema()),
                "max_tokens": self.max_tokens, "reasoning_tokens": self.reasoning_tokens,
                "dependencies": self.dependencies,
                "implementation": digest(Path(__file__).read_text(encoding="utf-8"))}


def stage_specs(protocol: str, variant: str) -> list[StageSpec]:
    """Both protocols share anchors and aggregation; only the task decomposition changes."""
    if protocol not in PROTOCOLS:
        raise ValueError(f"Unknown judge protocol: {protocol}")
    common = judge_system(variant, version="v8")
    def instructions(name):
        return (DIRECTORY / f"stage-{name}-v1.txt").read_text(encoding="utf-8")
    reference, development, validity = (instructions(k) for k in ("reference", "development", "validity"))
    criteria = "\n".join(f"{key}: {description}" for key, description in CRITERIA.items())
    criterion = instructions("criterion")
    if protocol == "two-stage-v1":
        return [StageSpec("concepts", ConceptFinding, common + "\nReturn reference and development objects.\n"
                          + reference + "\n" + development, 1536, 512),
                StageSpec("quality", QualityFinding, common + "\nReturn validity and criteria objects.\n"
                          + validity + "\n" + criterion + "\nScore all five criteria:\n" + criteria, 1536, 512)]
    return [StageSpec("validity", ValidityFinding, common + "\n" + validity, 1024, 512),
            StageSpec("reference", ReferenceFinding, common + "\n" + reference, 1024, 512),
            StageSpec("development", DevelopmentFinding, common + "\n" + development, 1024, 512, ("reference",)),
            *(StageSpec(key, CriterionFinding, common + "\nReturn rating and issues objects.\n" + criterion
                        + f"\nScore only {key}: {description}", 512, 256)
              for key, description in CRITERIA.items())]
