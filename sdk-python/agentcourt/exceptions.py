"""AgentCourt exceptions."""


class AgentCourtError(Exception):
    """Base exception for AgentCourt SDK."""
    pass


class PaymentRequiredError(AgentCourtError):
    """Raised when a dispute requires payment (HTTP 402).

    This means either:
    1. You've exceeded the free tier (100 disputes/month)
    2. The API requires x402 payment for this request

    To resolve, either:
    - Wait for your free tier to reset (1st of each month)
    - Include x402 payment in your request
    """
    def __init__(self, message: str, payment_challenge: str = ""):
        self.payment_challenge = payment_challenge
        super().__init__(message)
