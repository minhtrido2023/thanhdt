#!/usr/bin/env python3
"""context_watch.py [<agent_id>]

Estimate how full each fleet agent's CURRENT conversation context is, so a long chat never
sneaks up on you. Claude Code auto-compacts each session on its own near the context limit
(built-in, ~90%+); this is the early-warning layer on top — it just READS, it can't compact
another session (companion model). Use it to see who's getting big and warn before the
built-in kicks in.

Per agent: read the newest transcript (.jsonl) in its project dir, take the LAST assistant
turn's usage (input + cache_read + cache_creation ≈ the tokens currently in context), and
compare to the context limit.

  context_watch.py            → table for all enabled agents (exit 1 if any ≥ WARN%)
  context_watch.py <id>       → one line "TOKENS LIMIT PCT" for that agent (for fleet_health)

Env: CTX_LIMIT (default 1000000, the 1M Opus window), CTX_WARN_PCT (default 80).
Never raises; unknown/missing → reported as '-'. Exit 0 unless the table sees a warn-level agent.
"""
import sys, os, json, glob, re

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, ".claude", "projects")
WANTS = os.path.join(HOME, ".config", "systemd", "user", "default.target.wants")
AGENTS_ROOT = "/home/trido/thanhdt/WorkingClaude/mike/agents"

LIMIT = int(os.environ.get("CTX_LIMIT", "1000000"))
WARN = float(os.environ.get("CTX_WARN_PCT", "80"))


def enabled_agents():
    out = []
    for link in sorted(glob.glob(os.path.join(WANTS, "mike@*.service"))):
        b = os.path.basename(link)
        out.append(b[len("mike@"):-len(".service")])
    return out


def newest_transcript(agent):
    """The agent's live session = the most recently modified transcript in its project dir."""
    enc = (AGENTS_ROOT + "/" + agent).replace("/", "-")
    pdir = os.path.join(PROJ, enc)
    files = glob.glob(os.path.join(pdir, "*.jsonl"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def ctx_tokens(tf):
    """Tokens currently in context = last assistant turn's input + cache (read+creation)."""
    last = None
    try:
        with open(tf, encoding="utf-8") as f:
            for line in f:
                if '"usage"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                m = e.get("message")
                if isinstance(m, dict) and m.get("role") == "assistant" and isinstance(m.get("usage"), dict):
                    last = m["usage"]
    except Exception:
        return None
    if not last:
        return None
    return (last.get("input_tokens") or 0) + (last.get("cache_read_input_tokens") or 0) \
        + (last.get("cache_creation_input_tokens") or 0)


def measure(agent):
    tf = newest_transcript(agent)
    if not tf:
        return None
    return ctx_tokens(tf)


def main():
    args = sys.argv[1:]
    if args:                                  # single-agent machine line for fleet_health
        t = measure(args[0])
        if t is None:
            print("- %d -" % LIMIT)
        else:
            print("%d %d %.0f" % (t, LIMIT, 100.0 * t / LIMIT))
        return

    warn = 0
    print("Fleet context usage  (limit=%dk, warn≥%.0f%%, built-in auto-compact ~90%%+)" % (LIMIT // 1000, WARN))
    print("%-14s %-12s %-6s %s" % ("AGENT", "CONTEXT", "USE%", ""))
    print("-" * 48)
    for a in enabled_agents():
        t = measure(a)
        if t is None:
            print("%-14s %-12s %-6s" % (a, "-", "-"))
            continue
        pct = 100.0 * t / LIMIT
        flag = ""
        if pct >= WARN:
            warn = 1
            flag = "  <== getting large (auto-compact will fire soon)"
        print("%-14s %-12s %-6.0f%s" % (a, "%dk/%dk" % (t // 1000, LIMIT // 1000), pct, flag))
    sys.exit(1 if warn else 0)


if __name__ == "__main__":
    main()
