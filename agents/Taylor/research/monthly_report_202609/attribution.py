import json, csv, glob, subprocess, collections
EX = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
def lastpos(d, no):
    last = None
    for l in open(f"{EX}/dnse_raw_{d}.jsonl"):
        r = json.loads(l)
        if r["kind"] == "positions" and str(r["account_no"]) == no: last = r
    q = collections.Counter()
    for p in last["payload"]["positions"]:
        if str(p.get("accountNo")) == no and (p.get("openQuantity") or 0) > 0: q[p["symbol"]] += p["openQuantity"]
    return last["ts"], q
fills = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))  # acc->tk->[buy_val, sell_val]
for acc in ACC:
    for f in glob.glob(f"{EX}/exec_{acc}_2026-09-*_journal.csv"):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r["event"] == "FILL":
                v = float(r["qty"]) * float(r["price"])
                fills[acc][r["ticker"]][0 if r["side"] == "buy" else 1] += v
fills["SpaceX"]["SCL"][1] += 1500 * 28300   # bán tay 30/09, đối soát qua email khớp lệnh (memory 2026-09-30) + Δcash 42.369.759
pos = {acc: (lastpos("2026-08-31", no), lastpos("2026-09-30", no)) for acc, no in ACC.items()}
tks = sorted({t for acc in pos for side in pos[acc] for t in side[1]} | {t for acc in fills for t in fills[acc]})
q = ("SELECT t.ticker, CAST(t.time AS STRING) d, t.Price FROM tav2_bq.ticker AS t WHERE t.time IN ('2026-08-28','2026-09-30') AND t.ticker IN (" + ",".join(f"'{x}'" for x in tks) + ")")
out = subprocess.run(["bash", "-c", f"source /home/trido/thanhdt/WorkingClaude/wc_env.sh; bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=json --max_rows=10000 \"{q}\""], capture_output=True, text=True).stdout
px = {(r["ticker"], r["d"]): float(r["Price"]) for r in json.loads(out)}
res = {}
for acc in ACC:
    (t0, q0), (t1, q1) = pos[acc]
    rows = []
    for t in sorted(set(q0) | set(q1) | set(fills[acc])):
        mv0 = q0.get(t, 0) * px.get((t, "2026-08-28"), 0); mv1 = q1.get(t, 0) * px.get((t, "2026-09-30"), 0)
        b, s = fills[acc][t]
        rows.append(dict(tk=t, q0=q0.get(t, 0), q1=q1.get(t, 0), p0=px.get((t, "2026-08-28")), p1=px.get((t, "2026-09-30")), mv0=mv0, mv1=mv1, buy=b, sell=s, pl_price=mv1 + s - mv0 - b))
    res[acc] = dict(ts0=t0, ts1=t1, rows=rows, mv0=sum(r["mv0"] for r in rows), mv1=sum(r["mv1"] for r in rows), pl_price=sum(r["pl_price"] for r in rows), buy=sum(r["buy"] for r in rows), sell=sum(r["sell"] for r in rows))
    print("==", acc, t0, t1, "mv0", round(res[acc]["mv0"]), "mv1", round(res[acc]["mv1"]), "pl_price", round(res[acc]["pl_price"]), "buy", res[acc]["buy"], "sell", res[acc]["sell"])
    for r in sorted(rows, key=lambda r: r["pl_price"]):
        print(f'  {r["tk"]} q {r["q0"]}->{r["q1"]} p {r["p0"]}->{r["p1"]} buy {r["buy"]:.0f} sell {r["sell"]:.0f} pl {r["pl_price"]:.0f}')
json.dump(res, open("attribution.json", "w"), indent=1)
