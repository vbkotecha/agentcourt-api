"""
AgentCourt x402 Payment Middleware

Integrates Coinbase x402 payment protocol for the AgentCourt API.
Agents must pay $0.05 USDC on Base mainnet to create disputes.
Free tier: 100 disputes/month per IP.

Setup:
    pip install flask
    export CDP_API_KEY_ID=...
    export CDP_API_KEY_SECRET=...
    export AGENTCOURT_WALLET_ADDRESS=0x...

Or use standalone:
    from x402_middleware import check_payment, create_payment_challenge
"""

import os
import json
import time
import hashlib
import urllib.request
import urllib.error
from typing import Optional, Tuple

# ─── Configuration ───────────────────────────────────────────────────────────

FACILITATOR_URL = "https://api.cdp.coinbase.com/platform/v2/x402"
NETWORK = "base"  # Base mainnet
CHAIN_ID = "eip155:8453"
ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC on Base
PRICE_USD = "0.05"  # $0.05 per dispute
PRICE_ATOMIC = "50000"  # $0.05 in atomic USDC units (6 decimals)

# Free tier tracking (in-memory, reset on restart)
FREE_TIER_LIMIT = 100
_ip_usage = {}

# ─── Free Tier Check ─────────────────────────────────────────────────────────

def check_free_tier(ip_address: str) -> bool:
    """Check if IP has free tier remaining."""
    count = _ip_usage.get(ip_address, 0)
    return count < FREE_TIER_LIMIT

def increment_usage(ip_address: str):
    """Track API usage for free tier."""
    _ip_usage[ip_address] = _ip_usage.get(ip_address, 0) + 1

# ─── x402 Payment Challenge ──────────────────────────────────────────────────

def create_payment_challenge(resource: str = "/v1/disputes") -> dict:
    """
    Create an x402 payment challenge response.
    Returns the 402 response body with payment requirements.
    """
    wallet = os.environ.get("AGENTCOURT_WALLET_ADDRESS", "")
    if not wallet:
        return {
            "error": "Payment not configured",
            "message": "Server wallet address not set. Set AGENTCOURT_WALLET_ADDRESS."
        }

    return {
        "x402Version": 1,
        "error": "X402_PAYMENT_REQUIRED",
        "paymentRequirements": {
            "scheme": "exact",
            "network": NETWORK,
            "chainId": CHAIN_ID,
            "asset": ASSET,
            "amount": PRICE_ATOMIC,
            "payTo": wallet,
            "maxTimeoutSeconds": 60,
            "resource": resource,
            "description": f"AgentCourt dispute resolution — ${PRICE_USD} USDC",
            "mimeType": "application/json",
        },
        "paymentInstructions": {
            "facilitatorUrl": FACILITATOR_URL,
            "network": NETWORK,
            "scheme": "exact",
        }
    }


# ─── Payment Verification ────────────────────────────────────────────────────

def verify_payment(payment_header: str, resource: str = "/v1/disputes") -> Tuple[bool, Optional[str]]:
    """
    Verify an x402 payment receipt against the CDP facilitator.
    Returns (valid: bool, error: Optional[str]).
    """
    if not payment_header:
        return False, "No payment header provided"

    key_id = os.environ.get("CDP_API_KEY_ID", "")
    key_secret = os.environ.get("CDP_API_KEY_SECRET", "")

    if not key_id or not key_secret:
        return False, "CDP credentials not configured"

    # Build verify request
    verify_payload = {
        "x402Version": 1,
        "paymentHeader": payment_header,
        "paymentRequirements": {
            "scheme": "exact",
            "network": NETWORK,
            "chainId": CHAIN_ID,
            "asset": ASSET,
            "amount": PRICE_ATOMIC,
            "payTo": os.environ.get("AGENTCOURT_WALLET_ADDRESS", ""),
            "maxTimeoutSeconds": 60,
            "resource": resource,
        }
    }

    try:
        # Note: CDP facilitator requires JWT auth using ES256 signing
        # For now, this is a placeholder that will be filled in with CDP SDK
        # In production, use the @coinbase/cdp-sdk to sign the request
        return False, "Payment verification requires CDP SDK integration (pending wallet setup)"
    except Exception as e:
        return False, f"Verification error: {str(e)}"


# ─── Payment Check Decorator ─────────────────────────────────────────────────

def require_payment_or_free_tier(ip_address: str, payment_header: Optional[str] = None) -> dict:
    """
    Check if request should be allowed (free tier) or requires payment.
    Returns:
        {"allowed": True} — proceed with request
        {"challenge": {...}} — return 402 with payment challenge
    """
    # Check free tier first
    if check_free_tier(ip_address):
        increment_usage(ip_address)
        return {"allowed": True, "tier": "free"}

    # Check payment header
    if payment_header:
        valid, error = verify_payment(payment_header)
        if valid:
            return {"allowed": True, "tier": "paid"}
        else:
            return {
                "challenge": create_payment_challenge(),
                "error": error
            }

    # No free tier left, no payment — return challenge
    return {"challenge": create_payment_challenge()}


# ─── Health Check ────────────────────────────────────────────────────────────

def x402_status() -> dict:
    """Return x402 payment configuration status."""
    return {
        "enabled": bool(os.environ.get("AGENTCOURT_WALLET_ADDRESS")),
        "wallet": os.environ.get("AGENTCOURT_WALLET_ADDRESS", "not configured"),
        "network": NETWORK,
        "price": f"${PRICE_USD} USDC",
        "free_tier": {
            "limit": FREE_TIER_LIMIT,
            "used": sum(_ip_usage.values()),
        },
        "facilitator": FACILITATOR_URL,
    }
