import subprocess, tempfile, os, pandas as pd
WORKDIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = "lithe-record-440915-m9"
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        out = subprocess.run(["bq","query","--use_legacy_sql=false","--format=csv","--max_rows=10000000",f"--project_id={PROJECT}"],
                              stdin=open(tmp), capture_output=True, text=True, timeout=580)
        if out.returncode != 0: raise RuntimeError(out.stderr)
        from io import StringIO
        return pd.read_csv(StringIO(out.stdout))
    finally: os.unlink(tmp)
START, END = "2014-01-01", "2026-09-03"
q = pd.read_csv(f"{WORKDIR}/quarterly_panel.csv")
tks = sorted(q.ticker.unique().tolist())
tk_list = ",".join(f"'{t}'" for t in tks)
print(f"[3] daily close for {len(tks)} tickers...")
px = bq(f"""SELECT t.ticker AS ticker, t.time AS time, t.Close AS Close FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tk_list}) AND t.time BETWEEN DATE '{START}' AND DATE '{END}'""")
px.to_csv(f"{WORKDIR}/daily_close.csv", index=False)
print(f"  rows={len(px)} tickers={px.ticker.nunique()}")
print("[4] vnindex...")
vni = bq(f"""SELECT t.time AS time, t.Close AS Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX'
AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time""")
vni.to_csv(f"{WORKDIR}/vnindex.csv", index=False)
print(f"  rows={len(vni)}")
