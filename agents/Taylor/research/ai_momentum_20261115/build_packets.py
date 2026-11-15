"""P0 dry-run: chon 10 su kien R4 ngau nhien (seed co dinh) trong [2026-07-01, 2026-10-14] (>=20 phien sau T de cham canary),
dung goi bang chung PIT: stats + rating as-of + BCTC co Release_Date<=T + stock_news public_date in [T-120,T]. KHONG co gia sau T."""
import sys, json, subprocess, numpy as np, pandas as pd
D = sys.argv[1]
BANNED = "PC1 VVS KSF NKG HSG HVN VJC NVL GEG SBA DMC IMP TRA TOS VTP BAF".split()
ev = pd.read_csv(f"{D}/events.csv", parse_dates=["time"])
ev = ev[(ev.variant == "R4") & (ev.time >= "2026-07-01") & (ev.time <= "2026-10-14")].sort_values(["time", "ticker"])
pick = ev.iloc[np.sort(np.random.default_rng(20261115).choice(len(ev), 10, replace=False))]
ff = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/forensic_flags.csv", parse_dates=["date"])
def bq(sql):
    out = subprocess.run(["bash", "-c", "source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null; bq query --use_legacy_sql=false "
        "--project_id=lithe-record-440915-m9 --format=json --max_rows=10000 \"$Q\""], env={"Q": sql, "PATH": "/usr/bin:/bin:/usr/local/bin",
        "HOME": "/home/trido"}, capture_output=True, text=True)
    if out.returncode: raise SystemExit(out.stderr[-2000:])
    return json.loads(out.stdout or "[]")
tks = ",".join(f'"{t}"' for t in pick.ticker)
news = pd.DataFrame(bq(f"""SELECT n.ticker, n.public_date, n.public_datetime, n.title, n.matched_event_codes, DATE(n.ingested_at) ing
  FROM tav2_bq.stock_news AS n WHERE n.ticker IN ({tks}) AND n.public_date BETWEEN "2026-03-01" AND "2026-10-14"
  GROUP BY 1,2,3,4,5,6"""))
fin = pd.DataFrame(bq(f"""SELECT f.ticker, f.quarter, f.Release_Date, f.NP_P0, f.NP_P4, f.Revenue_P0, f.Revenue_YoY_P0, f.GPM_P0, f.PE, f.PB, f.ROE_Trailing
  FROM tav2_bq.ticker_financial AS f WHERE f.ticker IN ({tks}) AND f.time>="2025-01-01" """))
fin["Release_Date"] = pd.to_datetime(fin.Release_Date); news["public_date"] = pd.to_datetime(news.public_date)
packets = []
for _, r in pick.iterrows():
    T = r.time; tk = r.ticker
    n = news[(news.ticker == tk) & (news.public_date <= T) & (news.public_date >= T - pd.Timedelta(days=120))].sort_values("public_date")
    f = fin[(fin.ticker == tk) & (fin.Release_Date <= T)].sort_values("Release_Date").tail(3)
    dd = tk in BANNED or bool(((ff.ticker == tk) & (ff.severity == "exclude") & (ff.date <= T)).any())
    packets.append({"event_id": f"{tk}_{T.date()}", "ticker": tk, "T": str(T.date()),
        "stats": {"mom20": r.mom20, "idio20": r.idio20, "volr": r.volr, "newhi_3m": True, "liq_bn": r.liq_bn,
                  "route_8l": r.route, "rating_8l_asof": int(r.rating), "rating_eff_date": str(r.rt_time)[:10], "dd_flag": dd},
        "financials_released_le_T": [{k: (None if pd.isna(v) else (str(v)[:10] if k == "Release_Date" else v)) for k, v in x.items() if k != "ticker"}
                                      for x in f.to_dict("records")],
        "news_le_T": [{"date": str(x.public_date.date()), "time": x.public_datetime, "title": x.title, "codes": x.matched_event_codes,
                       "ingested": x.ing} for x in n.itertuples()]})
json.dump(packets, open(f"{D}/dryrun_packets.json", "w"), ensure_ascii=False, indent=1, default=float)
for p in packets: print(p["event_id"], p["stats"]["route_8l"], p["stats"]["rating_8l_asof"], "dd" if p["stats"]["dd_flag"] else "", "news", len(p["news_le_T"]), "fin", len(p["financials_released_le_T"]))
