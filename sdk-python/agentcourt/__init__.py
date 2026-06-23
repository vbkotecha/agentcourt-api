"""
AgentCourt Python SDK

Policy-driven dispute resolution for AI agent commerce.

    pip install agentcourt

Usage:
    from agentcourt import AgentCourt

    court = AgentCourt()
    ruling = court.file_dispute(
        policy="api-quality",
        claim="Schema mismatch",
        desired_remedy="full_refund",
        delivered=True,
        meets_spec=False,
    )
    print(ruling.ruling)  # "full_refund"
"""
from .client import AgentCourt, Dispute, Ruling, Policy
from .exceptions import AgentCourtError, PaymentRequiredError

__version__ = "1.0.0"
__all__ = ["AgentCourt", "Dispute", "Ruling", "Policy", "AgentCourtError", "PaymentRequiredError"]
