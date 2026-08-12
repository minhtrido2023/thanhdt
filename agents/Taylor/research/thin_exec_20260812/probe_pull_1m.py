"""Kéo bar 1 phút (vnstock/VCI) cho rổ mã THANH KHOẢN MỎNG + cache ra CSV.

R&D only (§8 coding_guidelines: namespace probe_*, không ghi vào tên canonical).
Chạy bằng /home/trido/thanhdt/wc_venv/bin/python.

Nguồn: vnstock 3.4.2, Quote(source='VCI').history(interval='1m').
GIỚI HẠN ĐÃ ĐO (không suy diễn): VCI KHÔNG có order-book depth lịch sử
(`Quote.price_depth()` → NotImplementedError) và `Quote.intraday()` chỉ trả tick
của PHIÊN HÔM NAY. Nên tất cả phân tích depth/fill dưới đây dựa trên KHỐI LƯỢNG
ĐÃ KHỚP theo phút, KHÔNG phải khối lượng chờ ở sổ lệnh.
"""
import os
import sys
import time
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "bars1m")
os.makedirs(OUT, exist_ok=True)

COHORT_CSV = os.path.join(HERE, "data", "cohort20.csv")
TARGET_N = int(os.environ.get("TARGET_N", "24"))


def pick_cohort():
    """Rổ = TV1 + mẫu ĐỀU theo hạng ADV trong dải 300–1500tr/phiên (quanh TV1 672tr).

    Lấy đều theo hạng (không random, không chọn tay) để khỏi cherry-pick mã dễ khớp.
    """
    df = pd.read_csv(COHORT_CSV)
    band = df[(df.adv20_mn >= 300) & (df.adv20_mn <= 1500)].sort_values("adv20_mn")
    band = band[band.ticker != "TV1"].reset_index(drop=True)
    step = max(1, len(band) // (TARGET_N - 1))
    sample = band.iloc[::step].head(TARGET_N - 1)
    out = ["TV1"] + sample.ticker.tolist()
    return out, df.set_index("ticker").adv20_mn.to_dict()


def main():
    from vnstock import Quote
    tickers, adv = pick_cohort()
    print(f"cohort n={len(tickers)}: {tickers}")
    meta = []
    for i, t in enumerate(tickers, 1):
        path = os.path.join(OUT, f"{t}.csv")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            print(f"[{i}/{len(tickers)}] {t} cached")
            continue
        for attempt in range(3):
            try:
                df = Quote(symbol=t, source="VCI").history(
                    start="2024-01-01", end="2026-08-12", interval="1m")
                if df is None or df.empty:
                    print(f"[{i}] {t} EMPTY")
                    break
                df.to_csv(path, index=False)
                meta.append({"ticker": t, "rows": len(df), "adv20_mn": adv.get(t)})
                print(f"[{i}/{len(tickers)}] {t} rows={len(df)} "
                      f"{df.time.min()}→{df.time.max()}")
                break
            except Exception as e:
                print(f"[{i}] {t} attempt{attempt} ERR {repr(e)[:120]}")
                time.sleep(5)
        time.sleep(1.5)
    if meta:
        pd.DataFrame(meta).to_csv(os.path.join(HERE, "data", "pull_meta.csv"),
                                  index=False)


if __name__ == "__main__":
    sys.exit(main())
