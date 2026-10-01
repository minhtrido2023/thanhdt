# -*- coding: utf-8 -*-
"""
cctg_rate_vn.py — Big-4 (VCB/BIDV/CTG/Agribank) CHỨNG CHỈ TIỀN GỬI (CCTG) rate, 6-month tenor.

NEW series, bootstrapped 2026-10-01 per user directive ("CCTG đưa vào model làm nguồn lãi proxy
nếu lãi suất cao hơn gửi tiết kiệm"). SEPARATE from deposit_rate_vn.py's Big-4 12M term-deposit
series — NEVER merges into or overwrites it. Combine the two only through
deposit_rate_vn.effective_deposit_rate(), which takes max(Big-4 12M, this CCTG series) — never
average, never silently replace one with the other.

Legal/instrument context (legal-vn secondary-source summary relayed in the 2026-10-01 user
directive, NOT independently re-verified this session -- re-verify with legal-vn before citing in
a client-facing document): CCTG ≈ term deposit for deposit-insurance purposes (Luật 111/2025, hạn
mức bảo hiểm 350 triệu VND), lãi CCTG được miễn thuế TNCN giống tiền gửi tiết kiệm, và lãi suất kỳ
hạn >=6 tháng do thị trường quyết định (không trần SBV). Vẫn là MỘT CÔNG CỤ KHÁC VỀ KỲ HẠN so với
sổ tiết kiệm 12 tháng: đây là lý do dùng max(), không gộp mù hai chuỗi khác kỳ hạn thành một.

Tenor mismatch (must NOT be papered over): deposit_rate_vn.py's series is **12-month**; this
series is **6-month**. A 6M rate sitting above a 12M rate is itself a market signal (inverted
curve / banks bidding up short tenor for liquidity) — effective_deposit_rate() surfacing that via
max() is intentional, not a bug, but any report citing the number must say which tenor is driving
it (see deposit_rate_vn.effective_deposit_rate()'s `driver` field).

First anchor only so far:
  - 2026-09-30: Big-4 CCTG 6-thang = 7.5%/nam (VietnamNet, 30/09/2026; mot so NH co phan toi 9.4%,
    nhung chuoi nay CHỈ theo dõi nhóm Big-4 để nhất quán với deposit_rate_vn.py's Big-4 scope).

Append-only: no observation before the first anchor's effective_date -> current_cctg_rate()
returns None (NOT an error, NOT a forward/backward guess) -- any backtest run before this file
existed, or any asof earlier than 2026-09-30, is BYTE-IDENTICAL to a world where this module never
existed (effective_deposit_rate() falls back to the Big-4 12M series alone whenever this returns
None). Future anchors go in `data/cctg_rate_vn_events.csv` (same append-only CSV pattern as
deposit_rate_vn.py's `_EVENTS_CSV` -- gitignored, never committed, forward-fill only).
"""
import os
import pandas as pd

CCTG_EVENTS = [
    ("2026-09-30", 7.5),
]

# Same sanity fence as deposit_rate_vn.py's Big-4 guard (0.5%..30%) -- duplicated, not imported,
# to avoid a circular import (deposit_rate_vn.py imports FROM this module).
RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 30.0

_EVENTS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cctg_rate_vn_events.csv")


def cctg_events_df():
    ev = pd.DataFrame(CCTG_EVENTS, columns=["time", "cctg_rate"])
    ev["time"] = pd.to_datetime(ev["time"])
    if os.path.exists(_EVENTS_CSV):
        try:
            extra = pd.read_csv(_EVENTS_CSV, usecols=["effective_date", "cctg_rate"])
        except pd.errors.EmptyDataError:
            extra = None
        except pd.errors.ParserError:
            raise  # corrupt CSV -> surface loudly, same policy as deposit_rate_vn.py (2026-10-01)
        except ValueError:
            extra = None
        if extra is not None and len(extra):
            extra = extra.rename(columns={"effective_date": "time"})
            extra["time"] = pd.to_datetime(extra["time"], errors="coerce")
            extra["cctg_rate"] = pd.to_numeric(extra["cctg_rate"], errors="coerce")
            extra = extra.dropna(subset=["time", "cctg_rate"])
            extra = extra[extra["time"] > ev["time"].max()]
            if len(extra):
                ev = pd.concat([ev, extra[["time", "cctg_rate"]]], ignore_index=True)
    return ev.sort_values("time").reset_index(drop=True)


def current_cctg_rate(asof=None):
    """Returns (rate_pct, last_date) or (None, None) if no CCTG observation exists at/before asof
    (in particular: any asof before 2026-09-30). asof=None means TODAY (see deposit_rate_vn's
    current_deposit_rate() docstring for why this must anchor to the real clock, not just the
    series' own last row)."""
    ev = cctg_events_df()
    asof_ts = pd.Timestamp.today().normalize() if asof is None else pd.to_datetime(asof)
    avail = ev[ev.time <= asof_ts]
    if avail.empty:
        return None, None
    last_date = avail.iloc[-1]["time"]
    rate_pct = float(avail.iloc[-1]["cctg_rate"])
    return rate_pct, last_date


def current_cctg_rate_checked(asof=None):
    """Same as current_cctg_rate() but makes CCTG-side problems VISIBLE to the caller instead of
    letting them disappear into "no CCTG data, fall back to Big-4 silently" -- added 2026-10-01
    per quant-skeptic round-2 fix 1. Before this, every CCTG-side failure mode (a corrupt/
    unparseable CSV, an out-of-range typo'd value e.g. a fraction-vs-percent slip) was swallowed by
    macro_killswitch_a_status()'s bare `except Exception: pass` around the CCTG overlay call --
    degrading a fail-CLOSED gate into fail-OPEN on the Big-4-only reading whenever the CCTG side
    broke, asymmetric with how every Big-4-side failure in that same function is handled (fail-
    closed with an explicit reason). This function centralizes the validation so every caller
    (macro_killswitch_a_status, effective_deposit_rate) gets the same symmetric treatment.

    Returns (rate_pct|None, date|None, error|None):
      - error is a short diagnostic string (rate_pct/date forced to None) when: (a)
        cctg_events_df() raises (corrupt CSV -- same loud-propagation policy as
        deposit_rate_vn.deposit_events_df()'s ParserError handling), or (b) the raw value is
        outside the sanity fence [RATE_MIN_PCT, RATE_MAX_PCT].
      - error is None (rate_pct/date may legitimately still be None) when there is simply no CCTG
        observation at/before asof -- that is NOT an error, it is the normal pre-anchor state
        (any asof before 2026-09-30) and callers must keep treating it as silent Big-4 fallback."""
    try:
        rate_pct, date = current_cctg_rate(asof)
    except Exception as exc:
        return None, None, f"cctg error: {exc!r}"
    if rate_pct is None:
        return None, None, None
    if not (RATE_MIN_PCT <= rate_pct <= RATE_MAX_PCT):
        return None, None, (f"cctg rate_pct={rate_pct!r} ngoài khoảng hợp lệ "
                             f"[{RATE_MIN_PCT},{RATE_MAX_PCT}]")
    return rate_pct, date, None
