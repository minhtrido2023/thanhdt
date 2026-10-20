"""Selfcheck — guard Release_Date khong dang tin trong rating_8l_history (job Taylor_20261020_045223, user duyet
2026-10-20). Luat: RD <= RD quy LIEN TRUOC (cung ma) HOAC RD < cuoi quy => eff_date = q_time (ticker_financial.time).

  G1  7 ca chac chan trong universe (gia tri literal tu ticker_financial 2026-10-20) -> co, eff = time.
  G2  RD < cuoi quy nhung > RD quy truoc (HVA/CT6 2026Q2) -> co, eff = time.
  G3  RD NULL -> khong co; eff = q_time (offset 0) — hanh vi cu giu nguyen.
  G4  Ngan hang: bank_eff_date theo guard; ngan hang binh thuong khong doi.
  G5  Ca binh thuong (RD > cuoi quy, > RD quy truoc) -> khong doi.
  G6  Bang nhau truoc 2026 (TA9 2015Q2: RD == RD quy truoc == time) -> co nhung eff KHONG doi.
  G7  Quy truoc thieu / RD quy truoc NULL -> chi xet luat cuoi quy.
  G8  Cum Q1 RD dau thang 4 (> cuoi quy) -> CO Y khong co (ngoai pham vi luat).
  G9  RD == cuoi quy -> khong co (luat la '<' chat).
  G10 index lon xon / thu tu dong lon xon -> ket qua gan dung dong.
  G11 eff_date_of scalar: rd_untrusted True/False/None/NaN.
  G12 attach_icb_pit dung eff da guard (bien ICB nam giua RD va time).
  G13 main(): rd_untrusted tinh TRUOC attach_icb_pit; HIST_SQL co f.quarter.
  G14 du lieu that (raw/tf_current.csv neu co): tap co = 27 dong, 22 dong doi eff, 7 trong universe.

Khong cham Executor; van dat MIKE_BOT_TEST_MODE=1 phong khi (§5b). Chay: python3 rating8l_eff_guard_selfcheck.py
"""
import os
import sys

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rating_8l_history as R

PASS = FAIL = SKIP = 0


def ok(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"PASS {name}")
    else:
        FAIL += 1; print(f"FAIL {name} — {detail}")


T = pd.Timestamp


def mk(rows):
    """rows = (ticker, quarter, Release_Date|None, q_time)"""
    return pd.DataFrame([{"ticker": t, "quarter": q, "Release_Date": rd, "q_time": qt} for t, q, rd, qt in rows])


def run(df):
    df = df.copy()
    df["rd_untrusted"] = R.release_date_untrusted(df)
    df["eff"] = R.eff_date_of(df["Release_Date"], df["q_time"], df["rd_untrusted"])
    return df


def row(df, t, q):
    return df[(df["ticker"] == t) & (df["quarter"] == q)].iloc[0]


# ---- G1: 7 ca chac chan (prev quarter row + flagged row) ----
G1 = [("BGE", "2026-02-02", "2026Q1", "2026-02-02", "2026-05-04"),
      ("BOT", "2026-01-28", "2026Q1", "2026-01-28", "2026-05-04"),
      ("DGT", "2026-02-02", "2026Q1", "2026-02-02", "2026-05-04"),
      ("HVA", "2026-01-22", "2026Q1", "2026-01-22", "2026-05-04"),
      ("VNE", "2026-02-02", "2026Q1", "2026-02-02", "2026-05-04"),
      ("SGP", "2026-05-04", "2026Q2", "2026-05-04", "2026-08-03"),
      ("VHE", "2026-05-04", "2026Q2", "2026-05-04", "2026-08-03")]
rows = []
for t, prd, q, rd, qt in G1:
    pq = "2025Q4" if q == "2026Q1" else "2026Q1"
    rows += [(t, pq, prd, prd), (t, q, rd, qt)]
d1 = run(mk(rows))
for t, prd, q, rd, qt in G1:
    r = row(d1, t, q)
    ok(f"G1 {t} {q}: co + eff=time {qt}", bool(r["rd_untrusted"]) and r["eff"] == T(qt), f"{r.to_dict()}")
    pr = row(d1, t, "2025Q4" if q == "2026Q1" else "2026Q1")
    ok(f"G1 {t} quy truoc khong bi danh dau, eff=RD", (not pr["rd_untrusted"]) and pr["eff"] == T(prd), f"{pr.to_dict()}")
ok("G1 eff moi KHAC eff quy truoc (het ghi de dong rating quy truoc)",
   all(row(d1, t, q)["eff"] != row(d1, t, "2025Q4" if q == "2026Q1" else "2026Q1")["eff"] for t, _, q, _, _ in G1))

# ---- G2: RD < cuoi quy, RD > RD quy truoc ----
d2 = run(mk([("HVA", "2026Q1", "2026-01-22", "2026-05-04"), ("HVA", "2026Q2", "2026-05-04", "2026-08-07"),
             ("CT6", "2026Q1", "2026-02-02", "2026-05-04"), ("CT6", "2026Q2", "2026-05-04", "2026-08-14")]))
ok("G2 HVA 2026Q2 (RD 05-04 < 06-30, > RD Q1) -> eff 2026-08-07",
   bool(row(d2, "HVA", "2026Q2")["rd_untrusted"]) and row(d2, "HVA", "2026Q2")["eff"] == T("2026-08-07"))
ok("G2 CT6 2026Q2 -> eff 2026-08-14", row(d2, "CT6", "2026Q2")["eff"] == T("2026-08-14"))

# ---- G3: RD NULL ----
d3 = run(mk([("AAA", "2025Q4", "2026-01-20", "2026-01-20"), ("AAA", "2026Q1", None, "2026-05-02")]))
ok("G3 RD NULL -> khong co, eff = q_time (offset 0)",
   (not row(d3, "AAA", "2026Q1")["rd_untrusted"]) and row(d3, "AAA", "2026Q1")["eff"] == T("2026-05-02"))
d3b = run(mk([("AAA", "2025Q4", None, "2026-01-20"), ("AAA", "2026Q1", None, "2026-05-02")]))
ok("G3b toan cot RD NULL khong crash, khong co", (~d3b["rd_untrusted"]).all() and d3b["eff"].tolist() == [T("2026-01-20"), T("2026-05-02")])

# ---- G4: ngan hang ----
ok("G4a bank_eff_date: rd_untrusted True -> q_time",
   R.bank_eff_date({"Release_Date": "2026-02-02", "q_time": "2026-05-04", "rd_untrusted": True}) == T("2026-05-04"))
ok("G4b bank_eff_date: binh thuong -> RD",
   R.bank_eff_date({"Release_Date": "2026-04-28", "q_time": "2026-04-28", "rd_untrusted": False}) == T("2026-04-28"))
ok("G4c bank_eff_date: thieu khoa rd_untrusted (caller cu) -> RD",
   R.bank_eff_date({"Release_Date": "2026-04-28", "q_time": "2026-04-29"}) == T("2026-04-28"))
d4 = run(mk([("VCB", "2025Q4", "2026-01-27", "2026-01-27"), ("VCB", "2026Q1", "2026-04-28", "2026-04-28")]))
ok("G4d ngan hang binh thuong VCB 2026Q1 -> khong co, eff=RD",
   (not row(d4, "VCB", "2026Q1")["rd_untrusted"]) and row(d4, "VCB", "2026Q1")["eff"] == T("2026-04-28"))

# ---- G5: binh thuong ----
d5 = run(mk([("FPT", "2025Q4", "2026-01-25", "2026-01-25"), ("FPT", "2026Q1", "2026-04-20", "2026-04-21")]))
ok("G5 ca binh thuong -> eff = RD (2026-04-20), khong phai time",
   (not row(d5, "FPT", "2026Q1")["rd_untrusted"]) and row(d5, "FPT", "2026Q1")["eff"] == T("2026-04-20"))

# ---- G6: bang nhau truoc 2026 ----
d6 = run(mk([("TA9", "2015Q1", "2015-08-03", "2015-08-03"), ("TA9", "2015Q2", "2015-08-03", "2015-08-03")]))
ok("G6 TA9 2015Q2 RD == RD Q1 -> co, eff khong doi (2015-08-03)",
   bool(row(d6, "TA9", "2015Q2")["rd_untrusted"]) and row(d6, "TA9", "2015Q2")["eff"] == T("2015-08-03"))

# ---- G7: quy truoc thieu / NULL ----
d7 = run(mk([("BBB", "2025Q3", "2025-10-20", "2025-10-20"), ("BBB", "2026Q1", "2025-10-20", "2026-04-25")]))
ok("G7a quy LIEN truoc (2025Q4) thieu -> khong so voi 2025Q3; RD < cuoi quy van co",
   bool(row(d7, "BBB", "2026Q1")["rd_untrusted"]) and row(d7, "BBB", "2026Q1")["eff"] == T("2026-04-25"))
d7b = run(mk([("BBB", "2025Q3", "2026-04-25", "2025-10-20"), ("BBB", "2026Q1", "2026-04-20", "2026-04-25")]))
ok("G7b quy cach 1 quy (2025Q3) KHONG duoc dung lam 'quy truoc'", not row(d7b, "BBB", "2026Q1")["rd_untrusted"])
d7c = run(mk([("CCC", "2025Q4", None, "2026-02-01"), ("CCC", "2026Q1", "2026-04-20", "2026-04-20")]))
ok("G7c RD quy truoc NULL -> khong co", not row(d7c, "CCC", "2026Q1")["rd_untrusted"])
d7d = run(mk([("DDD", "2025Q4", "2026-02-01", "2026-02-01"), ("DDD", "2026Q1", "2026-04-20", "2026-04-20"),
              ("EEE", "2025Q4", "2026-05-01", "2026-05-01"), ("EEE", "2026Q1", "2026-04-20", "2026-04-20")]))
ok("G7d khong lan ma: DDD binh thuong khong bi danh dau vi RD cua EEE",
   (not row(d7d, "DDD", "2026Q1")["rd_untrusted"]) and bool(row(d7d, "EEE", "2026Q1")["rd_untrusted"]))
d7e = run(mk([("FFF", "2025Q4", "2026-01-30", "2026-01-30"), ("FFF", "2026Q1", "2026-01-31", "2026-05-04")]))
ok("G7e RD > RD quy truoc nhung < cuoi quy -> co", bool(row(d7e, "FFF", "2026Q1")["rd_untrusted"]))

# ---- G8: cum Q1 dau thang 4 ----
d8 = run(mk([("TLP", "2025Q4", "2026-02-02", "2026-02-02"), ("TLP", "2026Q1", "2026-04-03", "2026-04-03")]))
ok("G8 TLP 2026Q1 RD 04-03 (> cuoi quy) -> CO Y khong co", not row(d8, "TLP", "2026Q1")["rd_untrusted"])

# ---- G9: RD == cuoi quy ----
d9 = run(mk([("GGG", "2025Q4", "2026-01-20", "2026-01-20"), ("GGG", "2026Q1", "2026-03-31", "2026-04-15")]))
ok("G9 RD == cuoi quy (03-31) -> khong co (luat '<' chat)", not row(d9, "GGG", "2026Q1")["rd_untrusted"])
d9b = run(mk([("GGG", "2025Q4", "2026-01-20", "2026-01-20"), ("GGG", "2026Q1", "2026-03-30", "2026-04-15")]))
ok("G9b RD 1 ngay truoc cuoi quy -> co", bool(row(d9b, "GGG", "2026Q1")["rd_untrusted"]))
d9c = run(mk([("HHH", "2025Q4", "2026-04-20", "2026-01-20"), ("HHH", "2026Q1", "2026-04-20", "2026-04-20")]))
ok("G9c RD == RD quy truoc (bang nhau) -> co ('<=')", bool(row(d9c, "HHH", "2026Q1")["rd_untrusted"]))

# ---- G10: index / thu tu lon xon ----
d10 = mk(rows).sample(frac=1.0, random_state=7)
d10.index = [100 + 3 * i for i in range(len(d10))][::-1]
d10 = run(d10)
ok("G10 index + thu tu lon xon: dung 7 dong co, dung ma/quy",
   sorted(zip(d10.loc[d10["rd_untrusted"], "ticker"], d10.loc[d10["rd_untrusted"], "quarter"]))
   == sorted((t, q) for t, _, q, _, _ in G1))

# ---- G11: scalar ----
ok("G11a scalar True -> q_time", R.eff_date_of("2026-02-02", "2026-05-04", True) == T("2026-05-04"))
ok("G11b scalar False -> RD", R.eff_date_of("2026-02-02", "2026-05-04", False) == T("2026-02-02"))
ok("G11c scalar None -> RD (hanh vi cu)", R.eff_date_of("2026-02-02", "2026-05-04", None) == T("2026-02-02"))
ok("G11d scalar NaN -> RD", R.eff_date_of("2026-02-02", "2026-05-04", float("nan")) == T("2026-02-02"))
ok("G11e scalar True + RD NULL -> q_time + offset (= q_time)", R.eff_date_of(None, "2026-05-04", True) == T("2026-05-04"))
ok("G11f Series khong truyen rd_untrusted -> hanh vi cu",
   list(R.eff_date_of(pd.Series(["2026-02-02", None]), pd.Series(["2026-05-04", "2026-05-04"])))
   == [T("2026-02-02"), T("2026-05-04")])

# ---- G12: attach_icb_pit dung eff da guard ----
icb = pd.DataFrame([{"ticker": "BGE", "ICB_Code": 8633, "icb_from": "2010-01-01"},
                    {"ticker": "BGE", "ICB_Code": 7535, "icb_from": "2026-03-15"}])
g = mk([("BGE", "2026Q1", "2026-02-02", "2026-05-04")]); g["rd_untrusted"] = [True]
ok("G12a attach_icb_pit: RD khong dang tin 02-02, time 05-04 -> ICB tai 05-04 (7535)",
   list(R.attach_icb_pit(g, icb)["ICB_Code"]) == [7535])
g["rd_untrusted"] = [False]
ok("G12b attach_icb_pit: cung dong, khong co -> ICB tai RD 02-02 (8633)", list(R.attach_icb_pit(g, icb)["ICB_Code"]) == [8633])
ok("G12c attach_icb_pit: thieu cot rd_untrusted (caller cu) -> nhu cu (8633)",
   list(R.attach_icb_pit(g.drop(columns=["rd_untrusted"]), icb)["ICB_Code"]) == [8633])

# ---- G13: noi day trong main / SQL ----
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rating_8l_history.py"), encoding="utf-8").read()
m = src[src.index("def main():"):]
ok("G13a main: rd_untrusted tinh TRUOC attach_icb_pit",
   0 < m.find('df["rd_untrusted"] = release_date_untrusted(df)') < m.find("attach_icb_pit(df, icb)"))
ok("G13b main: eff_date dung rd_untrusted",
   'df["eff_date"] = eff_date_of(df["Release_Date"], df["q_time"], df["rd_untrusted"])' in m)
ok("G13c HIST_SQL lay f.quarter", "f.quarter" in R.HIST_SQL)
ok("G13d bank_eff_date + attach_icb_pit truyen rd_untrusted",
   'r.get("rd_untrusted")' in src and 'left.get("rd_untrusted")' in src)

# ---- G14: du lieu that ----
_tf = os.environ.get("R8L_GUARD_TF_CSV", "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/"
                     "rating_8l_lag_20261020/raw/tf_current.csv")
if os.path.exists(_tf):
    tf = pd.read_csv(_tf)
    tf = tf[pd.to_datetime(tf["time"]) >= T("2014-06-01")].rename(columns={"time": "q_time"})
    tf = run(tf)
    fl = tf[tf["rd_untrusted"]]
    chg = fl[fl["eff"] != pd.to_datetime(fl["Release_Date"])]
    uni = chg[chg["in_univ_qend"].astype(str).str.lower() == "true"]
    ok("G14a du lieu that: 27 dong co", len(fl) == 27, f"n={len(fl)}")
    ok("G14b 22 dong doi eff (tat ca 2026)", len(chg) == 22 and chg["quarter"].str.startswith("2026").all(), f"n={len(chg)}")
    ok("G14c 7 dong doi trong universe = dung 7 ca chac chan",
       sorted(uni["ticker"] + uni["quarter"]) == sorted(t + q for t, _, q, _, _ in G1), f"{sorted(uni['ticker'] + uni['quarter'])}")
else:
    SKIP += 1; print(f"SKIP G14 — khong co {_tf}")

print(f"\n{PASS} PASS / {FAIL} FAIL / {SKIP} SKIP")
sys.exit(1 if FAIL else 0)
