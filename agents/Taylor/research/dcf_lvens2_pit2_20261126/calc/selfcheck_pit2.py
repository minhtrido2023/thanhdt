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
EXPECT_BLIND = {"universe"}   # universe chỉ ghép theo (mã, ngày phiên ≤ D) ⇒ dòng > D không bao giờ khớp panel (đã cắt giá ở D)


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


def main(ym, mc, out):
    os.makedirs(out, exist_ok=True); fr = L.FROZEN
    D = L.last_session(ym)
    L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_base")
    L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_poison", poison=make_poison(D))
    sfx = L.MC_TAG[mc]
    base = md5(f"{out}/lvens2_{ym}{sfx}_sc_base.parquet"); pois = md5(f"{out}/lvens2_{ym}{sfx}_sc_poison.parquet")
    rows = [("poison vs base", "PASS" if base == pois else "FAIL", base[:8], pois[:8])]
    for s in SOURCES:
        L.run([ym], "pit", out, fr, mc_pit=mc, tag="_sc_mut", poison=make_poison(D), nocut={s})
        m = md5(f"{out}/lvens2_{ym}{sfx}_nocut-{s}_sc_mut.parquet")
        st = "DETECTED" if m != base else ("BLIND(expected)" if s in EXPECT_BLIND else "BLIND(UNEXPECTED)")
        rows.append((f"mutate-nocut {s}", st, base[:8], m[:8]))
    print(f"\nSELFCHECK {ym} {mc} D={D.date()} TZ={os.environ.get('TZ', '<unset>')}")
    for r in rows:
        print(" | ".join(r))
    bad = [r for r in rows if r[1] in ("FAIL", "BLIND(UNEXPECTED)")]
    print("RESULT:", "PASS" if not bad else f"FAIL {len(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.path.join(L.HERE, "..", "out", "sc")))
