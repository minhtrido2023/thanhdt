#!/usr/bin/env python3
"""Fetch foreign-flow data from VNDirect finfo API (index + VN30F front-month).
Cache to agents/Taylor/foreign_flow_vnindex.csv + foreign_flow_vn30f.csv.
No auth; needs User-Agent + Referer headers. Filter field is `tradingDate` (NOT `date`).
"""
import sys, time, io
import requests
import pandas as pd

BASE = "https://api-finfo.vndirect.com.vn/v4/foreigns"
HDR = {"User-Agent": "Mozilla/5.0", "Referer": "https://dstock.vndirect.com.vn/"}
OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor"
START = "2018-08-30"
TODAY = "2026-07-23"


def fetch_q(q, size=3000):
    url = f"{BASE}?q={q}&sort=tradingDate:asc&size={size}"
    for attempt in range(4):
        r = requests.get(url, headers=HDR, timeout=30)
        if r.status_code == 200:
            return r.json().get("data", [])
        time.sleep(1.5)
    raise RuntimeError(f"HTTP {r.status_code} for {url}\n{r.text[:300]}")


def fetch_index():
    q = f"code:VNINDEX~tradingDate:gte:{START}"
    data = fetch_q(q)
    df = pd.DataFrame(data)
    df["tradingDate"] = pd.to_datetime(df["tradingDate"])
    df = df.sort_values("tradingDate").reset_index(drop=True)
    print(f"[index] VNINDEX foreign flow: {len(df)} rows {df.tradingDate.min().date()} -> {df.tradingDate.max().date()}")
    df.to_csv(f"{OUT}/foreign_flow_vnindex.csv", index=False)
    return df


def fetch_vn30f():
    """Chain VN30F front-month contracts. Contract code VN30Fyymm, type=FU, floor=HNX.
    Front month = the nearest-expiry contract active on each date. VN30 futures expire
    3rd Thursday of contract month. We fetch all monthly contracts across the window and
    stitch: for each trading date use the contract whose month is the current/next expiry.
    Simpler robust approach: fetch each monthly contract's full series, then for each date
    pick the contract with the smallest positive days-to-expiry-month.
    """
    frames = []
    # contracts from 2018-08 .. 2026-08
    for yy in range(18, 27):
        for mm in range(1, 13):
            if yy == 18 and mm < 8:
                continue
            if yy == 26 and mm > 8:
                continue
            code = f"VN30F{yy:02d}{mm:02d}"
            try:
                data = fetch_q(f"code:{code}~tradingDate:gte:{START}", size=3000)
            except Exception as e:
                print(f"  {code}: ERR {e}")
                continue
            if not data:
                continue
            d = pd.DataFrame(data)
            d["contract"] = code
            d["expiry_ym"] = (2000 + yy) * 100 + mm
            frames.append(d)
            print(f"  {code}: {len(d)} rows")
            time.sleep(0.15)
    if not frames:
        raise RuntimeError("no VN30F data")
    allc = pd.concat(frames, ignore_index=True)
    allc["tradingDate"] = pd.to_datetime(allc["tradingDate"])
    # front-month select: for each date, contract with smallest expiry_ym >= date's ym
    allc["date_ym"] = allc["tradingDate"].dt.year * 100 + allc["tradingDate"].dt.month
    allc = allc[allc["expiry_ym"] >= allc["date_ym"]].copy()
    allc = allc.sort_values(["tradingDate", "expiry_ym"])
    front = allc.groupby("tradingDate", as_index=False).first()
    front = front.sort_values("tradingDate").reset_index(drop=True)
    print(f"[deriv] VN30F front-month: {len(front)} rows {front.tradingDate.min().date()} -> {front.tradingDate.max().date()}")
    front.to_csv(f"{OUT}/foreign_flow_vn30f.csv", index=False)
    return front


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "index"):
        fetch_index()
    if what in ("all", "deriv"):
        fetch_vn30f()
