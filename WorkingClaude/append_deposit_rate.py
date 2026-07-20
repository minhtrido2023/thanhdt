#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
append_deposit_rate.py — append ONE new Big-4 12M deposit-rate anchor to the append-only live
extension data/deposit_rate_vn_events.csv, read by deposit_rate_vn.py::deposit_events_df().

This NEVER edits the 26 frozen historical anchors hardcoded in deposit_rate_vn.py. It is the
write endpoint for the monthly refresh routine, normally run by a human with a confirmed
number (--source manual_verify / *_web / cafef / vietstock).

--source web_crosscheck_auto (added 2026-07-20, user-approved, hardened through 3 rounds of
quant-skeptic REFUTED review — see mike/kb/projects/deposit-rate-autocheck.md for the full
adversarial history, KEEP IT, it is the reason each backstop below exists): refresh_deposit_rate_vn.sh
dispatches an agent (Winston) monthly to WebSearch-crosscheck the Big-4 12M ONLINE rate. A prompt
instruction is NOT a boundary — round 2 proved this by writing 12.00% via a flag combination the
prompt merely asked the agent not to use, and round 3 proved a narrower fix (gating only --force)
still left a wide-open bypass (--source manual_verify needs neither --sources nor --note). The
backstops below are the result and are ALL keyed off CALLER IDENTITY (the JOB_ID env var
dispatch.sh exports into every headless agent's environment), never off a self-declared flag or
--source string the agent itself controls:

1. SOURCE CHOICE ITSELF is gated: when JOB_ID is set, --source MUST be web_crosscheck_auto — every
   other source string (manual_verify, *_web, cafef, vietstock — all human-only) is refused
   outright. An agent cannot escape the checks below by simply claiming to be a different source.
2. --force is refused outright whenever JOB_ID is set, for ANY --source. Combined with (1), there
   is no --source/--force combination a dispatched agent can reach that skips evidence checks or
   overrides the delta guard.
3. PUBLISHER INDEPENDENCE is mechanically checked, not agent-self-reported: --sources must be a
   JSON array of >=2 {"publisher","url","date"} entries whose URLs resolve to >=2 DISTINCT owner
   groups (see SAME_OWNER_GROUPS below — known sister-site clusters, e.g. VCCorp's
   cafef.vn/cafebiz.vn/kenh14.vn/soha.vn/genk.vn/sport5.vn, count as ONE source, not two — round-2
   review's own worked example was an unnoticed same-owner pair). Domain extraction rejects
   unparsable/scheme-less URLs outright (round-3 review showed a bare "cafef.vn/x" silently became
   a "safe" singleton group instead of resolving to the real domain) and collapses subdomains to
   the registered domain.

Refusal messages deliberately do NOT print the override command (round-2 review found the OLD
message taught the blocked party its own bypass — a human resolving the escalation already knows
the runbook path, so printing it only served the party that must not use it).

DELTA GUARD: any write where |--rate − current_deposit_rate()| >= 1.0pp (the same threshold
dcf_refresh_gate.py treats as non-inert) is refused unless --force is passed — and --force is
unavailable to any process with JOB_ID set (see above), so an agent can never write a move this
size under any --source, full stop; it must always escalate to a human, who resolves it
interactively (JOB_ID unset) with --source manual_verify --force.

SCOPE / THREAT MODEL (explicit after 5 rounds of adversarial review, mike/kb/projects/
deposit-rate-autocheck.md — round 5 converged on this framing rather than finding a 6th string-
parsing bug): the --sources owner-group check defends against CARELESS same-owner citation by a
cooperative agent (Winston, under an explicit system-prompt instruction to WebSearch honestly and
cite what it actually found) — the real, expected failure mode. It is NOT a defense against a
malicious caller: nothing here fetches or verifies that a cited URL is real, so two invented
distinct-looking domains would trivially pass. That is an accepted, structural limitation, not an
oversight — closing it would require an actual URL fetch + content check per source, which is a
disproportionate lift for a monthly, NEUTRAL-tilt-only input running inside the same trusted fleet
(not an adversarial third party). Do not chase further string-encoding edge cases (percent-escapes
are rejected outright; non-ASCII/IDN hosts are rejected outright) in the name of defending against
a threat model this mechanism was never meant to cover.

deposit_rate_vn is a LIVE production input (rating_8l.py NEUTRAL-only deposit tilt, daily). Only
anchors with an effective_date strictly newer than the last frozen anchor (2026-06-01) take effect.

Usage (human, interactive):
  python3 append_deposit_rate.py --rate 6.9 --effective 2026-07-01 --source manual_verify \
          [--collected 2026-07-03] [--note "VCB +0.1pp so thang truoc"] [--force]

Usage (agent, web_crosscheck_auto):
  python3 append_deposit_rate.py --rate 6.8 --effective 2026-07-20 --source web_crosscheck_auto \
          --sources '[{"publisher":"CafeF","url":"https://cafef.vn/...","date":"2026-07-07"},
                       {"publisher":"VnExpress","url":"https://vnexpress.net/...","date":"2026-07-16"}]' \
          --note "..."

Idempotent: re-running with an effective_date already present is skipped (unless --force), so a
killed-then-rerun invocation does not duplicate a row.
"""
import argparse
import csv
import json
import os
import sys
import tempfile
import urllib.parse
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "data", "deposit_rate_vn_events.csv")
HEADER = ["effective_date", "deposit_rate", "collected_date", "source", "note"]
VALID_SOURCES = {"vcb_web", "bidv_web", "ctg_web", "agribank_web", "cafef", "vietstock",
                  "manual_verify", "web_crosscheck_auto"}
# Sources where a human did NOT directly eyeball the number (fully agent-driven) — --note is
# mandatory so the cited cross-check evidence is always in the audit trail, not just implied.
SOURCES_REQUIRING_NOTE = {"web_crosscheck_auto"}
# Sources requiring --sources (structured, mechanically-checked publisher independence).
SOURCES_REQUIRING_STRUCTURED_SOURCES = {"web_crosscheck_auto"}
MIN_DISTINCT_OWNERS = 2
MAX_SOURCE_AGE_DAYS = 35  # dispatch prompt asks for ~25 days; a bit of slack, mechanically enforced
MAX_FUTURE_EFFECTIVE_DAYS = 2  # a dispatched agent confirms a rate observed TODAY, never a
# future-effective one — small slack only for timezone/midnight-boundary edge cases

# Known same-owner domain clusters (VN media groups where sister sites republish the same wire
# content — a rate table syndicated across these does NOT count as independent confirmation).
# Extend this list whenever a new same-owner collision is discovered (best-effort, NOT a claim of
# completeness — see docstring); unlisted domains each form their own singleton owner group.
SAME_OWNER_GROUPS = {
    "vccorp": {"cafef.vn", "cafebiz.vn", "kenh14.vn", "soha.vn", "genk.vn", "gamek.vn",
               "afamily.vn", "ttvn.vn", "autopro.com.vn", "sport5.vn"},
}

# Vietnamese multi-label second-level suffixes (registrable domain = last 3 labels, not 2, for
# these — e.g. "vietnamnet.com.vn" and "nld.com.vn" are DIFFERENT registrable domains, both
# ending in .com.vn; collapsing to just "com.vn" would wrongly merge every unrelated .com.vn site
# into one group). Not an exhaustive public-suffix-list, just the ones relevant to VN news/finance.
MULTI_LABEL_SUFFIXES = {"com.vn", "net.vn", "org.vn", "edu.vn", "gov.vn", "biz.vn", "info.vn",
                        "name.vn", "int.vn", "ac.vn", "health.vn", "pro.vn"}


def _registrable_domain(host):
    """host -> registrable domain, handling VN's 3-label suffixes (see MULTI_LABEL_SUFFIXES)."""
    labels = host.split(".")
    if len(labels) >= 3 and ".".join(labels[-2:]) in MULTI_LABEL_SUFFIXES:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:]) if len(labels) >= 2 else host


def _owner_group(url):
    """Registered domain -> owner-group id. Raises ValueError for any URL that doesn't parse to
    a real host — an unparsable/scheme-less URL must NEVER silently become a "safe" singleton
    group (that would let 2 malformed variants of the SAME domain look like 2 distinct owners)."""
    if "%" in url:
        raise ValueError(f"URL '{url}' contains a percent-escape — refuse rather than decode and "
                         f"re-parse (round-5 review: cafef%2Evn vs cafef.vn otherwise looks like "
                         f"2 distinct hosts to a naive string check). Cite the plain URL.")
    parsed = urllib.parse.urlparse(url)
    # .hostname (not .netloc) strips port AND userinfo natively — round-4 review broke .netloc
    # via 'cafef.vn:443' and 'x@cafef.vn', both of which defeated the SAME_OWNER_GROUPS lookup.
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host or not host.isascii():
        raise ValueError(f"URL '{url}' has no parseable ASCII host (missing scheme? IDN/fullwidth "
                         f"host?) — refuse to guess an owner group for it. Cite a plain ASCII URL.")
    if host.startswith("www."):
        host = host[4:]
    base = _registrable_domain(host)
    for group, domains in SAME_OWNER_GROUPS.items():
        if base in domains:
            return group
    return base


def _read_rows():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("effective_date")]


def _valid_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def main():
    ap = argparse.ArgumentParser(description="Append one Big-4 12M deposit-rate anchor (append-only).")
    ap.add_argument("--rate", type=float, required=True, help="Big-4 12M deposit rate, %%/yr (e.g. 6.9)")
    ap.add_argument("--effective", required=True, help="effective date YYYY-MM-DD (rate posted/effective)")
    ap.add_argument("--source", required=True,
                    help="one of: " + " | ".join(sorted(VALID_SOURCES)))
    ap.add_argument("--collected", default=None,
                    help="real collection date YYYY-MM-DD (default: today) — point-in-time marker")
    ap.add_argument("--note", default="", help="free-text note (e.g. 'BIDV +0.2pp')")
    ap.add_argument("--sources", default=None,
                    help='JSON array of {"publisher","url","date"} — REQUIRED for '
                         '--source web_crosscheck_auto, mechanically checked for >=%d distinct '
                         'owner groups (see SAME_OWNER_GROUPS)' % MIN_DISTINCT_OWNERS)
    ap.add_argument("--force", action="store_true",
                    help="append even if this effective_date already exists (default: skip = "
                         "idempotent). REFUSED outright when JOB_ID env is set (i.e. running "
                         "inside a dispatched headless agent) — human-only override.")
    args = ap.parse_args()

    # --- caller-identity gate: binds to WHO is running, not to any self-declared flag/string ---
    # Round-3 review found the round-2 fix bound ONLY --force to caller identity, leaving the
    # simplest bypass wide open: an agent (JOB_ID set) could just pass --source manual_verify
    # (a string it fully controls) to skip --sources/--note entirely and write with no evidence
    # at all, so long as the delta stayed under the guard and --force was never needed. Fix: when
    # JOB_ID is set, the source CHOICE itself is gated, not just --force — a dispatched agent may
    # ONLY ever use --source web_crosscheck_auto (the one path with full mechanical checks below).
    # Every other source string is human-only and refused outright for any JOB_ID-having process.
    is_dispatched_agent = os.environ.get("JOB_ID") is not None  # PRESENCE, not truthiness — an
    # empty-but-set JOB_ID="" must still count as "running inside a dispatch" (round-4 review
    # found bool("") == False slipped straight through the gate).
    if is_dispatched_agent and args.force:
        sys.exit("ERROR: --force is refused — this process has JOB_ID set (running inside a "
                 "dispatched headless agent). This override is human-only; resolve escalations "
                 "interactively.")
    if is_dispatched_agent and args.source != "web_crosscheck_auto":
        sys.exit(f"ERROR: --source '{args.source}' is refused — this process has JOB_ID set "
                 f"(running inside a dispatched headless agent). A dispatched agent may ONLY use "
                 f"--source web_crosscheck_auto (the mechanically-checked path); every other "
                 f"source is human-only. Escalate for interactive human review instead.")

    # --- validate ---
    try:
        eff = _valid_date(args.effective)
    except ValueError:
        sys.exit(f"ERROR: --effective '{args.effective}' is not YYYY-MM-DD")
    real_today = date.today().isoformat()
    # Round-8 review: current_deposit_rate() itself is now fixed (deposit_rate_vn.py resolves
    # asof=None to real today, not "last row by time"), which closes the production impact of a
    # bad --effective regardless of how it entered the CSV. This is defense-in-depth on the writer
    # side too, same caller-identity pattern as --force/--source/--collected: an agent's --effective
    # must be within a sane window of today, never an arbitrary/typo'd year.
    if is_dispatched_agent:
        eff_age_days = (eff - _valid_date(real_today)).days
        # Asymmetric on purpose (round-8 review): a dispatched agent confirms a rate observed
        # TODAY, so it has no legitimate reason to backdate far (>35d, matches source recency) OR
        # to write a future effective_date at all (a forward anchor is a deliberate human decision
        # about when a just-announced future change takes effect, not something to confirm live).
        if eff_age_days > MAX_FUTURE_EFFECTIVE_DAYS or eff_age_days < -MAX_SOURCE_AGE_DAYS:
            sys.exit(f"ERROR: --effective '{args.effective}' is {eff_age_days} days from today "
                     f"({real_today}) — refused for a dispatched agent (max "
                     f"{MAX_FUTURE_EFFECTIVE_DAYS} days forward, {MAX_SOURCE_AGE_DAYS} days "
                     f"back). A typo'd/fabricated effective_date has an outsized consequence "
                     f"(pins or pre-empts the live series) — escalate for human review instead.")
    collected = args.collected or real_today
    try:
        _valid_date(collected)
    except ValueError:
        sys.exit(f"ERROR: --collected '{collected}' is not YYYY-MM-DD")
    # Round-7 review: the recency check must never anchor to a value the agent itself supplies —
    # --collected was exactly that, and a falsified --collected (e.g. 1999-01-20) revived the
    # stale-source exploit fix 1 was meant to close. Same caller-identity treatment as --force and
    # --source above: a dispatched agent gets NO say over --collected at all, full stop.
    if is_dispatched_agent and collected != real_today:
        sys.exit(f"ERROR: --collected '{collected}' is refused — this process has JOB_ID set, so "
                 f"--collected may ONLY be the real current date ({real_today}). A dispatched "
                 f"agent cannot supply its own collection date.")
    if not (0.0 < args.rate < 30.0):
        sys.exit(f"ERROR: --rate {args.rate} out of sane range (0, 30) — refuse to write")
    if args.source not in VALID_SOURCES:
        sys.exit(f"ERROR: --source '{args.source}' not in {sorted(VALID_SOURCES)}")
    if args.source in SOURCES_REQUIRING_NOTE and not args.note.strip():
        sys.exit(f"ERROR: --source {args.source} requires a non-empty --note citing the "
                 f"cross-checked evidence (URLs/dates) — refuse to write without provenance.")

    # --- publisher independence: mechanically checked, not agent-self-reported ---
    if args.source in SOURCES_REQUIRING_STRUCTURED_SOURCES:
        if not args.sources:
            sys.exit(f"ERROR: --source {args.source} requires --sources (JSON array of "
                     f">= {MIN_DISTINCT_OWNERS} {{publisher,url,date}} entries) — refuse to "
                     f"write without a mechanically-checkable evidence list.")
        try:
            sources = json.loads(args.sources)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: --sources is not valid JSON: {e}")
        if not isinstance(sources, list) or len(sources) < MIN_DISTINCT_OWNERS:
            sys.exit(f"ERROR: --sources must be a JSON array with >= {MIN_DISTINCT_OWNERS} "
                     f"entries, got {sources!r}")
        urls = [s.get("url", "") for s in sources if isinstance(s, dict)]
        if len(urls) != len(sources) or not all(urls):
            sys.exit("ERROR: every --sources entry must be an object with a non-empty 'url'.")
        try:
            owner_groups = {_owner_group(u) for u in urls}
        except ValueError as e:
            sys.exit(f"ERROR: {e}")
        if len(owner_groups) < MIN_DISTINCT_OWNERS:
            sys.exit(f"ERROR: --sources resolve to only {len(owner_groups)} distinct owner "
                     f"group(s) ({sorted(owner_groups)}) — need >= {MIN_DISTINCT_OWNERS}. "
                     f"Sister sites under the same media group (see SAME_OWNER_GROUPS) do not "
                     f"count as independent confirmation. Refuse to write.")
        # --- recency: the JSON schema demands a 'date' per source (dispatch prompt requires
        # ~25 days) but round-6 review found the field was parsed and never actually read — an
        # honest agent citing 2 genuinely-independent but STALE evergreen pages passed silently.
        # Mechanically enforce it here instead of trusting the prompt.
        # Anchor recency to the REAL system clock, never to --collected — round-7 review showed
        # anchoring to an agent-suppliable flag let a falsified --collected revive the exploit
        # fix 1 was meant to close (same class of bug as gating --force/--source on a self-
        # declared string instead of caller identity).
        today_d = _valid_date(real_today)
        for s in sources:
            raw_date = s.get("date", "")
            try:
                src_date = _valid_date(raw_date)
            except ValueError:
                sys.exit(f"ERROR: --sources entry has invalid/missing 'date' ('{raw_date}') — "
                         f"must be YYYY-MM-DD. Refuse to write without a checkable recency claim.")
            age_days = (today_d - src_date).days
            if age_days < 0 or age_days > MAX_SOURCE_AGE_DAYS:
                sys.exit(f"ERROR: --sources entry dated {raw_date} is {age_days} days from "
                         f"today ({real_today}) (max {MAX_SOURCE_AGE_DAYS}, or in the future) "
                         f"— too stale/invalid to count as current confirmation. Refuse to write.")

    # --- delta guard: bounds a single write AND cumulative drift since the last HUMAN write ---
    # Round-6 review found comparing only against current_deposit_rate() lets a chain of
    # consecutive sub-1.0pp agent writes drift the live input arbitrarily far with no single step
    # ever tripping the guard. Fix: also compare against the last HUMAN-sourced anchor (source not
    # in SOURCES_REQUIRING_STRUCTURED_SOURCES) — or the last frozen anchor if no CSV row is
    # human-sourced yet, since those 26 anchors are hardcoded by a human in deposit_rate_vn.py.
    rows = _read_rows()
    sys.path.insert(0, HERE)
    import deposit_rate_vn
    current = deposit_rate_vn.current_deposit_rate()
    NONINERT_DELTA_PP = 1.0  # same threshold dcf_refresh_gate.py treats as non-inert
    human_rows = sorted(
        (r for r in rows if r.get("source") not in SOURCES_REQUIRING_STRUCTURED_SOURCES),
        key=lambda r: r["effective_date"])
    last_human_rate = (float(human_rows[-1]["deposit_rate"]) if human_rows
                       else deposit_rate_vn.DEPOSIT_EVENTS[-1][1])
    delta_vs_current = abs(args.rate - current)
    delta_vs_human = abs(args.rate - last_human_rate)
    if max(delta_vs_current, delta_vs_human) >= NONINERT_DELTA_PP and not args.force:
        sys.exit(f"ERROR: rate {args.rate:g}% differs from current {current:.2f}% by "
                 f"{delta_vs_current:.2f}pp and from the last human-confirmed rate "
                 f"{last_human_rate:.2f}% by {delta_vs_human:.2f}pp (>= {NONINERT_DELTA_PP}pp on "
                 f"either) — refuse to write. A move this size needs a human to review and "
                 f"resolve the escalation interactively (--force is human-only, see above — it "
                 f"is never available to a dispatched agent process regardless of --source).")

    existing = {r["effective_date"] for r in rows}
    if args.effective in existing and not args.force:
        print(f"SKIP: effective_date {args.effective} already present (use --force to override). "
              f"No write — CSV unchanged.")
        return 0

    if args.force:
        rows = [r for r in rows if r["effective_date"] != args.effective]
    new_row = {"effective_date": args.effective, "deposit_rate": f"{args.rate:g}",
               "collected_date": collected, "source": args.source, "note": args.note}
    rows.append(new_row)

    # --- atomic rewrite: temp file in same dir -> os.replace (survives a mid-write kill) ---
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CSV_PATH), prefix=".dep_", suffix=".csv")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, CSV_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

    # --- verify reload through the real consumer path ---
    sys.path.insert(0, HERE)
    import importlib
    import deposit_rate_vn
    importlib.reload(deposit_rate_vn)  # pick up the just-written CSV
    ev = deposit_rate_vn.deposit_events_df()
    frozen_max = max(datetime.strptime(d, "%Y-%m-%d").date()
                     for d, _ in deposit_rate_vn.DEPOSIT_EVENTS)
    cur = deposit_rate_vn.current_deposit_rate()
    print(f"OK: appended {args.effective} = {args.rate:g}% (source={args.source}, collected={collected}).")
    print(f"    deposit_events_df() now has {len(ev)} anchors; current_deposit_rate() = {cur:.2f}%.")
    entered = (ev["time"].dt.date == eff).any()
    if not entered:
        print(f"    WARNING: {eff} did NOT enter the live series — deposit_events_df() only appends "
              f"anchors newer than the last frozen anchor {frozen_max}. Row saved to CSV but INERT "
              f"until an effective_date > {frozen_max} is added.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
