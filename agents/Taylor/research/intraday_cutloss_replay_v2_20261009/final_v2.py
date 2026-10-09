#!/usr/bin/env python3
"""final_v2.py — mọi bảng của REPORT v2 → out/final_v2.txt + CSV. Chạy sau run_stage1.sh + run_stage2.sh."""
import io
import os
import sys
from contextlib import redirect_stdout

sys.argv = ["x"]
from analyze_v2 import A1, flags, load_cfg, np, pd, summ, verdict, HERE  # noqa: E402

pd.set_option("display.width", 220)
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
H = (1, 5, 20)


def ok(ex):
    return ex[~ex.glitch & (ex.sold > 0)] if len(ex) else ex


def row(s, h):
    r = s[s.h == h] if len(s) else s
    return (f"{r['mean%'].iloc[0]:+.2f} [{r['ci_lo%'].iloc[0]:+.2f}; {r['ci_hi%'].iloc[0]:+.2f}]"
            if len(r) else "—")


def line(name, sc):
    s = summ(sc)
    n = f"{len(sc)}/{sc.day.nunique()}" if len(sc) else "0/0"
    return {"nhóm": name, "N ca/ngày": n, **{f"T+{h}": row(s, h) for h in H},
            "bán oan T+5 %": round(sc.oan5.mean() * 100) if len(sc) else None}


def classify(old_tr, new_tr, new_mw, new_rel, new_cases):
    """Ca RIÊNG của code cũ (mã đang giữ) → số phận dưới code mới."""
    nt = {(r.day, r.ticker) for r in new_tr.itertuples() if r.held}
    mwr = {}
    for r in new_mw.itertuples():
        mwr.setdefault((r.day, r.ticker), (r.reason, r.not_individual))
    rl = {(r.day, r.ticker) for r in new_rel.itertuples()}
    hold = {(t0[:10], tk) for (t0, tk), c in new_cases.items() if (c.get("hold_override") or "").startswith("hoãn")}
    out = []
    for r in old_tr[old_tr.held].itertuples():
        k = (r.day, r.ticker)
        if k in rl:
            f = "(A) ca riêng → gắn nhãn gộp sau"
        elif k in nt:
            f = "(C) ca hoãn → GIỮ" if k in hold else "vẫn ca riêng"
        elif k in mwr:
            reason, ni = mwr[k]
            ni = ni if isinstance(ni, str) else None
            if ni and "VNINDEX" in ni:
                f = "(B) chạm sàn ∧ VNI≤−2% → gộp"
            elif ni:
                f = "(B) chạm sàn, idio chưa đạt → gộp"
            elif "luỹ kế" in reason:
                f = "(A) gộp theo cửa sổ 60'"
            else:
                f = "(A) hệ quả: gộp trong 1 lượt"
        else:
            f = "không kích hoạt lại (khác)"
        out.append({"day": r.day, "ticker": r.ticker, "fate": f})
    return pd.DataFrame(out)


def policy_compare(ex_old, ex_new, fate):
    """B_k (% giá trị vị thế theo TC; dương = cutloss hơn giữ) trên tập ca riêng của code CŨ; ca code mới không
    bán = 0. CI bootstrap cụm ngày."""
    key = ["day", "ticker"]
    o = ex_old[~ex_old.glitch].groupby(key)[[f"B{h}" for h in H]].sum().reset_index()
    n = ex_new[~ex_new.glitch].groupby(key)[[f"B{h}" for h in H]].sum().reset_index() if len(ex_new) else \
        pd.DataFrame(columns=key + [f"B{h}" for h in H])
    m = fate.merge(o, on=key, how="inner").merge(n, on=key, how="left", suffixes=("_old", "_new")).fillna(0)
    rows = []
    for g, x in [("TẤT CẢ", m)] + list(m.groupby("fate")):
        r = {"số phận": g, "N ca/ngày": f"{len(x)}/{x.day.nunique()}"}
        for h in H:
            for side in ("old", "new"):
                c = f"B{h}_{side}"
                lo, hi = A1.boot_ci(x, c)
                r[f"T+{h} {side}"] = f"{x[c].mean()*100:+.2f} [{lo*100:+.2f}; {hi*100:+.2f}]"
        rows.append(r)
    return pd.DataFrame(rows), m


def main():
    buf = io.StringIO()
    with redirect_stdout(buf):
        cfg = {}
        for name, pat in [("v2_new", "v2_new_BROKEN_d0.5_t3_s*"), ("v2_old", "v2_old_BROKEN_d0.5_t3_s*"),
                          ("v1_new", "v1_new_BROKEN_d0.5_t3_s*"), ("v1_old", "v1_old_BROKEN_d0.5_t3_s*"),
                          ("v2_new_UNCLEAR", "v2_new_UNCLEAR_d0.5_t3_c*")] + \
                         [(f"v2_new_d{d}_t{t}", f"v2_new_BROKEN_d{d}_t{t}_c*")
                          for d, t in (("0.25", 1), ("0.25", 3), ("0.5", 1), ("1", 1), ("1", 3))]:
            ex, tr, mw, rel, cases = load_cfg(pat)
            cfg[name] = (flags(ex, tr), tr, mw, rel, cases)
            cfg[name][0].to_csv(os.path.join(OUT, f"{name}_exec.csv"), index=False)

        print("=" * 30, "H1 (PREREG) — code mới, universe v2, BROKEN, ADV20 ≥ 10 tỷ, bỏ ca lỗi dữ liệu")
        ex = cfg["v2_new"][0]
        h1 = ok(ex)[ok(ex).adv_bucket == ">=10 tỷ"]
        s = summ(h1)
        print(s.round(2).to_string(index=False))
        v = verdict(s[s.h == 5])
        print("VERDICT cấu hình gốc:", v)
        print("\nĐộ bền (dấu mean E5, ADV≥10 tỷ) qua 6 cấu hình sổ lệnh (d = × KL/phút, t = số bước giá):")
        signs = []
        for name in ("v2_new_d0.25_t1", "v2_new_d0.25_t3", "v2_new_d0.5_t1", "v2_new", "v2_new_d1_t1", "v2_new_d1_t3"):
            e = ok(cfg[name][0])
            e = e[e.adv_bucket == ">=10 tỷ"]
            ss = summ(e)
            r5 = ss[ss.h == 5]
            signs.append(np.sign(r5["mean%"].iloc[0]) if len(r5) else 0)
            r5 = r5 if len(r5) else None
            print(f"  {name:18s} N={len(e)}/{e.day.nunique()}  T+1 {row(ss,1)}  T+5 {row(ss,5)}  T+20 {row(ss,20)}"
                  f"  → {verdict(r5)}")
        halves = [summ(g)[lambda d: d.h == 5]["mean%"].iloc[0] for _, g in h1.groupby("half")]
        print("  2 nửa thời gian T+5:", [round(x, 2) for x in halves])
        robust = len(set(signs)) == 1 and all(np.sign(x) == signs[0] for x in halves)
        print("  ⇒ dấu nhất quán:", robust, "| VERDICT CUỐI:",
              v if robust else f"{v} → hạ 1 bậc (đổi dấu)")

        for name in ("v2_new", "v1_old", "v1_new"):
            e = cfg[name][0]
            print("\n" + "=" * 30, f"{name}: theo ADV20 và giá (<5.000đ), bỏ ca lỗi dữ liệu")
            rows = [line("TẤT CẢ (giữ ca lỗi)", e[e.sold > 0]), line("TẤT CẢ (bỏ ca lỗi)", ok(e))]
            rows += [line(f"ADV {b}", ok(e)[ok(e).adv_bucket == b]) for b in ("<1 tỷ", "1-10 tỷ", ">=10 tỷ")]
            rows += [line("giá < 5.000đ", ok(e)[ok(e).px_lt5k]), line("giá ≥ 5.000đ", ok(e)[~ok(e).px_lt5k])]
            rows += [line(f"book {b}", ok(e)[ok(e).book == b]) for b in sorted(ok(e).book.dropna().unique())]
            print(pd.DataFrame(rows).to_string(index=False))
            print(f"  ca lỗi dữ liệu bị loại: P1==TC {int(e.g_p1_eq_ref.sum())}, Vol=0 {int(e.g_vol0.sum())}, "
                  f"quote cũ >60' {int(e.g_stale.sum())} (tổng {int(e.glitch.sum())} / {len(e)})")

        e = ok(cfg["v2_new"][0])
        print("\nBán ngay tại T0 (lý tưởng), v2_new ADV≥10 tỷ:")
        print(summ(e[e.adv_bucket == ">=10 tỷ"], "Eideal").round(2).to_string(index=False))
        u = cfg["v2_new_UNCLEAR"][0]
        u = u[~u.glitch]
        print("\nUNCLEAR (bán 50% book V2.4), v2_new — B_k trên TOÀN vị thế, ADV≥10 tỷ:")
        uu = u[u.adv_bucket == ">=10 tỷ"]
        for h in H:
            lo, hi = A1.boot_ci(uu, f"B{h}")
            print(f"  T+{h}: {uu[f'B{h}'].mean()*100:+.2f} [{lo*100:+.2f}; {hi*100:+.2f}]  N={len(uu)}/{uu.day.nunique()}")

        for uni in ("v2", "v1"):
            exo, tro, _, _, _ = cfg[f"{uni}_old"]
            exn, trn, mwn, reln, casen = cfg[f"{uni}_new"]
            fate = classify(tro, trn, mwn, reln, casen)
            fate.to_csv(os.path.join(OUT, f"fate_{uni}.csv"), index=False)
            print("\n" + "=" * 30, f"LUẬT MỚI vs CŨ — universe {uni}: ca RIÊNG (mã đang giữ) của code cũ → code mới")
            print(fate.fate.value_counts().to_string())
            print(f"  code cũ: {len(tro[tro.held])} ca riêng / {tro[tro.held].day.nunique()} ngày; code mới: "
                  f"{len(trn[trn.held])} ca riêng; mới gắn nhãn {len(reln)}; MARKET_WIDE mã mới {len(mwn)}")
            pc, m = policy_compare(exo, exn, fate)
            m.to_csv(os.path.join(OUT, f"policy_{uni}.csv"), index=False)
            print("  B_k chính sách (% giá trị vị thế, dương = cutloss hơn giữ; ca code mới không bán = 0), BROKEN:")
            print(pc.to_string(index=False))
            for name, e in (("cũ", exo), ("mới", exn)):
                e2 = ok(e)
                print(f"  E (ca có bán, bỏ lỗi) code {name}: N={len(e2)}/{e2.day.nunique() if len(e2) else 0} "
                      + "  ".join(f"T+{h} {row(summ(e2), h)}" for h in H))
        print("\n" + "=" * 30, "Độ nhạy sổ lệnh trên mã giá < 5.000đ và ADV < 1 tỷ (universe v1, code mới, BROKEN)")
        for d, t in (("0.25", 1), ("0.25", 3), ("0.5", 1), ("0.5", 3), ("1", 1), ("1", 3)):
            pat = "v1_new_BROKEN_d0.5_t3_s*" if (d, t) == ("0.5", 3) else f"v1_new_BROKEN_d{d}_t{t}_s*"
            ex, tr, *_ = load_cfg(pat)
            e = ok(flags(ex, tr))
            for lab, g in (("giá<5k", e[e.px_lt5k]), ("ADV<1 tỷ", e[e.adv_bucket == "<1 tỷ"]),
                           ("ADV>=10 tỷ", e[e.adv_bucket == ">=10 tỷ"])):
                ss = summ(g)
                print(f"  d{d} t{t} {lab:10s} N={len(g)}/{g.day.nunique() if len(g) else 0} fill TB "
                      f"{g.fill.mean()*100 if len(g) else float('nan'):.0f}%  T+1 {row(ss,1)}  T+5 {row(ss,5)}")

        print("\n" + "=" * 30, "Tự kiểm: tính lại H1 độc lập từ out/v2_new_exec.csv (không qua summarize)")
        x = pd.read_csv(os.path.join(OUT, "v2_new_exec.csv"))
        x = x[(~x.glitch) & (x.sold > 0) & (x.adv20 >= 1e10)]
        e5 = x.avg * (1 - 2 * 0.00097 - x.impact) / x.P5 - 1
        print(f"  N={len(x)} ngày={x.day.nunique()} mean E5={e5.mean()*100:+.4f}% (khớp bảng H1 nếu = mean% h=5)")
    txt = buf.getvalue()
    open(os.path.join(OUT, "final_v2.txt"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
