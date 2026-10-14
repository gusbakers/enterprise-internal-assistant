from dataclasses import dataclass, field


@dataclass
class Evidence:
    id: str
    source: str
    text: str
    score: float | None = None


@dataclass
class Result:
    answer: str
    domain: str
    mode: str = "verified data"
    evidence: list[Evidence] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)
    sql: str | None = None
    parameters: list = field(default_factory=list)
    elapsed_ms: int = 0
    resolved_question: str = ""
    notice: str = ""
