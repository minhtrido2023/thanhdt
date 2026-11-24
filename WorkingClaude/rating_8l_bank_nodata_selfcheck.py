#!/usr/bin/env python3
"""rating_8l_bank_nodata_selfcheck.py — selfcheck cho đổi mặc định LIVE bank-nodata 3 -> 4 (fail-closed)
trong rating_8l.py::rate_bank (user duyệt 2026-11-19, job Taylor_20261119_095521).

BẤT BIẾN:
  1. Mã BANK KHÔNG có trong bank_lens_v3 ⇒ (4, "bank-nodata") — nhãn giữ NGUYÊN chuỗi vì
     rating_8l_history.override_current_bank_aq khớp theo chuỗi đó.
  2. Mã BANK CÓ dữ liệu lens ⇒ KHÔNG đổi gì: so từng mã trong data/bank_lens_v3.csv thật với bản
     tham chiếu đóng băng của rate_bank ở HEAD trước khi sửa (chỉ khác nhánh nodata).
  3. "bank-noROE" giữ 3 (ngoài phạm vi duyệt lần này).
  4. Phía history (phương án B 2026-11-19): dòng live 4 + "bank-nodata" ⇒ dòng MỚI NHẤT của mã đó
     = max(proxy, 4) (chỉ hạ hạng), dòng cũ hơn giữ proxy, mã có lens vẫn nhận hạng live.
  5. Mutation: trả lại 3 cho nhánh nodata ⇒ test 1 PHẢI bắt được.

PHỤ THUỘC MÔI TRƯỜNG: TZ — không có (không gọi now()); vẫn chạy env -u TZ và TZ=Asia/Tokyo.
WORKDIR_8L — nơi có data/bank_lens_v3.csv; mặc định checkout canonical (worktree sparse không có data/).
Usage: python3 rating_8l_bank_nodata_selfcheck.py
"""
import os, sys, tempfile
os.environ.setdefault("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
WORKDIR = os.environ["WORKDIR_8L"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import rating_8l as R
import rating_8l_history as H

N_OK, FAILS = 0, []
def ok(cond, label, detail=""):
    global N_OK
    if cond: N_OK += 1
    else: FAILS.append(label + (f" -- {detail}" if detail else ""))


def ref_head(r, bankd):
    """rate_bank tại HEAD trước khi sửa (đóng băng để so) — nhánh nodata trả 3."""
    b = bankd.get(r["ticker"])
    if not b: return 3, "bank-nodata"
    roe, npl, cov = b.get("ROE"), b.get("NPL"), b.get("coverage")
    if pd.isna(roe): return 3, "bank-noROE"
    if roe < 0.08: return 5, "weak franchise (ROE<8%)"
    pristine = pd.notna(npl) and npl<=0.012 and pd.notna(cov) and cov>=1.5
    strong   = pd.notna(npl) and npl<=0.020 and pd.notna(cov) and cov>=0.9
    if roe>=0.15 and pristine: return 1, "elite asset-quality"
    if roe>=0.14 and strong:   return 2, "strong asset-quality"
    if roe>=0.12: return 3, "profitable (AQ-modulated)"
    return 4, "modest ROE"


def t1_nodata():
    saved = R.BANKD
    try:
        R.BANKD = {}
        ok(R.rate_bank({"ticker": "ZZZ"}) == (4, "bank-nodata"), "nodata (BANKD rỗng) -> (4,'bank-nodata')",
           str(R.rate_bank({"ticker": "ZZZ"})))
        R.BANKD = {"AAA": {"ROE": 0.16, "NPL": 0.01, "coverage": 1.6}}
        ok(R.rate_bank({"ticker": "ZZZ"}) == (4, "bank-nodata"), "mã vắng trong lens -> (4,'bank-nodata')")
        ok(R.rate_bank({"ticker": "ZZZ"})[0] > 3, "nodata KHÔNG lọt cổng <=3")
    finally:
        R.BANKD = saved


def t2_synthetic_unchanged():
    cases = {"E1": dict(ROE=0.16, NPL=0.010, coverage=1.6), "S2": dict(ROE=0.145, NPL=0.015, coverage=1.0),
             "P3": dict(ROE=0.13, NPL=0.04, coverage=0.5), "M4": dict(ROE=0.10, NPL=0.01, coverage=2.0),
             "W5": dict(ROE=0.05, NPL=0.01, coverage=2.0), "NR": dict(ROE=np.nan, NPL=0.01, coverage=2.0)}
    exp = {"E1": 1, "S2": 2, "P3": 3, "M4": 4, "W5": 5, "NR": 3}
    saved = R.BANKD
    try:
        R.BANKD = cases
        for tk, e in exp.items():
            got = R.rate_bank({"ticker": tk})
            ok(got[0] == e and got == ref_head({"ticker": tk}, cases), f"lens path {tk} -> {e} (không đổi)", str(got))
        ok(R.rate_bank({"ticker": "NR"}) == (3, "bank-noROE"), "bank-noROE giữ 3 (ngoài phạm vi)")
    finally:
        R.BANKD = saved


def t3_real_lens():
    lens = pd.read_csv(os.path.join(WORKDIR, "data", "bank_lens_v3.csv"))
    bankd = {row["ticker"]: row.to_dict() for _, row in lens.iterrows()}
    saved = R.BANKD
    try:
        R.BANKD = bankd
        diff = [tk for tk in bankd if R.rate_bank({"ticker": tk}) != ref_head({"ticker": tk}, bankd)]
        ok(not diff, f"{len(bankd)} mã bank CÓ lens thật: kết quả y hệt HEAD", str(diff))
        ok(all(R.rate_bank({"ticker": tk})[1] != "bank-nodata" for tk in bankd), "mã có lens không bao giờ nhận nhãn nodata")
    finally:
        R.BANKD = saved
    print(f"  [3] real bank_lens_v3.csv: {len(bankd)} mã, 0 khác HEAD = {not diff}")


def t4_history_still_rejects():
    hist = pd.DataFrame({"ticker": ["AAA", "AAA", "BBB"], "route": ["BANK"] * 3,
                         "eff_date": pd.to_datetime(["2026-05-01", "2026-08-01", "2026-08-01"]),
                         "rating": [2, 2, 1], "tier": ["B", "B", "A"]})
    live = pd.DataFrame({"ticker": ["AAA", "BBB"], "route": ["BANK", "BANK"], "rating": [4, 2],
                         "note": ["bank-nodata", "strong asset-quality"]})
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "data"))
        live.to_csv(os.path.join(tmp, "data", "rating_8l.csv"), index=False)
        # lens đọc được (BBB) ⇒ cổng chặn G1 không bật; snapshot vắng ⇒ G4 bỏ qua. 1/2 nodata = 50% > 45%
        # ⇒ thêm 3 mã lens giả để tỉ lệ = 1/5 (cổng G3 không bật)
        pd.DataFrame({"ticker": ["BBB", "C1", "C2", "C3"], "ROE": 0.15}).to_csv(
            os.path.join(tmp, "data", "bank_lens_v3.csv"), index=False)
        pd.concat([live, pd.DataFrame({"ticker": ["C1", "C2", "C3"], "route": "BANK", "rating": 3,
                                       "note": "profitable (AQ-modulated)"})]).to_csv(
            os.path.join(tmp, "data", "rating_8l.csv"), index=False)
        old, _sn = H.WORKDIR, os.environ.get("R8L_BANK_LENS_SNAPSHOT")
        os.environ["R8L_BANK_LENS_SNAPSHOT"] = os.path.join(tmp, "data", "no_snapshot.json")
        try:
            H.WORKDIR = tmp
            out = H.override_current_bank_aq(hist.copy())
        finally:
            H.WORKDIR = old
            if _sn is None: os.environ.pop("R8L_BANK_LENS_SNAPSHOT", None)
            else: os.environ["R8L_BANK_LENS_SNAPSHOT"] = _sn
    ok(list(out["rating"]) == [2, 4, 2],
       "history: dòng MỚI NHẤT AAA (proxy 2, live 4/bank-nodata) ⇒ 4; dòng cũ giữ 2; BBB có lens ⇒ 2",
       str(list(out["rating"])))


def t5_mutation():
    saved_fn, saved_d = R.rate_bank, R.BANKD
    n_before = len(FAILS)
    try:
        R.rate_bank = lambda r: ref_head(r, R.BANKD)   # revert về mặc định 3
        t1_nodata()
    finally:
        R.rate_bank, R.BANKD = saved_fn, saved_d
    caught = len(FAILS) - n_before
    del FAILS[n_before:]
    ok(caught >= 1, "MUTATION: revert nodata->3 BỊ test 1 bắt", f"caught={caught}")


if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '<unset>')}  WORKDIR_8L={WORKDIR}")
    t1_nodata(); t2_synthetic_unchanged(); t3_real_lens(); t4_history_still_rejects(); t5_mutation()
    for f in FAILS: print("FAIL:", f)
    print(f"{'PASS' if not FAILS else 'FAIL'}: {N_OK} ok, {len(FAILS)} fail")
    sys.exit(1 if FAILS else 0)
