"""8L rating — kiem tra do nhay voi 1 ma von hoa cuc lon (kieu VIC).

Cau hoi (dispatch Taylor_20260802_014330, Viec 2): phat hien "meo do 1 ma von hoa lon"
o tang CHI SO (Phu luc B/C: PB/PE cap-weighted bi VIC boi meo) co lay sang tang
CHON CO PHIEU (8L rating) khong?

Thiet ke: leave-one-out THUC SU tren chinh pipeline production `rating_8l.main()`.
- Chay A = universe day du (baseline)
- Chay B = bo VIC khoi universe TU DAU (truoc moi buoc tinh)
- Chay C = bo top-5 von hoa
So sanh `rating` (cong gate <=3) va `zone`/`value_score` (truc value co buoc percentile
cross-sectional) tren tap ticker CHUNG.

An toan: WORKDIR_8L tro vao thu muc probe nay => KHONG ghi de bat ky file canonical nao
(data/rating_8l.csv, rating_8l_screener.csv... cua production khong bi dung toi).
"""
import os, sys, shutil, pickle

PROBE = os.path.dirname(os.path.abspath(__file__))
os.environ["WORKDIR_8L"] = PROBE          # phai set TRUOC khi import rating_8l (doc luc import)
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

import pandas as pd
import rating_8l as R

CACHE = os.path.join(PROBE, "bq_cache.pkl")


def fetch_once():
    """Lay MAIN_SQL + FIN_SQL 1 lan roi cache => 3 lan chay dung Y HET dau vao
    (khac biet duy nhat giua cac lan chay la tap ticker bi bo)."""
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    d = {"MAIN": R.bq(R.MAIN_SQL), "FIN": R.bq(R.FIN_SQL)}
    with open(CACHE, "wb") as f:
        pickle.dump(d, f)
    return d


def run(tag, drop):
    """Chay lai main() voi universe da bo `drop`; tra ve (rating_df, screener_df)."""
    cache = fetch_once()

    def fake_bq(sql):
        df = cache["MAIN"].copy() if "ticker_1m" in sql else cache["FIN"].copy()
        return df[~df["ticker"].isin(drop)].reset_index(drop=True)

    R.bq = fake_bq
    R.main()
    out = pd.read_csv(os.path.join(PROBE, "data", "rating_8l.csv"))
    scr = pd.read_csv(os.path.join(PROBE, "data", "rating_8l_screener.csv"), index_col=0)
    for src, dst in (("rating_8l.csv", f"run_{tag}_rating.csv"),
                     ("rating_8l_screener.csv", f"run_{tag}_screener.csv")):
        shutil.copy(os.path.join(PROBE, "data", src), os.path.join(PROBE, dst))
    return out, scr


if __name__ == "__main__":
    cache = fetch_once()
    m = cache["MAIN"].copy()
    m["mktcap_bn"] = m["Close"] * m["OShares"] / 1e9
    top = m.dropna(subset=["mktcap_bn"]).nlargest(8, "mktcap_bn")[["ticker", "mktcap_bn"]]
    print("\n=== TOP 8 VON HOA (Close x OShares, ty VND) ===")
    print(top.to_string(index=False))
    top5 = list(top["ticker"].head(5))

    import io, contextlib
    runs = {}
    for tag, drop in (("A_full", set()), ("B_noVIC", {"VIC"}), ("C_noTop5", set(top5))):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            runs[tag] = run(tag, drop)
        with open(os.path.join(PROBE, f"log_{tag}.txt"), "w") as f:
            f.write(buf.getvalue())
        print(f"[run {tag}] drop={sorted(drop) or 'none'} -> {len(runs[tag][0])} ma rated, "
              f"{len(runs[tag][1])} ma vao screener")

    A_r, A_s = runs["A_full"]
    print("\n=== KET QUA LEAVE-ONE-OUT ===")
    for tag in ("B_noVIC", "C_noTop5"):
        X_r, X_s = runs[tag]
        common = sorted(set(A_r.ticker) & set(X_r.ticker))
        a = A_r.set_index("ticker").loc[common]
        x = X_r.set_index("ticker").loc[common]
        d_rating = (a["rating"] != x["rating"]).sum()
        print(f"\n--- {tag} (N chung = {len(common)}) ---")
        print(f"  rating (cong gate <=3) doi: {d_rating} ma")
        if d_rating:
            ch = pd.DataFrame({"A": a["rating"], tag: x["rating"]})
            print(ch[ch["A"] != ch[tag]].to_string())
        n_gate_a = int((a["rating"] <= 3).sum()); n_gate_x = int((x["rating"] <= 3).sum())
        print(f"  so ma qua gate<=3: A={n_gate_a} vs {tag}={n_gate_x}")

        cs = sorted(set(A_s.ticker) & set(X_s.ticker))
        as_ = A_s.set_index("ticker").loc[cs]
        xs_ = X_s.set_index("ticker").loc[cs]
        print(f"  screener N chung = {len(cs)}")
        for col in ("ey_pct", "cfy_pct", "ps_pct", "value_score_v3"):
            diff = (as_[col] - xs_[col]).abs()
            print(f"    |delta {col:15}| max={diff.max():.4f}  mean={diff.mean():.5f}  "
                  f"so ma doi >0.01: {(diff > 0.01).sum()}")
        d_zone = (as_["zone"] != xs_["zone"]).sum()
        print(f"  zone (BUY-NOW/ACC/WATCH) doi: {d_zone} ma")
        if d_zone:
            zz = pd.DataFrame({"A": as_["zone"], tag: xs_["zone"],
                               "vs_A": as_["value_score_v3"], "vs_X": xs_["value_score_v3"]})
            print(zz[zz["A"] != zz[tag]].to_string())
