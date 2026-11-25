# -*- coding: utf-8 -*-
"""cmp_cells.py — tính ô bốn-ô (đúng logic paper_cell_monthly) cho 2026-05..10 dưới: vp2 (V3.1, không PIT) · merged (lvens2_incremental PIT strict, bản đã merge)
· pit2 strict/step/stepca/stepcar. Liệt kê ô đổi nhãn của biến thể chọn (stepcar) so với merged và vp2, kèm thuộc tính để giải thích (E_fix, E_unexpl, ca_n, route, Δlv, khoảng cách tới trung vị).
Dùng: python cmp_cells.py OUT_JSON OUT_CSV"""
import sys, json
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
VP2 = f"{WC}/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c/out_F/vp2.parquet"
MERGED = f"{WC}/wt-dcf-lvens2-inc-20261125/agents/Taylor/research/dcf_lvens2_incremental_20261125/out/pit/lvens2_{{ym}}.parquet"
NEW = "out/final/lvens2_{ym}{sfx}.parquet"
YMS = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
CELL = {(1, 1): "RE_DUOC_THUA_NHAN", (1, 0): "RE_CHUA_THUA_NHAN", (0, 1): "DAT_CON_NEO", (0, 0): "DAT_DANG_NGUOI"}


def cells(pan, ud, f):
    d = ud[ud.in_universe].merge(f, on="ticker").merge(pan[["ticker", "route", "lv_ENS2"]], on="ticker").dropna(subset=["hi52", "lv_ENS2"]).copy()
    d["v_all"] = d.lv_ENS2.rank(pct=True); d["a"] = d.hi52.rank(pct=True); d["isb"] = d.route == "BANK"
    d["v_grp"] = d.groupby("isb").lv_ENS2.rank(pct=True); n = d.groupby("isb").ticker.transform("size"); d["v_grp"] = np.where(n >= 15, d.v_grp, d.v_all)
    d["cell"] = [CELL[(int(v >= 0.5), int(x >= 0.5))] for v, x in zip(d.v_grp, d.a)]
    return d.set_index("ticker")


def main(out_json, out_csv):
    import duckdb
    vp2 = pd.read_parquet(VP2, columns=["ticker", "ym", "route", "lv_ENS2"]); vp2["ym"] = vp2.ym.astype(str)
    px = duckdb.connect().execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
        WHERE Close > 0 AND CAST(time AS DATE) >= DATE '2025-03-01' AND CAST(time AS DATE) <= DATE '2026-10-31'""").df()
    px["time"] = pd.to_datetime(px.time); px = px.sort_values(["ticker", "time"]).reset_index(drop=True); g = px.groupby("ticker")
    px["hi52"] = np.log(px.Close) - np.log(g.Close.rolling(252, min_periods=120).max().reset_index(level=0, drop=True).sort_index().values)
    res = {}; rows = []
    for ym in YMS:
        D = px[px.time.dt.strftime("%Y-%m") == ym].time.max()
        u = pd.read_parquet(f"{WC}/data/bq_cache/universe_pit/{D.year}.parquet", columns=["time", "ticker", "in_universe"]); u["time"] = pd.to_datetime(u.time)
        ud = u[u.time == D]; f = px[px.time == D][["ticker", "hi52"]]
        C = {"vp2": cells(vp2[vp2.ym == ym], ud, f), "merged": cells(pd.read_parquet(MERGED.format(ym=ym)), ud, f)}
        newp = {}
        for v, sfx in (("strict", ""), ("step", "_mcstep"), ("stepca", "_mcstepca"), ("stepcar", "_mcstepcar")):
            newp[v] = pd.read_parquet(NEW.format(ym=ym, sfx=sfx)); C[v] = cells(newp[v], ud, f)
        r = {"n": {k: int(len(v)) for k, v in C.items()}}
        for ref in ("vp2", "merged", "strict", "step", "stepca"):
            com = C["stepcar"].index.intersection(C[ref].index)
            r[f"stepcar_vs_{ref}_changed"] = int((C["stepcar"].loc[com, "cell"] != C[ref].loc[com, "cell"]).sum())
        for ref in ("vp2",):
            for v in ("strict", "step", "stepca", "merged"):
                com = C[v].index.intersection(C[ref].index); r[f"{v}_vs_vp2_changed"] = int((C[v].loc[com, "cell"] != C[ref].loc[com, "cell"]).sum())
        res[ym] = r
        nb = newp["stepcar"].set_index("ticker"); mg = pd.read_parquet(MERGED.format(ym=ym)).set_index("ticker")
        for ref in ("merged", "vp2"):
            com = C["stepcar"].index.intersection(C[ref].index)
            ch = [t for t in com if C["stepcar"].at[t, "cell"] != C[ref].at[t, "cell"]]
            for t in ch:
                s, o = C["stepcar"].loc[t], C[ref].loc[t]
                why = []
                if bool(nb.at[t, "E_fix"]): why.append("E_fix(bank E sửa)")
                if bool(nb.at[t, "E_unexpl"]): why.append("E_unexpl")
                if int(nb.at[t, "ca_n"]) > 0: why.append(f"ca_step x{nb.at[t, 'ca_ratio']:.3f}")
                if s.route != o.route: why.append(f"route {o.route}->{s.route}")
                if ref == "vp2" and t in mg.index and bool(mg.at[t, "n_next_used"]): pass
                dv = s.v_grp - o.v_grp
                near = min(abs(s.v_grp - 0.5), abs(o.v_grp - 0.5)) < 0.05
                if not why: why.append("trôi hạng (lv đổi do mã khác/MULT/HEDf)" if not near else "sát trung vị (<0,05)")
                elif near: why.append("sát trung vị")
                rows.append({"ym": ym, "ref": ref, "ticker": t, "route": s.route, "cell_ref": o.cell, "cell_new": s.cell, "lv_ref": round(o.lv_ENS2, 4), "lv_new": round(s.lv_ENS2, 4),
                             "v_grp_ref": round(o.v_grp, 3), "v_grp_new": round(s.v_grp, 3), "dv": round(dv, 3), "why": "; ".join(why)})
    json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    for ym, r in res.items():
        print(ym, r)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
