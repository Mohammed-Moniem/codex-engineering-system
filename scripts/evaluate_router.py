#!/usr/bin/env python3
"""Offline regression oracle for the documented engineering router contract."""

from __future__ import annotations

import argparse
import json
import re


ROUTES = {
    "quickplan",
    "plan",
    "wayfinder",
    "grill",
    "debug",
    "triage",
    "review-council",
    "architecture",
}


def route(prompt: str) -> str:
    text = prompt.casefold()
    text = re.sub(r"\b(?:do not|don't|without)\s+(?:use\s+)?[@$][a-z0-9-]+", "", text)
    for name in ("quickplan", "plan", "wayfinder", "grill", "debug", "triage", "review-council", "architecture"):
        if re.search(rf"(?:^|\s)[@$]{re.escape(name)}\b", text):
            return name

    if any(signal in text for signal in ("triage this", "raw bug report", "incoming request", "classify this issue")):
        return "triage"
    if any(signal in text for signal in ("review this", "review the diff", "review this branch", "pull request review")):
        return "review-council"
    if any(signal in text for signal in ("coupling hotspot", "dependency cycle", "architecture debt", "module boundaries")):
        return "architecture"
    if any(signal in text for signal in ("intermittent", "flaky", "regression", "reproduce the failure", "root cause this bug")):
        return "debug"
    if any(signal in text for signal in ("multi-session", "foggy", "unclear across", "cross-service migration", "offline sync", "authentication migration")):
        return "wayfinder"
    if any(signal in text for signal in ("human decision", "stakeholder choice", "clarify the product decision", "bounded design choice")):
        return "grill"
    if any(signal in text for signal in ("fix this typo", "rename this field", "small bounded", "one-line change", "update one string")):
        return "quickplan"
    if any(signal in text for signal in ("where is", "explain this function", "read-only lookup", "find the file")):
        return "direct"
    return "plan"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", nargs="+")
    args = parser.parse_args()
    result = {"route": route(" ".join(args.prompt))}
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
