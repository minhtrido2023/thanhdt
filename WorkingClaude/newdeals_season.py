#!/usr/bin/env python3
"""newdeals_season.py — vòng làm mới topic "New deals" THEO MÙA BCTC (job Taylor_20261117_102211,
user duyệt 17/11/2026, decided_by: user). RESEARCH / MONITOR ONLY: không đụng custom30V / BAL / LAG /
rating_8l.py / trading_rules / lệnh.

Bốn việc:
  1. TRIGGER mùa: quý BCTC mới nhất (ticker_financial cache, PIT time<=asof) phủ >= COVERAGE_MIN của
     watchlist Nhóm A (sector_lens_monitor.NAMES) ⇒ mùa đó "đến hạn". Idempotent theo mùa
     (state["seasons_done"]); không bao giờ chạy lùi về mùa cũ hơn mùa đã xong.
  2. Vòng làm mới: rating 8L (data/rating_8l.csv — sản phẩm của pt_8l_daily, KHÔNG gọi lại rating_8l.py;
     phải tươi hơn ngày BCTC mới nhất của watchlist, không thì hoãn) + sector lens ⇒ tập Golden/Strong
     (rating<=2) và double-confirm; so với mùa trước ⇒ VÀO / RA / ĐỔI HẠNG.
  3. Hàng đợi DD: mã VÀO/ĐỔI HẠNG chưa có DD đúng quý ⇒ xếp hàng, TRẦN DD_CAP mã/mùa (ưu tiên: dư từ
     mùa trước, rồi double-confirm, MoS DCF cao, rating thấp); phần dư = deferred_next_season. KHÔNG tự chạy
     DD — chỉ ghi hàng đợi + (tuỳ chọn) 1 event bus cho Mike dispatch. Quý DD hiện có = `bctc_quarter` của
     bản mới nhất trong mike/kb/dd_price_zones.json (schema dd_price_zones/v1 — tái dùng, không thêm schema).
  4. DC Book theo mùa: đặt lại seed = tập double-confirm của mùa mới (giá thô ngày chốt, equal-weight);
     seed cũ chuyển vào meta.season_history (KHÔNG xoá).
Kèm helper hiển thị cho newdeals_daily_report.py: freshness_line() + apply_dd_labels() (nhãn "DD asof <quý>",
"⚠️ DD cũ (Qx)" và gạch ACCUMULATE/STRONG của mã có DD cũ — gắn cảnh báo, không ẩn).

CLI:  $DNA_PYEXE newdeals_season.py [--asof YYYY-MM-DD] [--dry] [--notify-bus]
      rc 0 = chạy xong (kể cả "chưa đến hạn"), rc 1 = lỗi (mùa KHÔNG bị đánh dấu xong ⇒ lượt sau thử lại).
"""
import json
import os
import re
import subprocess
import sys
import datetime as dt
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
DATA = os.path.join(ROOT, "data")
FIN_PATH = os.path.join(DATA, "bq_cache", "ticker_financial.parquet")
RATING_CSV = os.path.join(DATA, "rating_8l.csv")
FWD_EVENTS = os.path.join(DATA, "rating_8l_forward_events.csv")
PAPER_FILE = os.path.join(DATA, "converge_portfolio_paper.json")
DCF_STATE = os.path.join(DATA, "dcf_refresh_state.json")
STATE_FP = os.path.join(DATA, "newdeals_season_state.json")
QUEUE_FP = os.path.join(DATA, "newdeals_dd_queue.json")
SNAP_DIR = os.path.join(DATA, "newdeals_season")
LOG_FP = os.path.join(DATA, "newdeals_season.log")
DD_ZONES = os.path.join(ROOT, "mike", "kb", "dd_price_zones.json")
APPEND_EVENT = os.path.join(ROOT, "mike", "bin", "append_event.sh")

COVERAGE_MIN = 0.80     # brief: "BCTC quý mới phủ >= ~80% watchlist"
DD_CAP = 5              # brief: "TRẦN 5 mã/mùa"
GOLDEN_MAX = 2          # 8L rating<=2 = golden/strong
INVESTABLE_MAX = 3      # 8L rating<=3 = vùng đầu tư được (gate LAG/KB)


def today_ict(asof=None):
    return asof or dt.datetime.now(ICT).date().isoformat()


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def watchlist():
    import sector_lens_monitor as slm
    return [n for n, _, _ in slm.NAMES]


# ------------------------------------------------------------------ 1. TRIGGER (thuần)
def quarter_coverage(fin_df, wl, asof):
    """fin_df cột ticker/time/quarter. Quý mới nhất = quarter lớn nhất toàn universe với time<=asof.
    Trả {quarter, covered, n, frac, missing, last_fin_date} — last_fin_date = ngày BCTC quý đó muộn nhất
    trong số mã watchlist đã phủ (mốc để kiểm rating có tươi hơn không)."""
    import pandas as pd
    df = fin_df[["ticker", "time", "quarter"]].copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df[df["time"] <= pd.Timestamp(asof)]
    if df.empty:
        return {"quarter": None, "covered": [], "n": len(wl), "frac": 0.0, "missing": list(wl),
                "last_fin_date": None}
    q = str(df["quarter"].max())
    w = df[df["ticker"].isin(wl) & (df["quarter"] == q)]
    covered = sorted(set(w["ticker"]))
    return {"quarter": q, "covered": covered, "n": len(wl),
            "frac": len(covered) / len(wl) if wl else 0.0,
            "missing": sorted(set(wl) - set(covered)),
            "last_fin_date": (w["time"].max().date().isoformat() if len(w) else None)}


def season_due(cov, state, threshold=COVERAGE_MIN):
    """(due, season, reason). Idempotent: mùa đã xong ⇒ no-op; mùa <= mùa xong gần nhất ⇒ no-op."""
    q = cov.get("quarter")
    if not q:
        return False, None, "no_financial_rows"
    done = (state or {}).get("seasons_done", [])
    if q in done:
        return False, q, "season_already_done"
    if done and q < max(done):
        return False, q, "older_than_last_done"
    if cov["frac"] < threshold:
        return False, q, f"coverage_below_threshold {cov['frac']:.0%}<{threshold:.0%}"
    return True, q, "season_due"


# ------------------------------------------------------------------ 2. DIFF (thuần)
def make_snapshot(ratings, dc_set, wl):
    """ratings {tk:int} (chỉ watchlist), dc_set {tk:buy_mode}."""
    r = {t: int(ratings[t]) for t in wl if t in ratings}
    return {"ratings": r,
            "golden": sorted(t for t, v in r.items() if v <= GOLDEN_MAX),
            "dc": {t: dc_set[t] for t in sorted(dc_set)}}


def diff_season(prev, cur):
    """VÀO = vào golden hoặc vào double-confirm; RA = rời golden hoặc rời double-confirm;
    ĐỔI HẠNG = rating 8L đổi (kể cả khi không đổi nhóm). prev None ⇒ mọi mã hiện có = VÀO."""
    prev = prev or {"ratings": {}, "golden": [], "dc": {}}
    pg, cg = set(prev["golden"]), set(cur["golden"])
    pd_, cd = set(prev["dc"]), set(cur["dc"])
    enter = sorted((cg - pg) | (cd - pd_))
    exit_ = sorted((pg - cg) | (pd_ - cd))
    rerank = []
    for t in sorted(set(prev["ratings"]) & set(cur["ratings"])):
        a, b = prev["ratings"][t], cur["ratings"][t]
        if a != b:
            rerank.append({"ticker": t, "from": a, "to": b})
    return {"enter": enter, "exit": exit_, "rerank": rerank}


# ------------------------------------------------------------------ 3. DD queue + nhãn (thuần)
def latest_dd_index(entries):
    """{ticker: {dd_date, rev, bctc_quarter}} — bản (dd_date, rev) cao nhất thắng (luật của
    dd_price_zones.json; rev None ≡ 0)."""
    best = {}
    for e in entries or []:
        t = e.get("ticker")
        if not t:
            continue
        k = (str(e.get("dd_date") or ""), int(e.get("rev") or 0))
        if t not in best or k > best[t][0]:
            best[t] = (k, {"dd_date": e.get("dd_date"), "rev": e.get("rev"),
                           "bctc_quarter": e.get("bctc_quarter")})
    return {t: v[1] for t, v in best.items()}


def dd_status(tk, dd_index, latest_q):
    """('none'|'fresh'|'stale', dd_asof_quarter|None). stale = DD dựa trên quý CŨ hơn quý BCTC mới nhất."""
    d = (dd_index or {}).get(tk)
    q = d.get("bctc_quarter") if d else None
    if not q:
        return "none", None
    if latest_q and q < latest_q:
        return "stale", q
    return "fresh", q


def build_dd_queue(changes, cur, dd_index, season, prev_queue=None, mos=None, cap=DD_CAP):
    """Ứng viên = VÀO + ĐỔI HẠNG sang hạng <=3 (+ phần deferred của mùa trước). Mã đã có DD đúng quý ⇒ dd_fresh (không
    tốn suất). Thứ tự ưu tiên: dư mùa trước → double-confirm → MoS DCF cao → rating thấp → ticker.
    `cap` suất đầu = queued; còn lại = deferred_next_season (ghi rõ)."""
    mos = mos or {}
    carried = [i["ticker"] for i in (prev_queue or {}).get("items", [])
               if i.get("status") == "deferred_next_season"]
    cands = []
    # ĐỔI HẠNG chỉ tốn suất DD khi hạng MỚI còn đầu tư được (<=INVESTABLE_MAX); tụt xuống 4-5 = rời
    # vùng đầu tư, không cần DD để vào (vẫn hiện trong changes.rerank để đọc).
    rr = [r["ticker"] for r in changes["rerank"] if r["to"] <= INVESTABLE_MAX]
    for t in carried + changes["enter"] + rr:
        if t not in cands and t not in changes["exit"]:
            cands.append(t)
    carried_set = set(carried)

    def key(t):
        m = mos.get(t)
        return (0 if t in carried_set else 1, 0 if t in cur["dc"] else 1,
                -(m if m is not None else -1e9), cur["ratings"].get(t, 9), t)

    items, slots = [], 0
    for t in sorted(cands, key=key):
        st, q = dd_status(t, dd_index, season)
        why = ("carried" if t in carried_set else
               "enter" if t in changes["enter"] else "rerank")
        it = {"ticker": t, "reason": why, "in_double_confirm": t in cur["dc"],
              "rating": cur["ratings"].get(t), "mos": mos.get(t), "dd_asof_quarter": q}
        if st == "fresh":
            it["status"] = "dd_fresh"
        elif slots < cap:
            it["status"] = "queued"; slots += 1
        else:
            it["status"] = "deferred_next_season"
        items.append(it)
    return {"season": season, "cap": cap, "items": items}


_TK_RE = re.compile(r"\*\*([A-Z0-9]{3})\*\*")
_MODE_RE = re.compile(r"(?<![~A-Za-z])(ACCUMULATE|STRONG)(?![~A-Za-z])")


def apply_dd_labels(md, dd_index, latest_q, only=None):
    """Mỗi dòng có **TICKER** (ticker thuộc `only` nếu truyền): thêm nhãn DD; DD cũ ⇒ '⚠️ DD cũ (Qx)' và
    gạch ACCUMULATE/STRONG trên dòng đó (không hiện như hợp lệ, nhưng KHÔNG ẩn dòng)."""
    out = []
    for line in md.split("\n"):
        tks = [t for t in _TK_RE.findall(line) if only is None or t in only]
        if tks:
            tk = tks[0]
            st, q = dd_status(tk, dd_index, latest_q)
            if st == "stale":
                line = _MODE_RE.sub(r"~~\1~~", line) + f" · ⚠️ DD cũ ({q}) — tín hiệu chưa hợp lệ tới khi DD {latest_q}"
            elif st == "fresh":
                line += f" · DD asof {q}"
            else:
                line += " · DD: chưa có"
        out.append(line)
    return "\n".join(out)


def freshness_line(asof=None, wl=None, fin_path=FIN_PATH, rating_csv=RATING_CSV,
                   dcf_state=DCF_STATE, paper_file=PAPER_FILE):
    """Dòng đầu báo cáo: BCTC phủ x% · rating ngày nào · DCF mùa nào · tuổi sổ DC. Không bao giờ raise
    (phần lỗi hiện '?'). Trả (line, latest_quarter|None)."""
    a = today_ict(asof)
    parts, q = [], None
    try:
        import pandas as pd
        wl = wl or watchlist()
        cov = quarter_coverage(pd.read_parquet(fin_path, columns=["ticker", "time", "quarter"]), wl, a)
        q = cov["quarter"]
        parts.append(f"BCTC {q} phủ {len(cov['covered'])}/{cov['n']} watchlist ({cov['frac']:.0%})")
    except Exception as e:
        parts.append(f"BCTC phủ ? ({type(e).__name__})")
    try:
        rd = dt.datetime.fromtimestamp(os.path.getmtime(rating_csv), ICT).date().isoformat()
        parts.append(f"rating 8L {rd}")
    except Exception:
        parts.append("rating 8L ?")
    try:
        s = _load_json(dcf_state, {})
        slot = (s.get("season_done") or ["?"])[-1]
        parts.append(f"DCF mùa {slot}")
    except Exception:
        parts.append("DCF mùa ?")
    try:
        m = _load_json(paper_file, {}).get("meta", {})
        start = m.get("start_date")
        age = (dt.date.fromisoformat(a) - dt.date.fromisoformat(start)).days
        parts.append(f"sổ DC mùa {m.get('season') or 'seed cố định (chưa theo mùa)'} từ {start} ({age} ngày)")
    except Exception:
        parts.append("sổ DC ?")
    return "🧭 *Độ tươi: " + " · ".join(parts) + "*", q


# ------------------------------------------------------------------ 4. DC Book theo mùa (thuần)
def reset_dc_book(paper, season, asof, dc_set, prices, vni, price_asof, ratings, sectors):
    """Trả paper MỚI: seed cũ (+meta liên quan) vào meta.season_history; seed mới = dc_set, giá thô ngày chốt,
    equal-weight (cap 0.20 như luật cũ). Đã ở mùa này ⇒ trả nguyên (idempotent)."""
    paper = json.loads(json.dumps(paper))
    meta = paper.setdefault("meta", {})
    if meta.get("season") == season:
        return paper
    missing = [t for t in dc_set if prices.get(t) is None]
    if missing or vni is None:
        raise ValueError(f"thiếu giá để đặt sổ mùa {season}: {missing or 'VNINDEX'}")
    hist = meta.setdefault("season_history", [])
    hist.append({"season": meta.get("season") or "seed-2026-06-26 (trước khi theo mùa)",
                 "start_date": meta.get("start_date"), "entry_price_asof": meta.get("entry_price_asof"),
                 "benchmark_entry": meta.get("benchmark_entry"), "closed_on": asof,
                 "seed_double_confirm_set": paper.get("seed_double_confirm_set", [])})
    n = len(dc_set)
    w = round(min(1.0 / n, 0.20), 4) if n else 0.0
    paper["seed_double_confirm_set"] = [
        {"ticker": t, "sector": sectors.get(t, ""), "buy_mode": dc_set[t], "rating_8l": ratings.get(t),
         "entry_price": float(prices[t]), "weight_paper": w} for t in sorted(dc_set)]
    meta.update({"season": season, "start_date": asof, "entry_price_asof": price_asof,
                 "benchmark_entry": float(vni), "end_date": None,
                 "review_date": "mùa BCTC kế tiếp (newdeals_season.py)"})
    paper.setdefault("parking", {})["weight_paper"] = round(max(0.0, 1 - w * n), 4)
    return paper


# ------------------------------------------------------------------ I/O mặc định (thay được khi test)
def _default_live(asof):
    """(dc_set, sectors) từ sector lens sống."""
    import sector_lens_monitor as slm
    r = slm.compute_status()
    sectors = {t: s for t, s, _ in slm.NAMES}
    return slm.double_confirm_set(r["df"], slm.load_ratings()), sectors


def _default_prices(tickers):
    """Giá THÔ (Price) phiên mới nhất + VNINDEX từ cache — đúng hệ quy chiếu entry_price của sổ paper."""
    import duckdb
    con = duckdb.connect(); con.execute("SET threads=1")
    tsql = ",".join(f"'{t}'" for t in list(tickers) + ["VNINDEX"])
    df = con.execute(f"""
        WITH r AS (SELECT ticker, time, Price, Close, VNINDEX,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn
                   FROM read_parquet('{DATA}/bq_cache/ticker/*.parquet') WHERE ticker IN ({tsql}))
        SELECT ticker, time, Price, Close, VNINDEX FROM r WHERE rn=1""").df()
    con.close()
    px = {r.ticker: float(r.Price if r.Price == r.Price else r.Close) for r in df.itertuples()}
    stk = df[df.ticker != "VNINDEX"].sort_values("time")
    vni = float(stk.iloc[-1].VNINDEX) if len(stk) else px.get("VNINDEX")
    return px, vni, str(df.time.max())[:10] if len(df) else None


def _default_mos(tickers, asof):
    out = {}
    try:
        from dcf_valuation import dcf_check
    except Exception:
        return out
    for t in tickers:
        try:
            d = dcf_check(t, asof)
            if d.get("status") != "NOT_COMPUTED" and d.get("margin_of_safety") is not None:
                out[t] = float(d["margin_of_safety"])
        except Exception:
            pass
    return out


def _bootstrap_prev(season, wl, paper):
    """Mùa đầu tiên chưa có snapshot: rating mùa trước = rating_prev PIT của rating_8l_forward_events.csv
    (khoá ticker, quarter=season); DC mùa trước = seed sổ DC hiện tại."""
    import pandas as pd
    r = {}
    if os.path.exists(FWD_EVENTS):
        e = pd.read_csv(FWD_EVENTS)
        e = e[(e.quarter == season) & e.ticker.isin(wl)]
        r = {str(t): int(v) for t, v in zip(e.ticker, e.rating_prev) if v == v}
    dc = {p["ticker"]: p.get("buy_mode", "") for p in paper.get("seed_double_confirm_set", [])}
    snap = make_snapshot(r, dc, wl)
    snap["dc"] = dict(sorted(dc.items()))      # seed có thể chứa mã ngoài watchlist — giữ nguyên
    snap["source"] = "bootstrap: rating_prev (rating_8l_forward_events.csv) + seed DC Book"
    return snap


def _post_bus(season, queue, changes):
    payload = {"season": season,
               "dd_queue": [i["ticker"] for i in queue["items"] if i["status"] == "queued"],
               "deferred_next_season": [i["ticker"] for i in queue["items"]
                                        if i["status"] == "deferred_next_season"],
               "dd_fresh": [i["ticker"] for i in queue["items"] if i["status"] == "dd_fresh"],
               "changes": changes, "action": "Mike dispatch DD theo skill due-diligence (tối đa 5)",
               "measured_by": f"newdeals_season.py → {QUEUE_FP}"}
    subprocess.run([APPEND_EVENT, "Taylor", "question", f"newdeals-season-{season} dd-queue",
                    json.dumps(payload, ensure_ascii=False)], check=True, timeout=60)


def run_refresh(asof=None, dry=False, notify_bus=False, wl=None, fin_df=None, ratings=None,
                rating_asof=None, live_fn=None, prices_fn=None, mos_fn=None, dd_entries=None,
                state_path=None, queue_path=None, snap_dir=None, paper_path=None, log_path=None,
                bus_fn=None):
    """Một lượt (cron hằng ngày). Thứ tự ghi: snapshot → queue → sổ DC → state (cuối cùng ⇒ crash giữa
    chừng = lượt sau làm lại, các bước trước đều idempotent theo mùa). Bus post SAU state, cờ bus_posted
    ⇒ lỗi post được thử lại lượt sau, không post lặp khi đã thành công."""
    import pandas as pd
    a = today_ict(asof)
    state_path = state_path or STATE_FP; queue_path = queue_path or QUEUE_FP
    snap_dir = snap_dir or SNAP_DIR; paper_path = paper_path or PAPER_FILE; log_path = log_path or LOG_FP
    wl = wl or watchlist()
    state = _load_json(state_path, {})
    out = {"date": a}
    if fin_df is None:
        fin_df = pd.read_parquet(FIN_PATH, columns=["ticker", "time", "quarter"])
    cov = quarter_coverage(fin_df, wl, a)
    due, season, reason = season_due(cov, state)
    out.update({"season": season, "coverage": round(cov["frac"], 3), "reason": reason,
                "missing": cov["missing"]})

    # bus post đã hứa mà chưa thành công ở lượt trước ⇒ thử lại (không chạy lại cả vòng)
    pend = state.get("bus_pending")
    if not due and pend and notify_bus and not dry:
        q = _load_json(queue_path, {}).get("seasons", {}).get(pend)
        if q:
            (bus_fn or _post_bus)(pend, q, q.get("changes", {}))
            state["bus_pending"] = None
            _atomic_write(state_path, state)
            out["bus_retry"] = pend

    if not due:
        _log(out, log_path, dry)
        return out

    if ratings is None:
        rdf = pd.read_csv(RATING_CSV, usecols=["ticker", "rating"])
        ratings = {str(t): int(v) for t, v in zip(rdf.ticker, rdf.rating) if v == v}
        rating_asof = dt.datetime.fromtimestamp(os.path.getmtime(RATING_CSV), ICT).date().isoformat()
    if cov["last_fin_date"] and (rating_asof or "") < cov["last_fin_date"]:
        out["reason"] = f"rating_not_fresh {rating_asof}<{cov['last_fin_date']}"
        _log(out, log_path, dry)
        return out

    dc_set, sectors = (live_fn or _default_live)(a)
    paper = _load_json(paper_path, {})
    cur = make_snapshot(ratings, dc_set, wl)
    prev_season = max(state.get("seasons_done", [])) if state.get("seasons_done") else None
    prev = _load_json(os.path.join(snap_dir, f"{prev_season}.json"), None) if prev_season else None
    if prev is None:
        prev = _bootstrap_prev(season, wl, paper)
    changes = diff_season(prev, cur)
    cand = set(changes["enter"]) | {r["ticker"] for r in changes["rerank"]}
    mos = (mos_fn or _default_mos)(sorted(cand), a)
    if dd_entries is None:
        dd_entries = _load_json(DD_ZONES, {}).get("entries", [])
    qall = _load_json(queue_path, {"seasons": {}})
    prev_q = qall["seasons"].get(prev_season) if prev_season else None
    queue = build_dd_queue(changes, cur, latest_dd_index(dd_entries), season, prev_q, mos)
    queue["changes"] = changes
    queue["created"] = a
    out.update({"changes": changes, "queue": queue["items"], "prev_source": prev.get("source", prev_season)})

    px, vni, px_asof = (prices_fn or _default_prices)(sorted(dc_set))
    new_paper = reset_dc_book(paper, season, a, dc_set, px, vni, px_asof, cur["ratings"], sectors)
    out["dc_seed"] = [p["ticker"] for p in new_paper["seed_double_confirm_set"]]
    if dry:
        out["dry"] = True
        return out

    cur.update({"season": season, "asof": a, "rating_asof": rating_asof, "coverage": cov})
    _atomic_write(os.path.join(snap_dir, f"{season}.json"), cur)
    qall["seasons"][season] = queue
    _atomic_write(queue_path, qall)
    _atomic_write(paper_path, new_paper)
    state["seasons_done"] = sorted(set(state.get("seasons_done", [])) | {season})
    state["last_season"] = season; state["last_run"] = a
    state["bus_pending"] = season if notify_bus else None
    _atomic_write(state_path, state)
    if notify_bus:
        (bus_fn or _post_bus)(season, queue, changes)
        state["bus_pending"] = None
        _atomic_write(state_path, state)
    _log(out, log_path, dry)
    return out


def _log(out, log_path, dry):
    if dry:
        return
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(out, ensure_ascii=False, default=str) + "\n")
    except Exception as e:
        print(f"newdeals_season: không ghi được log {log_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    import argparse
    sys.path.insert(0, ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default=None)
    ap.add_argument("--dry", action="store_true", help="tính đủ, KHÔNG ghi gì")
    ap.add_argument("--notify-bus", action="store_true", help="post hàng đợi DD lên bus cho Mike")
    a = ap.parse_args()
    try:
        res = run_refresh(asof=a.asof, dry=a.dry, notify_bus=a.notify_bus)
    except Exception as e:
        print(f"❌ newdeals_season: {type(e).__name__}: {e} — mùa KHÔNG đánh dấu xong", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
