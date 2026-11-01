#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Funnel 8L v2 — bộ CHỌN mã due diligence mỗi ngày + nhật ký chọn PIT + cổng trần DD (fail-closed).

User duyệt 2026-11-01 20:05 ICT (job Taylor_20261101_130719). Tham số KHOÁ theo PREREG (ghi TRƯỚC khi
chạy trên dữ liệu thật, commit cf37e8fa7):
  agents/Taylor/research/discretionary_dd_pick_v2_20261101/PREREG.md
Đổi tham số = PREREG mới; KHÔNG re-tune theo kết quả.

KHÔNG phải engine mới: pool = vũ trụ chất lượng của funnel (`quality_mask` + loại trừ `load_exclusions`),
V = `dcf_valuation.fair_value` (khung mặc định domestic_v2), E = quý mới nhất PIT của `load_financials`
(cùng quy tắc làn C), mùa BCTC = `fa_ratings_earnings_window_daily.sh --check`.

Bộ chọn chỉ SINH ĐỀ XUẤT cho Mike (tầng nhẹ); KHÔNG dispatch DD, KHÔNG mua/size. Sổ claim
`data/discretionary_dd_ledger.jsonl` là cổng cơ học trần DD: Mike/agent gọi
    discretionary_dd_pick.py --claim TICKER --tier light|full [--by Mike] [--job JOB]
TRƯỚC khi dispatch; rc=2 ⇒ hết suất / sổ hỏng / không xác định được ⇒ KHÔNG dispatch.
    discretionary_dd_pick.py --slots            # in suất còn lại hôm nay (ICT)
"""

import argparse
import contextlib
import datetime as dt
import fcntl
import io
import json
import os
import re
import subprocess
import sys
import threading

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discretionary_candidate_funnel as F  # noqa: E402

ICT = F.ICT
PREREG = "agents/Taylor/research/discretionary_dd_pick_v2_20261101/PREREG.md"

# --- PREREG §2 (khoá) ---
W_V, W_E, W_R = 0.50, 0.30, 0.20
DCF_NA_HAIRCUT = 0.8              # mã DCF không tính được: V = phân vị earn_yield trong route × 0,8
FRESH_DAYS = 45                   # quý mới nhất biết trong 45 ngày lịch trước asof ⇒ "vừa ra"
Q_GOOD, Q_MID, Q_BAD = 1.0, 0.6, 0.3
CFO_NP_GOOD = 0.5
YOY_LOW_BASE = 3.0                # YoY > 300% ⇒ nền thấp/lãi một lần
R_SCORE = {1: 1.0, 2: 0.67, 3: 0.33}
# --- PREREG §1, §3, §4, §5 ---
DD_COOLDOWN_DAYS = 90
TOP_K = 8
CAP = {True: {"light": ("day", 1), "full": ("day", 1)},        # mùa BCTC
       False: {"light": ("week", 1), "full": ("week", 2)}}     # ngoài mùa
ESCALATE_MOS = 0.25
LIVE_DEADLINE_S = 40              # trần cứng DCF live (cron funnel timeout 120s) — quá ⇒ fail-soft

WINDOW_GATE = os.path.join(F.MIKE_ROOT, "bin", "fa_ratings_earnings_window_daily.sh")
EXEC_DIR = os.path.join(F.DATA_DIR, "execution_logs")
ACCOUNTS = ("SpaceX", "ZaloPay")
RESEARCH_DIR = os.path.join(F.MIKE_ROOT, "agents", "Taylor", "research")
PRICE_CACHE_DIR = os.path.join(F.DATA_DIR, "bq_cache", "ticker")

LOG_COLS = ["asof", "rank", "ticker", "route", "rating", "score", "V", "E", "R", "mos", "dcf_ok",
            "fv_ps", "price", "price_date", "release_date", "g_yoy", "cfo_np", "q", "labels", "lanes",
            "season", "picked", "escalate_full", "reason", "logged_at"]


def pick_paths(base_dir=F.DATA_DIR):
    return {"log": os.path.join(base_dir, "discretionary_pick_log.csv"),
            "ledger": os.path.join(base_dir, "discretionary_dd_ledger.jsonl")}


@contextlib.contextmanager
def file_lock(path):
    """flock độc quyền trên `<path>.lock` (file riêng, không bao giờ bị đọc như dữ liệu). Đóng fd ⇒ nhả
    khóa kể cả khi tiến trình bị kill. Tuần tự hóa read-check-append giữa NHIỀU tiến trình."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fd = os.open(path + ".lock", os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def append_atomic(path, text):
    """Một lần os.write() lên fd O_APPEND ⇒ không xen kẽ/không dòng dở giữa các tiến trình; fsync."""
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        b = text.encode("utf-8")
        n = os.write(fd, b)
        if n != len(b):
            raise OSError(f"ghi dở {n}/{len(b)} byte vào {path}")
        os.fsync(fd)
    finally:
        os.close(fd)


def with_deadline(fn, secs):
    """Chạy fn() trong thread daemon, chờ tối đa `secs`. Quá hạn ⇒ TimeoutError (thread bỏ lại, daemon nên
    không giữ tiến trình sống)."""
    box = {}

    def _t():
        try:
            box["v"] = fn()
        except BaseException as e:                          # noqa: BLE001
            box["e"] = e
    th = threading.Thread(target=_t, daemon=True)
    th.start()
    th.join(secs)
    if th.is_alive():
        raise TimeoutError(f"quá trần {secs}s")
    if "e" in box:
        raise box["e"]
    return box["v"]


# ----------------------------------------------------------------------------- nguồn phụ
def in_season(d, gate=WINDOW_GATE):
    """(bool, note). Tái dùng cổng mùa BCTC của cron re-rate. Lỗi/đầu ra lạ ⇒ NGOÀI mùa (chặt hơn)."""
    try:
        out = subprocess.run(["bash", gate, "--check", d.isoformat()], capture_output=True,
                             text=True, timeout=30)
        s = out.stdout.strip()
    except Exception as e:                                  # noqa: BLE001
        return False, f"cổng mùa lỗi ({type(e).__name__}: {e}) ⇒ coi NGOÀI mùa"
    if out.returncode == 0 and s == "RUN":
        return True, "mùa BCTC"
    if out.returncode == 0 and s.startswith("SKIP"):
        return False, "ngoài mùa"
    return False, f"cổng mùa trả lạ rc={out.returncode} '{s[:80]}' {out.stderr.strip()[:120]} ⇒ coi NGOÀI mùa"


def held_and_excluded(exec_dir=EXEC_DIR):
    """(held, excluded_tickers, warnings) từ active_nav_<acct>.json. Thiếu/hỏng file ⇒ cảnh báo (không
    biết mã đang giữ ⇒ đề xuất vẫn chạy nhưng Mike phải tự loại — cảnh báo hiện ở khối 08:00)."""
    held, excl, warns = set(), set(), []
    for a in ACCOUNTS:
        p = os.path.join(exec_dir, f"active_nav_{a}.json")
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            excl |= {str(t) for t in d.get("excluded_tickers") or []}
            for pos in d.get("positions") or []:
                if float(pos.get("qty") or 0) > 0:
                    held.add(str(pos["ticker"]))
        except Exception as e:                              # noqa: BLE001
            warns.append(f"bộ chọn: không đọc được {p} ({type(e).__name__}) — CHƯA loại mã đang giữ {a}")
    return held, excl, warns


def read_ledger(path):
    """List claim. File không có ⇒ []. Dòng hỏng ⇒ raise (fail-closed: không đếm được suất)."""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            rec = json.loads(line)                          # hỏng ⇒ JSONDecodeError
            if not {"date", "ticker", "tier"} <= set(rec):
                raise ValueError(f"{path}:{i} thiếu khoá date/ticker/tier")
            dt.date.fromisoformat(rec["date"])
            out.append(rec)
    return out


def read_pick_log(path):
    if not os.path.exists(path):
        return pd.DataFrame(columns=LOG_COLS)
    df = pd.read_csv(path, dtype={"asof": str, "ticker": str})
    if len(df) and "logged_at" in df:
        # Khử trùng theo asof: nếu 1 asof bị ghi >1 lần (chạy song song cũ / lỗi), giữ ĐÚNG lô ghi đầu tiên.
        first = df.groupby("asof")["logged_at"].transform("min")
        df = df[df["logged_at"] == first].reset_index(drop=True)
    return df


def recent_dd(asof, log_df, ledger, research_dir=RESEARCH_DIR, days=DD_COOLDOWN_DAYS, upto=None):
    """Mã đã ĐỀ XUẤT (picked) / claim / có thư mục dd_<MÃ>_<YYYYMMDD> trong [asof − days, upto].
    upto = ngày CHẠY (≥ asof): DD làm sau asof nhưng trước lúc chạy đã là sự thật đã biết (ca thật
    HPG DD 31/10, asof 30/10)."""
    lo = asof - dt.timedelta(days=days)
    asof = max(asof, upto or asof)
    out = set()
    if len(log_df):
        p = log_df[log_df["picked"].astype(str).str.lower().isin(["true", "1"])]
        for t, a in zip(p["ticker"], p["asof"]):
            if lo <= dt.date.fromisoformat(a) <= asof:
                out.add(t)
    for r in ledger:
        if lo <= dt.date.fromisoformat(r["date"]) <= asof:
            out.add(r["ticker"])
    if os.path.isdir(research_dir):
        for n in os.listdir(research_dir):
            parts = n.split("_")      # dd_X_20261015 · dd_blind2_X_20261015 · dd_X_reweight_20261015
            if len(parts) >= 3 and parts[0] == "dd" and len(parts[-1]) == 8 and parts[-1].isdigit():
                try:
                    d = dt.datetime.strptime(parts[-1], "%Y%m%d").date()
                except ValueError:
                    continue
                if lo <= d <= asof:
                    out.update(x for x in parts[1:-1] if re.fullmatch(r"[A-Z][A-Z0-9]{2,3}", x))
    return out


def prices_at(tickers, asof, cache_dir=PRICE_CACHE_DIR):
    """{ticker: (Price chưa điều chỉnh, phiên)} phiên gần nhất ≤ asof trong cache (sync 23:45 ⇒ lúc
    19:37 thường là T-1 — phiên ghi rõ trong log)."""
    import pyarrow.parquet as pq
    frames = []
    for y in (asof.year - 1, asof.year):
        p = os.path.join(cache_dir, f"{y}.parquet")
        if os.path.exists(p):
            frames.append(pq.read_table(p, columns=["ticker", "time", "Price"],
                                        use_threads=False).to_pandas(use_threads=False))
    if not frames:
        return {}
    px = pd.concat(frames)
    px["time"] = pd.to_datetime(px["time"])
    px = px[px["ticker"].isin(set(tickers)) & (px["time"] <= pd.Timestamp(asof)) & (px["Price"] > 0)]
    last = px.sort_values("time").groupby("ticker").tail(1)
    return {t: (float(p), d.date()) for t, p, d in zip(last["ticker"], last["Price"], last["time"])}


def _dcf_engine():
    sys.path.insert(0, F.WC_ROOT)
    cwd = os.getcwd()
    import dcf_valuation as D                                # import đổi cwd (os.chdir) ⇒ trả lại
    os.chdir(cwd)
    return D


# ----------------------------------------------------------------------------- chấm điểm
def _pct(s):
    return s.rank(pct=True, method="average")


def score_pool(rating, fin, cands, banned, forensic, insider, held, excl, recent, asof, prices,
               dcf_fn=None):
    """DataFrame pool đã chấm điểm (PREREG §1-2), sắp theo score giảm dần. `dcf_fn(ticker, price)` ⇒
    dict kiểu fair_value (tiêm được cho selfcheck); None ⇒ dcf_valuation số CP quý (fin-path, nhanh)."""
    df = F.growth_cols(rating, fin)
    df = df[F.quality_mask(df)].copy()
    blocked = banned | set(forensic) | set(insider) | held | excl | recent
    why = {}
    for t in df["ticker"]:
        r = [n for n, s in (("BANNED", banned), ("forensic", forensic), ("insider", insider),
                            ("đang giữ", held), ("excluded", excl), (f"DD<{DD_COOLDOWN_DAYS}d", recent))
             if t in s]
        if r:
            why[t] = ",".join(r)
    dropped = {t: why[t] for t in df["ticker"] if t in blocked}
    df = df[~df["ticker"].isin(blocked)].reset_index(drop=True)
    if df.empty:
        return df, dropped

    if dcf_fn is None:
        D = _dcf_engine()
        dfin = D._load_financials()
        last = dfin[dfin["time"] <= pd.Timestamp(asof)].groupby("ticker").tail(1).set_index("ticker")

        def dcf_fn(t, p):
            os_ = last["OShares"].get(t)
            return D.fair_value(t, str(asof), price=p, fin=dfin,
                                oshares=float(os_) if os_ is not None and pd.notna(os_) else None)
    mos, fv, ok, pr, pdt, rob = [], [], [], [], [], []
    for t in df["ticker"]:
        p, d = prices.get(t, (None, None))
        r = dcf_fn(t, p) if p else {"ok": False}
        good = bool(r.get("ok")) and r.get("margin_of_safety") is not None
        mos.append(r.get("margin_of_safety") if good else np.nan)
        fv.append(r.get("fair_value_ps") if good else np.nan)
        ok.append(good)
        rob.append(_robust(r, p) if good else False)
        pr.append(p)
        pdt.append(str(d) if d else None)
    df["mos"], df["fv_ps"], df["dcf_ok"], df["price"], df["price_date"], df["robust"] = (
        mos, fv, ok, pr, pdt, rob)

    # V
    v = pd.Series(0.0, index=df.index)
    okm = df["dcf_ok"]
    if okm.any():
        v[okm] = _pct(df.loc[okm, "mos"].astype(float))
    na = ~okm & df["earn_yield"].notna()
    if na.any():
        v[na] = df[na].groupby("route")["earn_yield"].transform(_pct) * DCF_NA_HAIRCUT
    df["V"] = v

    # E
    j = fin.reindex(df["ticker"]) if fin is not None else None
    known = pd.to_datetime(j["known"]).to_numpy() if j is not None else np.full(len(df), np.datetime64("NaT", "ns"))   # không có tài chính ⇒ không BCTC mới ⇒ E=0 (§29)
    df["release_date"] = [None if pd.isna(k) else str(pd.Timestamp(k).date()) for k in known]
    age = (pd.Timestamp(asof) - pd.to_datetime(pd.Series(known, index=df.index))).dt.days
    p0 = j["NP_P0"].to_numpy(dtype=float) if j is not None else np.full(len(df), np.nan)
    p4 = j["NP_P4"].to_numpy(dtype=float) if j is not None else np.full(len(df), np.nan)
    fresh = (age <= FRESH_DAYS).to_numpy() & (p0 > 0)
    low_base = fresh & (((df["g_yoy"].astype(float) > YOY_LOW_BASE).to_numpy())
                        | ((p4 <= 0) & (p0 > 0)))
    g_rank = df["g_yoy"].astype(float).where(~((p4 <= 0) & (p0 > 0)), np.inf)   # nền âm ⇒ đỉnh hạng
    e_pct = pd.Series(0.0, index=df.index)
    if fresh.any():
        e_pct[fresh] = _pct(g_rank[fresh].fillna(-np.inf))
    cfo = pd.to_numeric(df.get("cfo_np"), errors="coerce") if "cfo_np" in df else pd.Series(np.nan, index=df.index)
    q = np.where(cfo >= CFO_NP_GOOD, Q_GOOD, np.where(cfo < 0, Q_BAD, Q_MID))
    q = np.where(low_base, Q_BAD, q)
    df["q"] = np.where(fresh, q, np.nan)
    df["cfo_np"] = cfo
    df["E"] = np.where(fresh, e_pct * q, 0.0)
    df["R"] = df["rating"].map(R_SCORE).fillna(0.0)
    df["score"] = W_V * df["V"] + W_E * df["E"] + W_R * df["R"]

    lanes = cands.groupby("ticker")["lane"].apply(lambda s: "".join(sorted(set(s)))) if len(cands) else {}
    df["lanes"] = df["ticker"].map(lambda t: lanes.get(t, "") if len(cands) else "")
    lab = []
    for i, r in df.iterrows():
        x = []
        if not r["dcf_ok"]:
            x.append("dcf_na")
        if low_base[i]:
            x.append("nen_thap")
        if fresh[i]:
            x.append("bctc_moi")
        if "A" in r["lanes"]:
            x.append("lech_gia")
        if r["price_date"] and r["price_date"] != str(asof):
            x.append(f"gia_phien_{r['price_date']}")
        lab.append("|".join(x))
    df["labels"] = lab
    df["escalate_full"] = df["dcf_ok"] & (df["mos"] >= ESCALATE_MOS) & df["robust"] & ~pd.Series(low_base, index=df.index)
    df = df.sort_values(["score", "mos", "ticker"], ascending=[False, False, True],
                        na_position="last").reset_index(drop=True)
    return df, dropped


def _robust(r, px):
    try:
        D = _dcf_engine()
        return bool(D.classify_dcf(r.get("margin_of_safety"), r.get("sensitivity"), px)[1])
    except Exception:                                       # noqa: BLE001 — không xác định ⇒ không robust
        return False


def iso_week(d):
    y, w, _ = d.isocalendar()
    return (y, w)


def pick_allowed(asof, season, log_df):
    """(ok, reason). Mùa: 1 pick/asof. Ngoài mùa: 1 pick/tuần ISO (pick ở asof KHÁC trong cùng tuần ⇒ chặn)."""
    if not len(log_df):
        return True, ""
    p = log_df[log_df["picked"].astype(str).str.lower().isin(["true", "1"])]
    others = [dt.date.fromisoformat(a) for a in p["asof"] if a != str(asof)]
    if not season:
        same = [a for a in others if iso_week(a) == iso_week(asof)]
        if same:
            return False, f"ngoài mùa: tuần này đã đề xuất ({same[-1]})"
    return True, ""


# ----------------------------------------------------------------------------- suất DD
def slots(today, season, ledger):
    """{tier: (used, cap, unit)} cho ngày `today` (ICT)."""
    out = {}
    for tier, (unit, cap) in CAP[season].items():
        used = sum(1 for r in ledger if r["tier"] == tier and (
            r["date"] == str(today) if unit == "day"
            else iso_week(dt.date.fromisoformat(r["date"])) == iso_week(today)))
        out[tier] = (used, cap, unit)
    return out


def claim(ticker, tier, today, base_dir=F.DATA_DIR, by="", job="", gate=WINDOW_GATE):
    """Ghi 1 claim nếu còn suất. rc 0 = đã ghi / đã claim từ trước (idempotent); 2 = hết suất / sổ hỏng /
    tier sai (KHÔNG ghi). Read-check-append nằm trong flock ⇒ nhiều tiến trình song song không vượt trần."""
    if tier not in ("light", "full"):
        return 2, f"tier '{tier}' không hợp lệ (light|full)"
    path = pick_paths(base_dir)["ledger"]
    with file_lock(path):
        try:
            ledger = read_ledger(path)
        except Exception as e:                              # noqa: BLE001
            return 2, f"sổ DD hỏng ({type(e).__name__}: {e}) — TỪ CHỐI (fail-closed), sửa {path}"
        tk = ticker.upper()
        if any(r["date"] == str(today) and r["ticker"] == tk and r["tier"] == tier for r in ledger):
            return 0, f"đã claim {tk} {tier} hôm nay (không tiêu thêm suất)"
        season, note = in_season(today, gate)
        used, cap, unit = slots(today, season, ledger)[tier]
        if used >= cap:
            return 2, (f"HẾT SUẤT DD {tier}: {used}/{cap} mỗi {'ngày' if unit == 'day' else 'tuần'} ({note}) "
                       f"— không dispatch")
        rec = {"date": str(today), "ticker": tk, "tier": tier, "season": season,
               "by": by, "job": job, "at": dt.datetime.now(ICT).isoformat(timespec="seconds")}
        append_atomic(path, json.dumps(rec, ensure_ascii=False) + "\n")
    return 0, f"OK claim {rec['ticker']} {tier} ({used + 1}/{cap} mỗi {'ngày' if unit == 'day' else 'tuần'}, {note})"


def slots_line(today, base_dir=F.DATA_DIR, gate=WINDOW_GATE):
    try:
        ledger = read_ledger(pick_paths(base_dir)["ledger"])
    except Exception as e:                                  # noqa: BLE001
        return f"suất DD: KHÔNG XÁC ĐỊNH (sổ hỏng: {type(e).__name__}) — mọi claim bị từ chối"
    season, note = in_season(today, gate)
    s = slots(today, season, ledger)
    parts = []
    for tier, name in (("light", "nhẹ"), ("full", "đầy đủ")):
        used, cap, unit = s[tier]
        parts.append(f"{name} còn {cap - used}/{cap} {'hôm nay' if unit == 'day' else 'tuần này'}")
    wk = sum(1 for r in ledger if r["tier"] == "full"
             and iso_week(dt.date.fromisoformat(r["date"])) == iso_week(today))
    return f"suất DD ({note}): " + ", ".join(parts) + f" · đầy đủ đã dùng tuần này {wk}"


# ----------------------------------------------------------------------------- chạy + ghi
def _plain(v):
    """numpy/pandas ⇒ kiểu JSON thuần (result json.dumps)."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return None if np.isnan(v) else float(v)
    if v is pd.NA or v is pd.NaT:
        return None
    return v


def _row(r, asof, season, picked, reason, now):
    rec = {c: _plain(r.get(c)) for c in LOG_COLS if c in r}
    rec.update(asof=str(asof), season=season, picked=picked, reason=reason,
               logged_at=now.isoformat(timespec="seconds"))
    return rec


def run_pick(rating, fin, cands, banned, forensic, insider, asof, base_dir=F.DATA_DIR, write=True,
             now=None, exec_dir=EXEC_DIR, research_dir=RESEARCH_DIR, gate=WINDOW_GATE,
             dcf_fn=None, live_fn=None, prices=None):
    """Kết quả dict cho result["dd_pick"]. Cùng asof đã có trong nhật ký ⇒ ĐỌC LẠI (không chấm lại,
    không ghi lại) — chạy lại không đổi đề xuất đã hiện. write=True ⇒ cả bước kiểm-asof + chấm + append
    nằm trong flock (2 tiến trình cùng asof: tiến trình sau chờ rồi ĐỌC LẠI lô của tiến trình trước)."""
    kw = dict(base_dir=base_dir, write=write, now=now, exec_dir=exec_dir, research_dir=research_dir,
              gate=gate, dcf_fn=dcf_fn, live_fn=live_fn, prices=prices)
    if not write:
        return _run_pick(rating, fin, cands, banned, forensic, insider, asof, **kw)
    with file_lock(pick_paths(base_dir)["log"]):
        return _run_pick(rating, fin, cands, banned, forensic, insider, asof, **kw)


def _run_pick(rating, fin, cands, banned, forensic, insider, asof, base_dir, write, now, exec_dir,
              research_dir, gate, dcf_fn, live_fn, prices):
    now = now or dt.datetime.now(ICT)
    paths = pick_paths(base_dir)
    log_df = read_pick_log(paths["log"])
    season, snote = in_season(asof, gate)
    prior = log_df[log_df["asof"] == str(asof)] if len(log_df) else log_df
    if len(prior):
        rec = [{k: _plain(v) for k, v in x.items()} for x in prior.sort_values("rank").to_dict(orient="records")]
        _, _, rwarns = held_and_excluded(exec_dir)           # cảnh báo nguồn vẫn hiện khi đọc lại
        return {"asof": str(asof), "season": season, "season_note": snote, "replayed": True,
                "picked": next((x for x in rec if str(x.get("picked")).lower() in ("true", "1")), None),
                "reason": str(prior.iloc[0].get("reason") or ""),
                "top": rec, "warnings": rwarns,
                "prereg": PREREG}
    warns = []
    try:
        ledger = read_ledger(paths["ledger"])
    except Exception as e:                                  # noqa: BLE001
        ledger = None
        warns.append(f"bộ chọn: sổ DD hỏng ({type(e).__name__}) — KHÔNG đề xuất (fail-closed)")
    held, excl, w = held_and_excluded(exec_dir)
    warns += w
    recent = recent_dd(asof, log_df, ledger or [], research_dir, upto=now.date())
    if prices is None:
        prices = prices_at(rating["ticker"], asof)
    scored, dropped = score_pool(rating, fin, cands, banned, forensic, insider, held, excl, recent,
                                 asof, prices, dcf_fn)
    ok, why = pick_allowed(asof, season, log_df)
    if ledger is None:
        ok, why = False, "sổ DD hỏng — fail-closed"
    if scored.empty:
        ok, why = False, "pool rỗng sau loại trừ"
    top = scored.head(TOP_K).copy()
    top["rank"] = range(1, len(top) + 1)
    picked = None
    if ok:
        first = top.iloc[0].to_dict()
        # Cổng lên tầng đầy đủ dùng MoS THẤP HƠN giữa số CP quý và số CP live (live ≤ quý luôn ⇒ fail-safe).
        if first["escalate_full"] and live_fn is not None:
            try:
                lv = with_deadline(lambda: live_fn(first["ticker"], first["price"], first["price_date"]),
                                   LIVE_DEADLINE_S)
                lm = lv.get("margin_of_safety") if lv.get("ok") else None
            except TimeoutError:
                # Fail-soft: giữ MoS không-live (số CP quý) nhưng gắn nhãn rõ là CHƯA xác nhận live,
                # và KHÔNG lên tầng đầy đủ (cổng lấy MoS THẤP HƠN quý/live — không có live ⇒ không xác nhận).
                lm = first["mos"]
                top.loc[top.index[0], "escalate_full"] = False
                top.loc[top.index[0], "labels"] = (first["labels"] + "|live_timeout_mos_quy_chua_xac_nhan").strip("|")
                warns.append(f"bộ chọn: DCF live {first['ticker']} quá trần {LIVE_DEADLINE_S}s ⇒ dùng MoS "
                             f"số quý (chưa xác nhận live), KHÔNG lên tầng đầy đủ")
            except Exception as e:                          # noqa: BLE001
                lm = None
                warns.append(f"bộ chọn: DCF live {first['ticker']} lỗi ({type(e).__name__}) ⇒ không lên tầng đầy đủ")
            if lm is None or lm < ESCALATE_MOS:
                top.loc[top.index[0], "escalate_full"] = False
                top.loc[top.index[0], "labels"] = (first["labels"] + "|live_mos_" +
                                                   ("na" if lm is None else f"{lm:.2f}")).strip("|")
        picked = top.iloc[0]["ticker"]
        why = "điểm cao nhất pool"
    rows = [_row(r, asof, season, bool(r["ticker"] == picked), why, now) for _, r in top.iterrows()]
    res = {"asof": str(asof), "season": season, "season_note": snote, "replayed": False,
           "picked": next((x for x in rows if x["picked"]), None), "reason": why, "top": rows,
           "pool_n": int(len(scored)), "dropped_n": len(dropped),
           "dropped_held_or_recent": sorted(t for t, r in dropped.items()
                                            if "đang giữ" in r or "DD<" in r),
           "warnings": warns, "prereg": PREREG}
    if write and rows:
        buf = io.StringIO()
        pd.DataFrame(rows, columns=LOG_COLS).to_csv(buf, header=not os.path.exists(paths["log"]), index=False)
        append_atomic(paths["log"], buf.getvalue())          # append-only, MỘT lần ghi
    return res


def live_dcf_fn(asof):
    """live_fn(ticker, price, price_date): price_date = PHIÊN THẬT của giá (T-1 cho asof=T), đúng hợp
    đồng dcf_valuation.fair_value (R8/H1) — KHÔNG khai asof."""
    D = _dcf_engine()
    return lambda t, p, price_date=None: D.fair_value(t, str(asof), price=p, price_date=price_date)


# ----------------------------------------------------------------------------- dòng topic 08:00
def _fmt_pct(x):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x * 100:+.0f}%"


TOPIC_DISCLAIMER = ("xếp việc DD, KHÔNG phải tín hiệu mua — PIT 2016-26: không edge; "
                    "ngưỡng MoS≥25% gần như không lọc")


def topic_line(pick, today, base_dir=F.DATA_DIR, gate=WINDOW_GATE):
    """1 dòng: mã DD hôm nay + lý do + suất còn lại (suất tính LÚC IN theo sổ claim)."""
    sl = slots_line(today, base_dir, gate)
    if pick is None:
        return f"🔎 Mã DD hôm nay: ⚠️ bộ chọn KHÔNG chạy phiên này (xem cảnh báo) · {sl}"
    w = "; ".join(pick.get("warnings") or [])
    p = pick.get("picked")
    if not p:
        return f"🔎 Mã DD hôm nay: không đề xuất ({pick.get('reason')}) · {sl}" + (f" · ⚠️ {w}" if w else "")
    tier = ("có thể xét DD đầy đủ nếu tầng nhẹ sạch (MoS≥25% robust)" if str(p.get("escalate_full")).lower() == "true"
            else "chỉ DD tầng nhẹ (chưa đạt ngưỡng chênh giá)")
    why = (f"điểm {float(p['score']):.2f} = V {float(p['V']):.2f}·E {float(p['E']):.2f}·R {float(p['R']):.2f}; "
           f"MoS DCF {_fmt_pct(_f(p.get('mos')))} (⚠️ top-1 lịch sử KÉM rank 2-8, PIT 2016-26), rating {int(float(p['rating']))}"
           + (f", BCTC {p['release_date']} YoY {_fmt_pct(_f(p.get('g_yoy')))}" if "bctc_moi" in str(p.get("labels")) else "")
           + (f" [{p['labels']}]" if p.get("labels") and str(p.get("labels")) != "nan" else ""))
    return (f"🔎 Mã DD hôm nay: **{p['ticker']}** ({TOPIC_DISCLAIMER}) — {tier}; {why} · {sl}"
            + (f" · ⚠️ {w}" if w else "") + " · Mike quyết, KHÔNG tự dispatch; claim suất bằng "
            "`discretionary_dd_pick.py --claim <MÃ> --tier light|full` trước khi dispatch")


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--claim", metavar="TICKER")
    ap.add_argument("--tier", choices=["light", "full"])
    ap.add_argument("--by", default="")
    ap.add_argument("--job", default="")
    ap.add_argument("--slots", action="store_true")
    ap.add_argument("--out-dir", metavar="DIR")
    a = ap.parse_args(argv)
    base = a.out_dir or F.DATA_DIR
    today = dt.datetime.now(ICT).date()
    if a.claim:
        if not a.tier:
            ap.error("--claim cần --tier light|full")
        rc, msg = claim(a.claim, a.tier, today, base, a.by, a.job)
        print(msg)
        return rc
    if a.slots:
        print(slots_line(today, base))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
