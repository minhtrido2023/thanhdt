"""Ước lượng số sự kiện G1/G2 nếu dựng 8L 2010Q1-2014Q2: tỉ lệ sự kiện/(mã universe·quý) đo trên nửa IS
2014-19 của P2v2 (sự kiện sau loại, có ô khớp SUE như bản chính) x số mã universe/quý 2010-2014 (q4 csv).
Đây là ƯỚC LƯỢNG TỈ LỆ (giả định tỉ lệ đổi hạng 2010-14 = 2014-19), không phải đếm."""
import pandas as pd
ev = pd.read_csv("../rating_8l_lag_p2v2_20261020/out_v2_events.csv")
u = pd.read_csv("q4_universe_by_quarter.csv"); u["q"] = pd.to_datetime(u["q"])
ev["eff"] = pd.to_datetime(ev["eff"])
main = ev[(~ev["excl"]) & ev["sue"].notna() & ev["cl"].notna()] if "cl" in ev else ev
for g in ["G1", "G2"]:
    gi = main[(main.grp == g) & (main.era == "IS")]
    nq = gi["cl"].nunique()
    is_u = u[(u.q >= "2014-07-01") & (u.q < "2020-01-01")]
    rate = len(gi) / is_u.n_univ.sum()
    new_u = u[(u.q >= "2010-04-01") & (u.q < "2014-07-01")]   # 2010Q1 = quý rating đầu, chưa có "prev"
    print(f"{g}: IS N={len(gi)} trên {nq} quý-lịch; mã·quý universe IS={is_u.n_univ.sum()} ⇒ rate={rate:.4f}; "
          f"2010Q2-2014Q2: {len(new_u)} quý, mã·quý={new_u.n_univ.sum()} ⇒ N_ước_lượng={rate*new_u.n_univ.sum():.0f}")
