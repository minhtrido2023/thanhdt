#!/usr/bin/env python3
"""fill_timing_monitor.py — monitor CƠ HỌC fill-vs-open cho fill_timing HYBRID (job Taylor_20261119_055805).

READ-ONLY production: chỉ đọc dnse_raw_*.jsonl + journal + BQ; không đổi cờ/config/plan/lệnh.
Luật khai trước (PREREG: agents/Taylor/research/fill_timing_monitor_20261119/PREREG.md, md5 ở PREREG.md5):
  * HYBRID_ON_DATE = 2026-08-26 — ngày commit 9be375a44 đổi `fill_timing_live_gate` +
    `fill_timing_hybrid_live_gate` True->False (user duyệt 2026-08-26). Selfcheck đối chiếu với git.
  * Đơn vị = (account,date,sym,side) trọng số qty; bps = (fill/open_unadj-1)*1e4;
    open_unadj = tav2_bq.ticker.Open*Price/Close. Chỉ tính (mã,ngày) ĐÃ có dòng BQ và ngày < hôm nay (ICT).
  * ĐỦ N (mỗi chiều) = >=30 mã-ngày VÀ >=8 tuần ISO => CI95 bootstrap khối tuần (5000, seed 20261119).
    Chưa đủ N => chỉ báo tiến độ, KHÔNG báo mean/kết luận.
  * BUY HYB_IN_BLOCK đủ N và mean > +22 bps => CẢNH BÁO "đề xuất rollback — user quyết". Không tự đổi gì.
Exit: 0 bình thường · 2 đã phát CẢNH BÁO rollback · 1 monitor không chạy được (đã post lý do).
"""
import argparse, glob, hashlib, io, json, os, re, subprocess, sys, tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

HYBRID_ON_DATE = "2026-08-26"
HYBRID_FLAG_COMMIT = "9be375a44"
MIN_UNITS, MIN_WEEKS = 30, 8
ROLLBACK_BPS = 22.0
BOOT_N, BOOT_SEED = 5000, 20261119
ACCOUNTS = {"0002023347": "SpaceX", "0001743768": "ZaloPay"}
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE = Path(__file__).resolve().parent
WC_ROOT = Path(os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude"))
DEFAULT_LOG_DIR = WC_ROOT / "data" / "execution_logs"
DEFAULT_STATE = WC_ROOT / "mike" / "state" / "fill_timing_monitor.json"
NOTIFY_CHANNEL = "trading_daily"  # tên kênh, resolve ở kb/discord_channels.json


class MonitorError(Exception):
    pass


def cls_note(n):
    """Cùng luật phân loại build.py job 052911."""
    if pd.isna(n): return "NO_JOURNAL_MATCH"
    if "GAP_OPEN_OVERRIDE" in n: return "GAP_OVERRIDE"
    if "hyb:blk" in n: return "HYB_IN_BLOCK"
    if ("ft:out" in n and n.rstrip().endswith("hyb")) or ("×" in n and "hyb" in n): return "HYB_OUT_OF_BLOCK"
    if "ft:in-window" in n: return "FT_BASE_IN"
    if "ft:out" in n: return "FT_BASE_OUT"
    return "NO_FT_TAG"


def load_orders(log_dir, asof):
    """Fill thật, lọc account (§12), dedupe (account,id), HYBRID_ON_DATE <= transDate < asof."""
    files = sorted(glob.glob(str(Path(log_dir) / "dnse_raw_2026-*.jsonl")))
    if not files:
        raise MonitorError(f"không có file dnse_raw_2026-*.jsonl trong {log_dir}")
    acct = {}
    for f in files:
        with open(f, errors="replace") as fh:
            for line in fh:
                try: r = json.loads(line)
                except ValueError: continue
                if r.get("kind") != "orders": continue
                for o in (r.get("payload") or {}).get("orders", []):
                    an = str(o.get("accountNo") or r.get("account_no"))
                    if an not in ACCOUNTS: continue
                    td = str(o.get("transDate", ""))
                    if (o.get("fillQuantity") or 0) > 0 and HYBRID_ON_DATE <= td < asof:
                        acct[(an, str(o["id"]))] = o
    if not acct:
        raise MonitorError(f"0 fill thật trong [{HYBRID_ON_DATE}, {asof}) sau lọc account — dnse_raw có {len(files)} file")
    O = pd.DataFrame([dict(account=ACCOUNTS[an], oid=i, date=o["transDate"], sym=o["symbol"],
                           side="BUY" if o["side"] == "NB" else "SELL", qty=o["fillQuantity"],
                           avg=o.get("averagePrice")) for (an, i), o in acct.items()])
    rows = []
    for f in sorted(glob.glob(str(Path(log_dir) / "exec_*_2026-*_journal.csv"))):
        m = re.match(r".*exec_(SpaceX|ZaloPay)_(\d{4}-\d\d-\d\d)_journal\.csv$", f)
        if not m or m.group(2) < HYBRID_ON_DATE: continue
        d = pd.read_csv(f, dtype=str, on_bad_lines="skip")
        d = d[d.event == "PLACE"]
        d["account"] = m.group(1)
        rows.append(d[["account", "child_oid", "note"]])
    if not rows:
        raise MonitorError(f"không có journal exec_*_journal.csv từ {HYBRID_ON_DATE} trong {log_dir}")
    J = pd.concat(rows).drop_duplicates(["account", "child_oid"], keep="last").rename(columns={"child_oid": "oid"})
    M = O.merge(J, on=["account", "oid"], how="left")
    M["cls"] = M.note.map(cls_note)
    return M


def _bq(sql):
    env = dict(os.environ)
    envsh = WC_ROOT / "wc_env.sh"
    cmd = f'source "{envsh}" >/dev/null 2>&1; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=1000000 "$FTM_SQL"'
    env["FTM_SQL"] = sql
    p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, env=env, timeout=300)
    if p.returncode != 0:
        raise MonitorError("BQ lỗi rc=%d: %s" % (p.returncode, (p.stderr or p.stdout).strip()[-400:]))
    return p.stdout


def load_open_bq(syms):
    lst = ",".join('"%s"' % s for s in sorted(syms))
    mx = _bq(f'SELECT CAST(MAX(t.time) AS STRING) AS d FROM tav2_bq.ticker AS t WHERE t.time >= "{HYBRID_ON_DATE}"')
    bq_max = mx.strip().splitlines()[-1].strip()
    if not re.match(r"\d{4}-\d\d-\d\d$", bq_max):
        raise MonitorError(f"BQ freshness không đọc được MAX(time): {mx.strip()[-200:]!r}")
    out = _bq(f'SELECT t.ticker, CAST(t.time AS STRING) AS d, t.Open, t.Close, t.Price FROM tav2_bq.ticker AS t '
              f'WHERE t.time >= "{HYBRID_ON_DATE}" AND t.ticker IN ({lst})')
    return pd.read_csv(io.StringIO(out)), bq_max


def build_units(M, B):
    """M: lệnh đã phân loại; B: ticker,d,Open,Close,Price. Trả (units HYB_IN_BLOCK, n_pending_orders)."""
    B = B.copy()
    B = B[(B.Close > 0) & (B.Open > 0) & (B.Price > 0)]
    B["open_unadj"] = B.Open * B.Price / B.Close
    X = M[M.cls == "HYB_IN_BLOCK"].merge(
        B.rename(columns={"ticker": "sym", "d": "date"})[["sym", "date", "open_unadj", "Price"]],
        on=["sym", "date"], how="left")
    pending = int(X.open_unadj.isna().sum())
    X = X.dropna(subset=["open_unadj"])
    X["bps"] = (X.avg / X.open_unadj - 1) * 1e4
    X["dayret"] = X.Price / X.open_unadj - 1
    rows = []
    for (acc, d, sym, side), g in X.groupby(["account", "date", "sym", "side"]):
        rows.append(dict(account=acc, date=d, sym=sym, side=side, bps=float(np.average(g.bps, weights=g.qty)),
                         n_ord=len(g), dayret=float(g.dayret.iloc[0])))
    U = pd.DataFrame(rows, columns=["account", "date", "sym", "side", "bps", "n_ord", "dayret"])
    U["week"] = pd.to_datetime(U.date).dt.strftime("%G-W%V")
    return U, pending


def boot_ci(x, w):
    rng = np.random.default_rng(BOOT_SEED)
    ws = sorted(w.unique())
    g = {k: x[w == k].values for k in ws}
    m = [np.concatenate([g[k] for k in rng.choice(ws, len(ws))]).mean() for _ in range(BOOT_N)]
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def evaluate(U):
    """Luật khai trước. Chưa đủ N => KHÔNG có mean/ci/verdict."""
    res = {}
    for side in ("BUY", "SELL"):
        g = U[U.side == side]
        r = dict(n_units=int(len(g)), n_weeks=int(g.week.nunique()), n_orders=int(g.n_ord.sum()))
        r["enough_N"] = bool(r["n_units"] >= MIN_UNITS and r["n_weeks"] >= MIN_WEEKS)
        if r["enough_N"]:
            r["mean_bps"] = float(g.bps.mean())
            r["ci_lo"], r["ci_hi"] = boot_ci(g.bps, g.week)
            for nm, s in (("down", g[g.dayret < 0]), ("up", g[g.dayret >= 0])):
                r[f"expost_{nm}_n"] = int(len(s)); r[f"expost_{nm}_mean"] = float(s.bps.mean()) if len(s) else None
        res[side] = r
    b = res["BUY"]
    res["alert"] = bool(b["enough_N"] and b["mean_bps"] > ROLLBACK_BPS)
    return res


def progress_line(res, bq_max, pending, today):
    def p(s):
        r = res[s]; return f"{s} N={r['n_units']}/{MIN_UNITS} mã-ngày, {r['n_weeks']}/{MIN_WEEKS} tuần"
    head = f"📊 fill_timing HYBRID monitor ({today}, từ {HYBRID_ON_DATE}; trong block): {p('BUY')} · {p('SELL')}"
    tail = f" · BQ tới {bq_max}" + (f", {pending} lệnh chờ giá" if pending else "")
    done = [s for s in ("BUY", "SELL") if res[s]["enough_N"]]
    if not done:
        return head + " — chưa đủ N, không kết luận" + tail
    parts = []
    for s in done:
        r = res[s]
        parts.append(f"{s} mean {r['mean_bps']:+.1f} bps CI95 [{r['ci_lo']:+.1f}; {r['ci_hi']:+.1f}]")
    note = f" (BUY ngưỡng rollback +{ROLLBACK_BPS:.0f}: " + ("CHẠM" if res["alert"] else "không chạm") + ")" if res["BUY"]["enough_N"] else ""
    return head + " — đủ N: " + "; ".join(parts) + note + tail


def alert_text(res, bq_max, today):
    b = res["BUY"]
    return (f"🚨 fill_timing HYBRID ({today}): BUY trong block mean {b['mean_bps']:+.1f} bps > +{ROLLBACK_BPS:.0f} "
            f"(ngưỡng rollback đã duyệt), N={b['n_units']} mã-ngày/{b['n_weeks']} tuần, CI95 [{b['ci_lo']:+.1f}; {b['ci_hi']:+.1f}]. "
            f"ĐỀ XUẤT rollback — user quyết; monitor KHÔNG tự đổi cờ/config. "
            f"Ex-post (chỉ mô tả, không dùng làm bộ lọc live): ngày giảm {b['expost_down_mean'] if b['expost_down_mean'] is None else round(b['expost_down_mean'],1)} bps (n={b['expost_down_n']}), "
            f"ngày tăng {b['expost_up_mean'] if b['expost_up_mean'] is None else round(b['expost_up_mean'],1)} bps (n={b['expost_up_n']}). BQ tới {bq_max}.")


def load_state(path):
    try:
        with open(path) as fh: return json.load(fh)
    except FileNotFoundError:
        return {"posted": {}}
    except ValueError as e:
        raise MonitorError(f"state file {path} hỏng JSON ({e}) — không đoán, kiểm tra tay")


def save_state(path, st):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".ftm_", suffix=".tmp")
    with os.fdopen(fd, "w") as fh: json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, path)


def post(msg, st, key, args):
    """Idempotent: key đã post thì bỏ qua; ghi state ngay sau khi post thành công (§5)."""
    if key in st["posted"]:
        return False
    cmd = args.notify_cmd.split() + [msg, NOTIFY_CHANNEL]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print(f"notify rc={p.returncode}: {(p.stderr or p.stdout).strip()[-300:]}", file=sys.stderr)
        return False
    st["posted"][key] = datetime.now(ICT).isoformat(timespec="seconds")
    save_state(args.state, st)
    return True


def run(args):
    today = args.today or datetime.now(ICT).strftime("%Y-%m-%d")
    st = load_state(args.state)
    M = load_orders(args.log_dir, today)
    if args.open_csv:
        B = pd.read_csv(args.open_csv); bq_max = str(B.d.max())
    else:
        B, bq_max = load_open_bq(set(M[M.cls == "HYB_IN_BLOCK"].sym))
    U, pending = build_units(M, B)
    res = evaluate(U)
    wk = pd.Timestamp(today).strftime("%G-W%V")
    line = progress_line(res, bq_max, pending, today)
    print(line)
    st["last_run"] = dict(today=today, bq_max=bq_max, pending_orders=pending,
                          res={s: {k: v for k, v in res[s].items() if k in ("n_units", "n_weeks", "enough_N")} for s in ("BUY", "SELL")})
    rc = 0
    if res["alert"]:
        rc = 2
        post(alert_text(res, bq_max, today), st, f"alert_{wk}", args)
    if args.force_weekly or pd.Timestamp(today).weekday() == 0:
        post(line, st, f"weekly_{wk}", args)
    save_state(args.state, st)
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    ap.add_argument("--open-csv", help="bỏ BQ, dùng CSV ticker,d,Open,Close,Price (selfcheck/offline)")
    ap.add_argument("--today", help="YYYY-MM-DD ICT (test); mặc định hôm nay theo ICT")
    ap.add_argument("--notify-cmd", default=str(HERE / "notify_thread.sh"))
    ap.add_argument("--force-weekly", action="store_true")
    args = ap.parse_args(argv)
    try:
        return run(args)
    except Exception as e:  # fail-closed, không crash im lặng
        reason = f"{type(e).__name__}: {e}"
        today = args.today or datetime.now(ICT).strftime("%Y-%m-%d")
        print("monitor không chạy được vì " + reason, file=sys.stderr)
        try:
            st = load_state(args.state)
        except MonitorError:
            st = {"posted": {}}
        key = "fail_%s_%s" % (today, hashlib.md5(reason.encode()).hexdigest()[:8])
        post(f"⚠️ fill_timing monitor không chạy được vì {reason[:500]} ({today})", st, key, args)
        return 1


if __name__ == "__main__":
    sys.exit(main())
