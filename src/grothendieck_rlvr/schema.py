"""Typed public contracts. A judge opinion remains distinct from a verifier result."""
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Record(BaseModel):
    """Reject undeclared fields so malformed local service output fails visibly."""
    model_config = ConfigDict(extra="forbid")


class Task(Record):
    """One archived generator instance, including its reference and provenance."""
    id: str
    problem: str
    answer: str
    family: str
    split: str
    provenance: dict
    metadata: dict = Field(default_factory=dict)
    source_id: str | None = None


class Verification(Record):
    """Infrastructure failures raise; only mathematical verdicts inhabit this record."""
    status: Literal["correct", "incorrect", "invalid_format"]
    answer: str | None = None
    detail: str = ""

    @property
    def correct(self) -> bool:
        """Binary reward gate, deliberately excluding partial correctness."""
        return self.status == "correct"


class Criterion(Record):
    """An ordinal rubric score supported by verbatim candidate excerpts."""
    score: int = Field(ge=0, le=4, strict=True)
    evidence: list[str]
    rationale: str


class Assessment(Record):
    """Evidence-bearing opinion from a frozen judge, not a proof certificate."""
    weights: ClassVar[dict[str, float]] = {
        "structural_understanding": .25, "justified_generality": .25,
        "problem_as_consequence": .20, "reuse_and_connections": .20,
        "conceptual_economy": .10,
    }
    theory_validity: Literal["none", "supported", "unsupported", "contradicted"]
    criteria: dict[str, Criterion]
    problems: list[str]

    @model_validator(mode="after")
    def all_criteria(self):
        """Require every declared criterion exactly once before computing a score."""
        if set(self.criteria) != set(self.weights):
            raise ValueError("Judge must return exactly the five rubric criteria")
        if any(c.score and not c.evidence for c in self.criteria.values()):
            raise ValueError("Positive scores require supporting excerpts")
        return self

    def validate_evidence(self, response: str) -> None:
        """Reject fabricated spans; this checks attribution, not mathematical truth."""
        if any(not e.strip() or e not in response for c in self.criteria.values() for e in c.evidence):
            raise ValueError("Judge evidence must be a nonempty exact response excerpt")

    @property
    def quality(self) -> float:
        """The preregistered validity gate precedes the normalized weighted mean."""
        if self.theory_validity != "supported":
            return 0.0
        return sum(self.weights[k] * self.criteria[k].score / 4 for k in self.weights)
