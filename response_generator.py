from __future__ import annotations

from state import QueryState


class ResponseGenerator:
    """Generate a natural English answer from tool output and agent state."""

    def generate_response(self, state: QueryState) -> str:
        if state.error:
            return (
                "Sorry, I could not complete your request. "
                "Please try again or verify your environment configuration.\n\n"
                f"Error: {state.error}"
            )

        if not state.tool_output:
            return (
                "I understood your question, but the selected tool did not return any results. "
                "Try refining the question or verify the data source."
            )

        if state.category == "unknown":
            return (
                "I was unable to route your question to a specific category, but here is the best available result:\n\n"
                f"{state.tool_output.strip()}"
            )

        return (
            f"Category: {state.category.upper()}\n"
            f"Question: {state.question}\n\n"
            f"{state.tool_output.strip()}\n\n"
            "If you would like, I can refine this answer or search another area."
        )
