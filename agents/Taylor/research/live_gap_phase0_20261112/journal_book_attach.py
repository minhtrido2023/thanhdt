#!/usr/bin/env python3
"""GD0 viec 3 — gan so BOOK cho moi FILL tu 2026-07-01 (journal exec_<acct>_<date>_journal.csv).
KHONG sua file goc. Xuat fills_booked.csv + book_summary.csv/md.
Thu tu suy book (certainty): journal_col > plan_id (id lenh trong plan_<acct>_<date>.json) > plan_ticker_side (cung ngay)
 > parent_pattern > ticker_lineage (book cua lo mua gan nhat cung ma) > UNKNOWN.
P&L thuc hien = FIFO theo (acct,ticker), phi 0.097%/chieu (CLAUDE.md §6), quy ve book cua LO MUA. Khong dieu chinh corp-action
(chia/thuong co phieu) => xap xi; sell khong co lo mua trong cua so (vi the legacy truoc 07-01/07-06) bi tach ra 'unmatched'.
Chay: /home/trido/thanhdt/wc_venv/bin/python journal_book_attach.py"""
import csv, glob, json, os, re, collections
import pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"; LOG = f"{WC}/data/execution_logs"; PL = f"{WC}/data/trade_plans"
HERE = os.path.dirname(os.path.abspath(__file__)); FEE = 0.00097
NORM = {"custom30V_parking": "PARK", "PARK": "PARK", "legacy_orphan": "LEGACY_ORPHAN", "DISCRETIONARY_SPECIAL": "DISCRETIONARY",
        "DISCRETIONARY": "DISCRETIONARY"}
def nb(b): return NORM.get(b, b)

# --- plan index
plan_id, plan_ts = {}, collections.defaultdict(set)
for f in sorted(glob.glob(f"{PL}/plan_*_2026-*.json")):
    m = re.match(r"plan_(SpaceX|ZaloPay)_(\d{4}-\d\d-\d\d)\.json$", os.path.basename(f))
    if not m: continue
    a, d = m.groups()
    try: P = json.load(open(f))
    except Exception: continue
    for o in P.get("orders", []):
        if not o.get("book") or o.get("book") == "PROBE": continue
        if o.get("id"): plan_id[(a, d, o["id"])] = (nb(o["book"]), o.get("play_type"))
        plan_ts[(a, d, o.get("ticker"), o.get("side"))].add(nb(o["book"]))
for f in sorted(glob.glob(f"{PL}/park_trim_*_2026-*.json") + glob.glob(f"{PL}/jit_unpark_*_2026-*.json")):
    m = re.match(r"(park_trim|jit_unpark)_(SpaceX|ZaloPay)_(\d{4}-\d\d-\d\d)\.json$", os.path.basename(f))
    if m:
        for (a, d) in [(m.group(2), m.group(3))]:
            plan_ts[(a, d, "__PARKFILE__", None)].add("PARK")

# --- journal fills
fills = []
for f in sorted(glob.glob(f"{LOG}/exec_SpaceX_*_journal.csv") + glob.glob(f"{LOG}/exec_ZaloPay_*_journal.csv")):
    a, d = re.match(r"exec_(\w+?)_(\d{4}-\d\d-\d\d)_journal", os.path.basename(f)).groups()
    if d < "2026-07-01": continue
    with open(f, newline="") as fh:
        r = csv.reader(fh); h = next(r); n = len(h)
        for ln in r:
            row = dict(zip(h, ln[:n - 1])); row["note"] = ",".join(ln[n - 1:])
            if row["event"] != "FILL": continue
            row.update(acct=a, date=d, src=os.path.basename(f), has_book_col="book" in h); fills.append(row)
df = pd.DataFrame(fills)
for c in ("book", "play_type"):
    if c not in df: df[c] = ""
df[["book", "play_type"]] = df[["book", "play_type"]].fillna("")
df["qty"] = df.qty.astype(float); df["price"] = df.price.astype(float)
n0 = len(df)
df = df.drop_duplicates(["acct", "date", "ts", "parent_id", "child_oid", "qty", "price", "filled_total"])
print("fills", n0, "after dedupe", len(df))
df = df.sort_values(["acct", "ts"]).reset_index(drop=True)

def pat(pid):
    if pid.startswith("PARKMERGE"): return "PARK"
    if "AUTOEXIT-CAPIT" in pid or "CAPIT" in pid: return "CAPIT"
    if "-LAG-" in pid or pid.endswith("-LAG") or "LAG" in pid: return "LAG"
    if "DISC" in pid or "-EXIT-" in pid: return "DISCRETIONARY"
    if "JIT" in pid or "PARK" in pid: return "PARK"
    return None
lineage = {}
out_book, out_basis, out_conf = [], [], []
for _, r in df.iterrows():
    a, d, pid, t, s = r.acct, r.date, r.parent_id, r.ticker, r.side
    b = basis = conf = None
    if r.book:
        b, basis, conf = nb(r.book), "journal_col", "high"
    elif (a, d, pid) in plan_id:
        b, basis, conf = plan_id[(a, d, pid)][0], "plan_id", "high"
    elif len(plan_ts.get((a, d, t, s), ())) == 1:
        b, basis, conf = next(iter(plan_ts[(a, d, t, s)])), "plan_ticker_side", "medium"
    elif pat(pid):
        b, basis, conf = pat(pid), "parent_pattern", "medium" if pat(pid) == "PARK" and "PARKMERGE" in pid else "low"
    elif (a, t) in lineage:
        b, basis, conf = lineage[(a, t)], "ticker_lineage", "low"
    else:
        b, basis, conf = "UNKNOWN", "none", "none"
    if s == "buy" and b not in ("UNKNOWN",): lineage[(a, t)] = b
    out_book.append(b); out_basis.append(basis); out_conf.append(conf)
df["book_inferred"], df["book_basis"], df["book_certainty"] = out_book, out_basis, out_conf
df["notional"] = df.qty * df.price

# --- FIFO realized P&L
lots = collections.defaultdict(list); pnl = collections.defaultdict(float); unm = collections.defaultdict(float)
rl = []
for i, r in df.iterrows():
    k = (r.acct, r.ticker)
    if r.side == "buy":
        lots[k].append([r.qty, r.price * (1 + FEE), r.book_inferred]); rl.append(None)
    else:
        q = r.qty; net = r.price * (1 - FEE); tot = 0.0; used = False
        while q > 0 and lots[k]:
            L = lots[k][0]; u = min(q, L[0]); p = u * (net - L[1]); pnl[(r.acct, L[2])] += p; tot += p
            L[0] -= u; q -= u; used = True
            if L[0] <= 1e-9: lots[k].pop(0)
        if q > 0: unm[(r.acct, r.book_inferred)] += q * r.price
        rl.append(tot)
df["realized_pnl_fifo"] = rl
df.drop(columns=["has_book_col"]).to_csv(f"{HERE}/fills_booked.csv", index=False)

g = df.groupby(["acct", "book_inferred", "side"]).agg(fills=("qty", "size"), orders=("parent_id", "nunique"), notional_vnd=("notional", "sum")).reset_index()
pv = g.pivot_table(index=["acct", "book_inferred"], columns="side", values=["fills", "orders", "notional_vnd"], fill_value=0)
pv.columns = [f"{a}_{b}" for a, b in pv.columns]; pv = pv.reset_index()
pv["realized_pnl_fifo_vnd(lo_mua_thuoc_book)"] = [round(pnl.get((a, b), 0.0)) for a, b in zip(pv.acct, pv.book_inferred)]
pv["unmatched_sell_notional_vnd"] = [round(unm.get((a, b), 0.0)) for a, b in zip(pv.acct, pv.book_inferred)]
pv.to_csv(f"{HERE}/book_summary.csv", index=False)
cert = df.groupby(["acct", "book_basis", "book_certainty"]).agg(fills=("qty", "size"), notional_vnd=("notional", "sum")).reset_index()
cert.to_csv(f"{HERE}/book_certainty.csv", index=False)
blank = df[~df.apply(lambda r: bool(r.book), axis=1)]
print("fills", len(df), "journal book blank:", blank.groupby("acct").size().to_dict())
print(cert.to_string())
pd.set_option("display.width", 250); pd.set_option("display.float_format", lambda x: f"{x:,.0f}")
print(pv.to_string())
print("REALIZED by acct:", {a: round(sum(v for (aa, b), v in pnl.items() if aa == a)) for a in ("SpaceX", "ZaloPay")})
