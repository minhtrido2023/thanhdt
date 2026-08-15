#!/usr/bin/env python3
"""ca_lib.py — read-only BigQuery reader + auditable ISS taxonomy for Sprint 1.

Scope discipline (job Taylor_20260815_114954): this module READS `tav2_bq.corporate_action`
and nothing else writes. No table/view is created; every artifact lands under this directory.

Why a second taxonomy next to `corp_action_lib.py` in the repo root
------------------------------------------------------------------
`corp_action_lib.PRICE_ADJUSTING_ISS` answers ONE production question: "does this event move
the Close/Price ratio on exright_date?" — a binary. Sprint 1 needs a different, finer object:
an event *subtype* (stock dividend vs bonus vs rights vs ESOP vs placement vs convertible),
because a cash-dividend study must be able to say which non-DIV events contaminate its windows
and a later ISS study needs the subtypes separated. The binary is derivable from the subtype
(see `PRICE_ADJUSTING_SUBTYPES`) and a selfcheck asserts the two agree, so this is a refinement,
not a fork.
"""
from __future__ import annotations

import json
import subprocess
import unicodedata

BQ_PROJECT = "lithe-record-440915-m9"
TABLE = f"{BQ_PROJECT}.tav2_bq.corporate_action"
MAX_ROWS = 1_000_000


def bq(sql: str, timeout: int = 600) -> list[dict]:
    """Run read-only SQL through the bq CLI, return list of dict rows.

    `--max_rows` is MANDATORY: the bq CLI silently truncates at 100 rows by default and still
    exits 0 (real incident 2026-08-13, `oshares_live`). A truncated read is indistinguishable
    from a short history unless you ask for the ceiling.
    """
    cmd = [
        "bq", "query", "--use_legacy_sql=false", "--format=json",
        f"--project_id={BQ_PROJECT}", f"--max_rows={MAX_ROWS}", sql,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"bq failed rc={p.returncode}\nSQL:\n{sql}\nSTDERR:\n{p.stderr[-3000:]}")
    out = p.stdout.strip()
    return json.loads(out) if out else []


# --------------------------------------------------------------------------------------------
# ISS taxonomy — every rule keyed on a STORED FIELD VALUE, never on a guess.
# --------------------------------------------------------------------------------------------
# Primary key is `issue_method_code` (a vendor enum: stable, language-free). `issue_method_name_vi`
# is carried as corroborating evidence and as the fallback when the code is absent. Titles are
# NEVER used to assign a subtype — only to spot-check one (see `title_conflicts_subtype`).

# Measured 2026-08-15: `issue_method_code` takes exactly 10 values on 11.722 ISS rows and is
# 1:1 with `issue_method_name_vi` on 9 of them. The 10th, `BBOD` (15 rows), carries a NULL name,
# a NULL title, a NULL description and `exercise_ratio = 0` on every row — there is no field in
# the table that says what it is, so it maps to UNKNOWN by evidence, not by oversight.
ISS_SUBTYPE_BY_METHOD_CODE: dict[str, str] = {
    "DIV": "STOCK_DIVIDEND",       # "Trả Cổ tức bằng Cổ phiếu"  (n=2.651)
    "Bonus": "BONUS",              # "Cổ phiếu thưởng"            (n=1.534)
    "Rights": "RIGHTS",            # "Quyền mua CP cho Cổ đông hiện hữu" (n=2.190)
    "EMPL": "ESOP",                # "Phát hành cho CBCNV"        (n=1.691)
    "PP": "PRIVATE_PLACEMENT",     # "Phát hành riêng lẻ"         (n=3.096)
    "TRANS": "CONVERTIBLE",        # "Chuyển từ trái phiếu chuyển đổi" (n=247)
    "ICRE": "CONVERTIBLE",         # "Phát hành cho trái chủ"     (n=9)
    "PUBL": "AUCTION",             # "Phát hành rộng rãi qua đấu giá"  (n=176)
    "MERGER": "MERGER",            # "Phát hành để sáp nhập"      (n=113)
}
ISS_SUBTYPE_BY_METHOD_NAME: dict[str, str] = {
    # --- accrue a right to EXISTING shareholders => price adjusts on exright_date ---
    "Trả Cổ tức bằng Cổ phiếu": "STOCK_DIVIDEND",
    "Cổ phiếu thưởng": "BONUS",
    "Quyền mua CP cho Cổ đông hiện hữu": "RIGHTS",
    # --- create shares for SOMEONE ELSE => share count rises, price does not adjust ---
    "Phát hành cho CBCNV": "ESOP",
    "Phát hành riêng lẻ": "PRIVATE_PLACEMENT",
    "Chuyển từ trái phiếu chuyển đổi": "CONVERTIBLE",
    "Phát hành cho trái chủ": "CONVERTIBLE",
    "Phát hành rộng rãi qua đấu giá": "AUCTION",
    "Phát hành để sáp nhập": "MERGER",
}

# Subtypes whose exright_date is expected to carry a mechanical price adjustment.
PRICE_ADJUSTING_SUBTYPES = {"STOCK_DIVIDEND", "BONUS", "RIGHTS"}

# Non-ISS event codes map straight to a family; no subtype inference is attempted.
NON_ISS_FAMILY = {
    "DIV": "CASH_DIVIDEND",
    "AIS": "ADDITIONAL_LISTING",
    "NLIS": "NEW_LISTING",
    "SUSP": "SUSPENSION",
    "MOVE": "EXCHANGE_MOVE",
    "MA": "MERGER_ACQUISITION",
}


def _norm(s: str | None) -> str:
    """NFC-normalise + collapse whitespace. Vietnamese diacritics arrive in mixed NFC/NFD forms;
    a raw `==` on a decomposed string silently misses and would inflate UNKNOWN."""
    if not s:
        return ""
    return " ".join(unicodedata.normalize("NFC", s).split())


_NAME_MAP_NORM = {_norm(k): v for k, v in ISS_SUBTYPE_BY_METHOD_NAME.items()}


def classify(event: dict) -> dict:
    """Return {family, subtype, rule, evidence} for one raw row.

    `rule` names the exact decision path so any row in the ledger can be re-derived by hand.
    Unrecognised/blank ISS methods return subtype UNKNOWN — never a guessed bucket. Guessing
    would convert a data gap into a confident-looking label, which is the failure mode this
    whole sprint exists to avoid.
    """
    code = (event.get("event_code") or "").strip()
    if code != "ISS":
        fam = NON_ISS_FAMILY.get(code, "OTHER")
        return {"family": fam, "subtype": fam, "rule": "event_code", "evidence": code or "<null>"}

    mcode = (event.get("issue_method_code") or "").strip()
    mname = _norm(event.get("issue_method_name_vi"))

    if mcode and mcode in ISS_SUBTYPE_BY_METHOD_CODE:
        return {"family": "ISSUANCE", "subtype": ISS_SUBTYPE_BY_METHOD_CODE[mcode],
                "rule": "issue_method_code", "evidence": mcode}
    if mname in _NAME_MAP_NORM:
        return {"family": "ISSUANCE", "subtype": _NAME_MAP_NORM[mname],
                "rule": "issue_method_name_vi", "evidence": mname}
    return {"family": "ISSUANCE", "subtype": "UNKNOWN", "rule": "unmatched",
            "evidence": mcode or mname or "<null>"}


def is_price_adjusting(event: dict) -> bool:
    """Mirror of `corp_action_lib.is_price_adjusting`, derived from the subtype.
    A selfcheck asserts the two agree on every real row — see selfcheck_sprint1.py T1."""
    code = (event.get("event_code") or "").strip()
    if code == "DIV":
        return True
    if code != "ISS":
        return False
    return classify(event)["subtype"] in PRICE_ADJUSTING_SUBTYPES


def num(v) -> float | None:
    """Coerce a BigQuery JSON scalar to float.

    `bq --format=json` renders EVERY numeric as a STRING. A literal `row['exercise_ratio'] == 0`
    is therefore always False even on a zero row — the bug that made the first ledger build
    report 48 unusable ratios instead of ~3.900. Numbers out of this reader are strings until
    something converts them; this is that something.
    """
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# The vendor's `event_title_vi` for an ISS is mechanically assembled as
#   "Phát hành cổ phiếu - " + issue_method_name_vi [+ " tỉ lệ {x}%"]
# so it CANNOT corroborate the subtype — it is the same field restated, and a subtype-vs-title
# agreement rate is vacuous. What the title does add is the RATIO, which is stored nowhere else
# in text form, so it is a genuine independent read on `exercise_ratio`.
_TITLE_RATIO = __import__("re").compile(r"tỉ\s*lệ\s*([0-9]+(?:[.,][0-9]+)?)\s*%")


def title_ratio(event: dict) -> float | None:
    """Ratio (as a fraction, e.g. 0.10 for 'tỉ lệ 10.0%') parsed from the title, or None."""
    m = _TITLE_RATIO.search(_norm(event.get("event_title_vi")))
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ".")) / 100.0
    except ValueError:
        return None
