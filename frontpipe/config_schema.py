"""
Config schema helpers and validation utilities.

This module defines the expected shape of the YAML config and light validation.
Keep it minimal—strict pydantic isn't required; we just assert required keys exist.
"""
from __future__ import annotations
from typing import Any, Dict, List
import re

REQUIRED_TOP = ["target_date_rule", "poll_interval_minutes", "report_time_local", "feeds"]

REQUIRED_FEED_KEYS = ["counterparty", "stream", "channel"]
ALLOWED_CHANNELS = {"email", "ftp", "sftp", "api", "portal", "manual"}

def validate_config(cfg: Dict[str, Any]) -> None:
    """Lightweight validation with clear errors."""
    for k in REQUIRED_TOP:
        if k not in cfg:
            raise ValueError(f"Missing top-level config key: {k}")
    if not isinstance(cfg["feeds"], list) or not cfg["feeds"]:
        raise ValueError("`feeds` must be a non-empty list.")

    for i, feed in enumerate(cfg["feeds"]):
        for k in REQUIRED_FEED_KEYS:
            if k not in feed:
                raise ValueError(f"Feed #{i} missing required key: {k}")
        ch = feed["channel"]
        if ch not in ALLOWED_CHANNELS:
            raise ValueError(f"Feed #{i} channel '{ch}' not in {ALLOWED_CHANNELS}")

        # If email: require some match instruction
        if ch == "email":
            pat = feed.get("expected_patterns", {})
            if not any(k in pat for k in ("subject_regex", "attachment_regex", "required_attachments")):
                raise ValueError(f"Email feed #{i} needs subject/attachment matching rules.")
            # if required_attachments provided, check shape
            if "required_attachments" in pat:
                if not isinstance(pat["required_attachments"], list) or not pat["required_attachments"]:
                    raise ValueError("required_attachments must be a non-empty list of regex strings.")
                for r in pat["required_attachments"]:
                    re.compile(r)

        # Validate regex strings if present
        def _compile_if_exists(key: str):
            v = feed.get("expected_patterns", {}).get(key)
            if v:
                re.compile(v)
        for key in ("subject_regex", "attachment_regex", "filename_regex", "extract_only"):
            _compile_if_exists(key)
