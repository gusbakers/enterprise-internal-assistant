from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["hr", "marketing", "product", "sql", "unknown"]


class QueryState(BaseModel):
    question: str = Field(..., description="Original user question")
    category: Category = Field("unknown", description="Detected routing category")
    tool_input: str | None = Field(
        None,
        description="Canonicalized or normalized query text sent to the selected tool",
    )
    tool_output: str | None = Field(None, description="Raw answer returned by the tool")
    response: str | None = Field(None, description="Final natural-language response")
    error: str | None = Field(None, description="Error message if an execution step failed")


class AgentState(BaseModel):
    query: QueryState = Field(..., description="The active query state")
    graph: dict[str, str] | None = Field(
        None,
        description="Optional graph metadata describing the connected agent components",
    )
    steps: list[str] = Field(
        default_factory=list,
        description="Execution steps taken through the agent graph",
    )
