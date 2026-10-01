"""AlphaLens paper — audit cuối cửa sổ (job Taylor_20261001_004002).

Tái lập 3 thứ từ tav2_bq.ticker (+ ticker_financial cho PE_MA1Y point-in-time):
  Gate 1  excess EW 4 tên vs VNINDEX, 06-30 close → 09-30 close (+ biến thể vào lệnh 07-01 open/close
          vì quyết định chốt 22:15 ICT 06-30, sau phiên — 06-30 close KHÔNG giao dịch được).
  Gate 2  exit condition hằng ngày: FPT PE > PE_MA1Y (PIT theo Release_Date), ngân hàng PB > (ROE5Y-0.05)/0.08.
  Control EW top-30 cổ phiếu theo ADV 06-30 + EW ngân hàng thanh khoản (không gồm ACB/MBB/HDB).

Giá vào control = Price_0630 × r_min, r_min = min(Close/Price) trên [06-30, 09-30]. Close/Price là tích hệ số
của các sự kiện CÒN Ở TƯƠNG LAI nên KHÔNG được giảm theo ngày; vendor hồi tố thiếu (ca VPB vintage này:
hệ số 0,7934 chỉ áp 09-18..09-23) làm r tại 06-30 quá cao ⇒ dùng r_min chữa. Return lệch >|40%| bị loại (PNJ).
Quy ước rights cho 4 tên = `terp` (giá Close đã hồi tố = thực hiện quyền); accrue-only lấy từ probe báo cáo.

Chạy: $DNA_PYEXE audit_alphalens.py   (cần `source wc_env.sh` cho bq)
"""
import io
import subprocess

import pandas as pd

PROJ = "lithe-record-440915-m9"
NAMES = ["FPT", "ACB", "MBB", "HDB"]
BANKS_ICB = 8355.0
D0, D_IN, D1 = "2026-06-30", "2026-07-01", "2026-09-30"
PE_MA1Y = [("2000-01-01", 18.692344505530468), ("2026-07-28", 16.33088984077529)]  # ticker_financial FPT, Release_Date


def bq(sql):
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJ}", "--format=csv",
                          "--max_rows=100000", sql], check=True, capture_output=True, text=True).stdout
    return pd.read_csv(io.StringIO(out))


def main():
    inl = ",".join(f'"{t}"' for t in NAMES)
    d = bq(f"""SELECT t.time, t.ticker, t.Open, t.Price, t.Close, t.PE, t.PB, t.ROE5Y, t.VNINDEX
               FROM tav2_bq.ticker AS t WHERE t.ticker IN ({inl}) AND t.time BETWEEN "{D0}" AND "{D1}" """)
    d["time"] = pd.to_datetime(d.time)
    d.to_csv("alphalens_bq.csv", index=False)
    vn = d.drop_duplicates("time").set_index("time").VNINDEX.sort_index()
    vni = bq(f"""SELECT t.time, t.Open, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX"
                 AND t.time IN ("{D_IN}")""").iloc[0]

    print("== Gate 1 (terp, Close hồi tố vintage hiện tại) ==")
    for label, px0, b0 in [("06-30 close", "c0630", vn.loc[D0]), ("07-01 open", "o0701", vni.Open),
                           ("07-01 close", "c0701", vni.Close)]:
        rets = {}
        for t, g in d.groupby("ticker"):
            g = g.set_index("time").sort_index()
            # `Open` trong BQ đã hồi tố cùng hệ số với `Close` — KHÔNG nhân thêm Close/Price (sửa hai lần)
            p = {"c0630": g.loc[D0, "Close"], "c0701": g.loc[D_IN, "Close"], "o0701": g.loc[D_IN, "Open"]}[px0]
            rets[t] = g.loc[D1, "Close"] / p - 1
        ew = sum(rets.values()) / len(rets)
        b = vn.loc[D1] / b0 - 1
        loo = {t: (ew * 4 - r) / 3 - b for t, r in rets.items()}
        print(f"  vào {label}: " + " ".join(f"{t} {r:+.2%}" for t, r in rets.items())
              + f" | EW {ew:+.2%} vs VNINDEX {b:+.2%} ⇒ excess {(ew - b) * 100:+.2f}pp"
              + " | LOO " + " ".join(f"-{t} {v * 100:+.2f}" for t, v in loo.items()))

    print("== Gate 2 (exit condition hằng ngày 07-01..09-30) ==")
    w = d[d.time >= D_IN]
    for t, g in w.groupby("ticker"):
        if t == "FPT":
            th = g.time.map(lambda x: [v for s, v in PE_MA1Y if x >= pd.Timestamp(s)][-1])
            r = g.PE / th
        else:
            r = g.PB / ((g.ROE5Y - 0.05) / 0.08)
        print(f"  {t}: n={len(g)} max ratio {r.max():.3f} violations {(r > 1).sum()}")

    print("== Control ==")
    c = bq(f"""
      WITH a AS (SELECT t.ticker, t.Price p0, t.Price*t.Volume_1M adv, t.ICB_Code icb FROM tav2_bq.ticker AS t
                 WHERE t.time="{D0}" AND t.ICB_Code IS NOT NULL),
           r AS (SELECT t.ticker, MIN(SAFE_DIVIDE(t.Close, t.Price)) rmin FROM tav2_bq.ticker AS t
                 WHERE t.time BETWEEN "{D0}" AND "{D1}" GROUP BY t.ticker),
           b AS (SELECT t.ticker, t.Close c1 FROM tav2_bq.ticker AS t WHERE t.time="{D1}")
      SELECT a.ticker, a.icb, a.adv, b.c1/(a.p0*r.rmin)-1 AS r FROM a JOIN r USING(ticker) JOIN b USING(ticker)
      WHERE a.adv IS NOT NULL ORDER BY a.adv DESC LIMIT 60""")
    bad = c[c.r.abs() > 0.40]
    c = c[c.r.abs() <= 0.40]
    c.to_csv("al_ctrl.csv", index=False)
    top = c.head(30)
    bk = c[(c.icb == BANKS_ICB) & ~c.ticker.isin(NAMES)]
    print(f"  loại |r|>40%: {bad.ticker.tolist()}")
    print(f"  EW top-30 ADV: {top.r.mean():+.2%} | EW ngân hàng ngoài 3 tên (n={len(bk)}): {bk.r.mean():+.2%}")
    print("  VPB:", c.loc[c.ticker == "VPB", "r"].round(4).tolist())


if __name__ == "__main__":
    main()
