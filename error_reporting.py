"""Opt-in error reporting to Sentry for the Cloud API (server.py).

A no-op unless SENTRY_DSN is set, so tests and local runs never send anything and never import
sentry_sdk.

Nothing sensitive leaves the process: no stack-frame local variables (they hold provider tokens
and the API token), no request bodies, headers, cookies or URLs, and every message is scrubbed of
URL passwords, bearer tokens and JWTs before it is sent.
"""

from __future__ import annotations

import os
import re
import sys
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from sentry_sdk.types import Event, Hint

# scheme://user:password@host -> scheme://user:***@host
_URL_PASSWORD = re.compile(
    r"(?P<head>[a-zA-Z][a-zA-Z0-9+.-]*://[^\s:/@]+:)[^\s@]+(?=@)"
)
# key=value / key: value secrets
_KV_SECRET = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key)(\s*[=:]\s*)\S+"
)
_BEARER = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]*")


def _enabled() -> bool:
    return bool(os.environ.get("SENTRY_DSN", "").strip())


def scrub(text: str) -> str:
    text = _URL_PASSWORD.sub(r"\g<head>***", text)
    text = _KV_SECRET.sub(r"\1\2***", text)
    text = _BEARER.sub("Bearer ***", text)
    return _JWT.sub("***jwt***", text)


def _scrub_event(event: Event, _hint: Hint) -> Event:
    # Scrubbed in place as a plain dict: the Event TypedDict is too strict for these edits.
    data = cast("dict[str, Any]", event)
    for exc in (data.get("exception") or {}).get("values") or []:
        if isinstance(exc.get("value"), str):
            exc["value"] = scrub(exc["value"])
    if isinstance(data.get("message"), str):
        data["message"] = scrub(data["message"])
    logentry = data.get("logentry")
    if isinstance(logentry, dict):
        # Keep only the scrubbed formatted text: a raw param (a token) is no longer next to
        # "Bearer" once split from its template.
        formatted = logentry.get("formatted") or logentry.get("message")
        data["logentry"] = {"message": scrub(str(formatted))} if formatted else {}
    request = data.get("request")
    if isinstance(request, dict):
        # Keep only the method: URLs, query strings and headers can carry tokens.
        data["request"] = {"method": request["method"]} if "method" in request else {}
    for crumb in (data.get("breadcrumbs") or {}).get("values") or []:
        if isinstance(crumb.get("message"), str):
            crumb["message"] = scrub(crumb["message"])
        crumb.pop("data", None)
    data.pop("extra", None)
    trace = (data.get("contexts") or {}).get("trace")
    if isinstance(trace, dict):
        trace.pop("dynamic_sampling_context", None)
    return event


def init_sentry() -> None:
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        return
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        release=os.environ.get("SENTRY_RELEASE") or None,
        # None (not 0.0) disables tracing completely: errors only.
        traces_sample_rate=None,
        send_default_pii=False,
        include_local_variables=False,  # frame locals hold provider and API tokens
        max_request_body_size="never",
        before_send=_scrub_event,
        # Log records are neither events nor breadcrumbs: free-form log text can carry secrets.
        integrations=[
            LoggingIntegration(level=None, event_level=None, sentry_logs_level=None)
        ],
    )
    sentry_sdk.set_tag("service", "cloud-api")
    print("sentry: enabled for cloud-api", file=sys.stderr, flush=True)


def capture(exc: BaseException) -> None:
    """Report an exception the API caught and turned into a generic error answer."""
    if not _enabled():
        return
    import sentry_sdk

    sentry_sdk.capture_exception(exc)
