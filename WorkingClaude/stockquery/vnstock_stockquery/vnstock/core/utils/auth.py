# vnstock/core/utils/auth.py

"""
User authentication and API key registration for vnstock.

Note: vnai dependency has been removed. Auth functions are no-ops.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def register_user(api_key: Optional[str] = None) -> bool:
    """Registration is disabled (vnai removed)."""
    logger.info("Auth registration disabled - vnai dependency removed")
    return True


def change_api_key(api_key: str) -> bool:
    """API key management is disabled (vnai removed)."""
    logger.info("API key management disabled - vnai dependency removed")
    return True


def check_status() -> Optional[dict]:
    """Status check is disabled (vnai removed)."""
    logger.info("Status check disabled - vnai dependency removed")
    return {"has_api_key": False, "tier": "unlimited", "limits": {}}
