"""Structured, privacy-safe observability for identity and authentication.

Responsible only for emitting standardized JSON logs without Personally
Identifiable Information (PII), credentials, or transient secrets.
"""

import json
import logging

logger = logging.getLogger("afterlook.identity")


def log_identity_event(
    action: str,
    attempt_id: str,
    *,
    success: bool,
    reason: str | None = None,
    actor_type: str | None = None,
) -> None:
    """Emit structured JSON log for identity events without exposing PII."""
    payload = {
        "event": "identity_oauth",
        "action": action,
        "attempt_id": attempt_id,
        "success": success,
        "actor_type": actor_type,
        "reason": reason,
    }
    if success:
        logger.info(json.dumps(payload))
    else:
        logger.warning(json.dumps(payload))
