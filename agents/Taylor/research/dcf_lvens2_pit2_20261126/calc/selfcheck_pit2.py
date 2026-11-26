# -*- coding: utf-8 -*-
"""selfcheck_pit2.py — kiểm PIT cho lvens2_pit2.py với poison TÁCH khỏi cut + mutation test.
1) baseline (không poison) vs poison (phá MỌI nguồn sau D, kể cả CA: sự kiện giả ex ≤ D nhưng public_date > D) ⇒ md5 parquet PHẢI trùng.
2) mutation: poison + bỏ cắt đúng 1 nguồn (--mutate-nocut) ⇒ md5 PHẢI khác (chứng minh phép thử nhìn thấy nguồn đó). Nguồn mà bỏ cắt cũng không đổi đầu ra
   ⇒ báo 'BLIND' (cấu trúc không dùng dòng > D của nguồn đó), không tính là lỗi nhưng phải khai.
Dùng: python selfcheck_pit2.py 2026-10 stepcar [out_dir]   → in bảng + rc 0 nếu (1) PASS và mọi mutation 'DETECTED' hoặc 'BLIND' đã khai trong EXPECT_BLIND."""
import os, sys, hashlib
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lvens2_pit2 as L  # noqa: E402

SOURCES = ["px", "vnd_px", "universe", "fin", "vnd_fs", "rating", "ca"]
EXPECT_BLIND = {"universe", "ca"}   # universe: chỉ ghép theo (mã, ngày phiên ≤ D) ⇒ dòng > D không bao giờ khớp panel.
# ca: ca_factor tự lọc ex ≤ ngày dòng và pub ≤ ngày dòng (lớp PIT thứ 2) ⇒ bỏ cắt ngoài không lộ; mutation 'ca+inner' phá CẢ lớp trong ⇒ PHẢI DETECTED.


def leaky_ca_factor(rows, ca, include_rights=False):
    """mutation: bỏ lọc pub ≤ ngày dòng (giữ ex ≤ ngày dòng) — như một lập trình viên quên public_date."""
    r = rows[["ticker", "known", "time"]].reset_index().rename(columns={"index": "_i"})
    e = ca if include_rights else ca[~ca.rights]
    m = r.merge(e, on="ticker", how="inner"); m = m[(m.ex > m.known) & (m.ex <= m.time)]
    g = m.groupby("_i").exercise_ratio.agg(lambda s: float(np.prod(1.0 + s.values))); n = m.groupby("_i").size()
    return (pd.Series(1.0, index=rows.index).where(~rows.index.isin(g.index), g.reindex(rows.index)).values, n.reindex(rows.index).fillna(0).astype(int).values)


def leaky_eg(orig):
    """mutation: e_guard không còn lọc public_date ≤ as-of (Dcut bị bỏ ⇒ giới hạn nới tới known+400 ngày)."""
    return lambda F, ca, Dcut=None, tol=0.06: orig(F, ca, Dcut=None, tol=tol)


def eguard_unit(fn):
    """1 mã ngân hàng, E tụt đúng 1/1,5 ở kỳ 2; sự kiện thưởng 50% CÔNG BỐ SAU D. Đúng PIT = không sửa, gắn cờ E_unexpl. Trả True nếu hành vi đúng."""
    D = pd.Timestamp("2026-03-31")
    t = pd.to_datetime(["2025-10-30", "2026-01-30"]).astype(L.NS)
    F = pd.DataFrame({"ticker": "XXX", "known": t, "E": [150.0, 100.0], "E_src": "BVPSxOS", "OShares": [10.0, 10.0]})
    ev = lambda pub: pd.DataFrame({"ticker": ["XXX"], "ex": [pd.Timestamp("2026-04-15")], "pub": [pd.Timestamp(pub)], "exercise_ratio": [0.5], "rights": [False]})
    E_late, fix_late, un_late = fn(F, ev("2026-04-05"), Dcut=D)      # pub > D
    E_ok, fix_ok, _ = fn(F, ev("2026-03-20"), Dcut=D)                # pub <= D ⇒ phải sửa (chứng minh ca test có răng)
    return bool(E_late[1] == 100.0 and not fix_late[1] and un_late[1] and fix_ok[1] and abs(E_ok[1] - 150.0) < 1e-9)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def make_poison(D):
    rng = np.random.RandomState(7)

    def poison(df, col, name):
        df = df.copy(); late = df[col] > D
        if name in ("px", "vnd_px", "pre"):
            for c in ("Close", "Price"):
                if c in df: df.loc[late, c] = df.loc[late, c] * 1.7
        elif name in ("fin", "vnd_fs"):
            num = [c for c in df.columns if c not in (col, "ticker", "quarter", "time", "known", "fq", "fiscalDate", "src", "E_src", "N_how") and pd.api.types.is_numeric_dtype(df[c])]
            df.loc[late, num] = df.loc[late, num] * 0.3
            if late.sum() == 0 and len(df):                    # chưa có dòng sau D ⇒ gài 1 bản sao mọi mã, ngày D+5
                x = df.groupby("ticker").tail(1).copy(); x[col] = D + pd.Timedelta(days=5); x[num] = x[num] * 0.3; df = pd.concat([df, x], ignore_index=True)
        elif name == "universe":
            x = df.drop_duplicates("ticker").copy(); x[col] = D + pd.Timedelta(days=3); df = pd.concat([df, x], ignore_index=True)
        elif name == "rating":
            df.loc[late, "route"] = rng.choice(["BANK", "POWER", "REALESTATE", "COMPOUNDER"], late.sum())
            x = df.drop_duplicates("ticker").copy(); x[col] = D + pd.Timedelta(days=2); x["route"] = rng.choice(["BANK", "POWER"], len(x)); df = pd.concat([df, x], ignore_index=True)
        elif name == "ca":
            df.loc[late, "exercise_ratio"] = df.loc[late, "exercise_ratio"] * 3
            tk = df.ticker.unique()
            x = pd.DataFrame({"ticker": tk, "ex": D - pd.Timedelta(days=10), "pub": D + pd.Timedelta(days=5), "exercise_ratio": 0.5, "rights": False})
            y = pd.DataFrame({"ticker": tk, "ex": D + pd.Timedelta(days=10), "pub": D - pd.Timedelta(days=5), "exercise_ratio": 0.5, "rights": False})
            df = pd.concat([df, x, y], ignore_index=True)
        return df
    return poison


def main(ym, mc, out, quick=False):
    os.makedirs(out, exist_ok=True); fr = L.FROZEN
    D = L.last_session(ym)
    if quick == "base":                                       # chỉ base (so md5 giữa TZ)
        L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_base"); print(f"BASE_MD5 TZ={os.environ.get('TZ', '<unset>')} {md5(f'{out}/lvens2_{ym}{L.MC_TAG[mc]}_sc_base.parquet')}"); return 0
    L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_base")
    L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_poison", poison=make_poison(D))
    sfx = L.MC_TAG[mc]
    base = md5(f"{out}/lvens2_{ym}{sfx}_sc_base.parquet"); pois = md5(f"{out}/lvens2_{ym}{sfx}_sc_poison.parquet")
    rows = [("poison vs base", "PASS" if base == pois else "FAIL", base[:8], pois[:8])]
    only = os.environ.get("SC_ONLY")                          # chạy lại 1 phần (vd SC_ONLY=inner: chỉ base + poison + ca+inner)
    for s in ([] if (quick or only) else SOURCES):
        L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_mut", poison=make_poison(D), nocut={s})
        m = md5(f"{out}/lvens2_{ym}{sfx}_nocut-{s}_sc_mut.parquet")
        st = "DETECTED" if m != base else ("BLIND(expected)" if s in EXPECT_BLIND else "BLIND(UNEXPECTED)")
        rows.append((f"mutate-nocut {s}", st, base[:8], m[:8]))
    print(f"\nSELFCHECK {ym} {mc} D={D.date()} TZ={os.environ.get('TZ', '<unset>')} quick={quick} md5_base={base}")
    for r in rows:
        print(" | ".join(r))
    orig = L.ca_factor; L.ca_factor = leaky_ca_factor
    try:
        L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_mutinner", poison=make_poison(D), nocut={"ca"})
    finally:
        L.ca_factor = orig
    m = md5(f"{out}/lvens2_{ym}{sfx}_nocut-ca_sc_mutinner.parquet")
    rows.append(("mutate-nocut ca+inner(pub)", "DETECTED" if m != base else "BLIND(UNEXPECTED)", base[:8], m[:8]))
    print(" | ".join(rows[-1]))
    # [v3] e_guard bỏ lọc public_date ≤ D: (a) phép thử đơn vị tổng hợp, không phụ thuộc tháng (PHẢI bắt được); (b) trên dữ liệu thật + poison (ghi nhận).
    u_ok, u_mut = eguard_unit(L.e_guard), eguard_unit(leaky_eg(L.e_guard))
    rows.append(("unit e_guard pub<=D", "PASS" if u_ok and not u_mut else "FAIL", f"real={u_ok}", f"mutant={u_mut}")); print(" | ".join(rows[-1]))
    orig_eg = L.e_guard; L.e_guard = leaky_eg(orig_eg)
    try:
        L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_egnopub")
        L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_egnopub_poison", poison=make_poison(D))
    finally:
        L.e_guard = orig_eg
    a_, b_ = md5(f"{out}/lvens2_{ym}{sfx}_sc_egnopub.parquet"), md5(f"{out}/lvens2_{ym}{sfx}_sc_egnopub_poison.parquet")
    rows.append(("mutate e_guard pub<=D (data)", "DETECTED" if a_ != base else ("DETECTED(poison)" if b_ != base else "BLIND(data)"), base[:8], f"{a_[:8]}/{b_[:8]}"))
    print(" | ".join(rows[-1]))
    bad = [r for r in rows if r[1] in ("FAIL", "BLIND(UNEXPECTED)")]
    print("RESULT:", "PASS" if not bad else f"FAIL {len(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.path.join(L.HERE, "..", "out", "sc"), quick=("base" if "base" in sys.argv[4:] else "quick" in sys.argv[4:])))
