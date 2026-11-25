# -*- coding: utf-8 -*-
"""a0_fetch_delisted.py — sửa lỗi skeptic #3 (SỐNG SÓT): kéo giá + BCTC quý của các mã CÓ ở VNDirect finfo (listed/delisted)
nhưng VẮNG trong cache BQ `ticker`. Nguồn ngoài BQ, công khai: https://api-finfo.vndirect.com.vn/v4/{stocks,stock_prices,financial_statements}.
Không gửi thông tin định danh nào. Out: ../out/delisted/{stocks.json, px_<T>.csv, fs_<T>.csv, fetch_log.csv}. Idempotent (bỏ qua file đã có)."""
import os, sys, json, time, glob
import requests, pandas as pd, duckdb
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out", "delisted"); WC = "/home/trido/thanhdt/WorkingClaude"
H = {"User-Agent": "Mozilla/5.0"}; B = "https://api-finfo.vndirect.com.vn/v4"
ITEMS = "12700,13000,14000,14110,21001,23100,23800,23000,23003,32000,32100,33600,11100,13120,13340,22509,22230"
def get(url, tries=4):
    for k in range(tries):
        try:
            r = requests.get(url, headers=H, timeout=40)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(1.5 * (k + 1))
    return None
def pages(url, size):
    out = []; p = 1
    while True:
        d = get(f"{url}&size={size}&page={p}")
        if d is None:
            return None
        out += d.get("data", [])
        if p >= d.get("totalPages", 1):
            return out
        p += 1
sp = os.path.join(OUT, "stocks.json")
if not os.path.exists(sp):
    st = pages(f"{B}/stocks?q=type:STOCK~status:listed,delisted", 3000); json.dump(st, open(sp, "w"), ensure_ascii=False)
st = pd.DataFrame(json.load(open(sp)))
have = set(duckdb.connect().execute(f"SELECT DISTINCT ticker FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')").df().ticker)
miss = st[~st.code.isin(have) & (st.code.str.len() == 3)].copy()
print("VND stocks", len(st), "status", st.status.value_counts().to_dict(), "| vắng trong BQ cache:", len(miss), miss.status.value_counts().to_dict(), flush=True)
def one(code):
    fp = os.path.join(OUT, f"px_{code}.csv"); ff = os.path.join(OUT, f"fs_{code}.csv"); npx = nfs = -1
    if not os.path.exists(fp):
        d = pages(f"{B}/stock_prices?sort=date&q=code:{code}~date:gte:2006-01-01", 5000)
        if d is not None:
            df = pd.DataFrame(d)
            cols = [c for c in ["code", "date", "floor", "close", "adClose", "nmVolume", "nmValue", "ptValue"] if c in df.columns]
            (df[cols] if len(df) else pd.DataFrame(columns=["code", "date"])).to_csv(fp, index=False); npx = len(df)
    if not os.path.exists(ff):
        d = pages(f"{B}/financial_statements?q=code:{code}~reportType:QUARTER~itemCode:{ITEMS}", 3000)
        if d is not None:
            df = pd.DataFrame(d)
            cols = [c for c in ["code", "itemCode", "modelType", "numericValue", "fiscalDate", "createdDate", "modifiedDate"] if c in df.columns]
            (df[cols] if len(df) else pd.DataFrame(columns=["code", "itemCode"])).to_csv(ff, index=False); nfs = len(df)
    return code, npx, nfs
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, miss.code.tolist()))
pd.DataFrame(res, columns=["code", "n_px", "n_fs"]).to_csv(os.path.join(OUT, "fetch_log.csv"), index=False)
print("done", len(res), "px files", len(glob.glob(os.path.join(OUT, "px_*.csv"))), "fs files", len(glob.glob(os.path.join(OUT, "fs_*.csv"))))
