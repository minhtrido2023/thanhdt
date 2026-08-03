#!/usr/bin/env python
"""BUOC B (§1.2, §2 ke hoach margin_kelly_full_cycle_plan_20260803.md)

Mo phong DUONG DI cua sleeve theo NGAY tren gia that (`p2/px_pit.parquet` -> event_paths_pit.csv),
chinh sach vay V(f) BAT BUOC (khong tuy nghi): moi su kien washout vay dung (f-1)x equity,
mua ro PIT equal-weight, giu 60 phien hoac den margin call.

Kiem margin call HANG NGAY:  E_t/A_t < maint  ->  cuong che ban tai close t+1 voi penalty.

GATE G-B (§5, dang ky TRUOC):
    tren path lich su thuc: 0 margin call tai f <= 1,5 (maint 35%, lai 14%, penalty 2%)
    bootstrap khoi: P(ruin) <= 1%.
    Rot tai f nao -> loai f do; moi f rot -> NO-GO.

RESEARCH-ONLY.
"""
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
TC = 0.00075
SEED = 20260803
B = 10_000
BLOCK_DAYS = 183
F_GRID = [1.0, 1.1, 1.2, 1.3, 1.5]          # §2 luoi f — KHONG test f>=1,8 (§2)

ev = pd.read_csv(HERE / "events_outcome_pit.csv", parse_dates=["event"])
ev = ev[(ev["skip"].fillna("") == "") & (ev["event"] >= "2014-01-01")].sort_values("event")
ev = ev.reset_index(drop=True)
assert len(ev) == 17
paths = pd.read_csv(HERE / "event_paths_pit.csv", parse_dates=["event", "time"])

# chan fractional-Kelly co tran (§2): f_k = min(1 + 0,25*(f*_oos - 1), 1,5), uoc luong CHI tu qua khu
ko = pd.read_csv(EXP / "kelly_oos.csv", parse_dates=["event"])
fk = ko.set_index("event")["f_full"]
ev["f_kelly"] = ev["event"].map(lambda d: min(1 + 0.25 * (fk.get(d, np.nan) - 1), 1.5)
                                if pd.notna(fk.get(d, np.nan)) else 1.0)
ev["f_kelly"] = ev["f_kelly"].clip(lower=1.0)


def block_ids(dates, gap=BLOCK_DAYS):
    ids, cur = [0], 0
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days >= gap:
            cur += 1
        ids.append(cur)
    return np.array(ids)


BLK = block_ids(list(ev["event"]))


def sim_event(evt, f, c, maint, penalty, ret_shift=0.0):
    """Tra ve (R = loi nhuan tren von tu co, called, ngay bi call, E/A thap nhat)."""
    p = paths[paths["event"] == evt].sort_values("t")
    nav = p["nav"].to_numpy(float)
    tt = p["time"].to_numpy()
    if ret_shift:                       # chan adversarial: keo ca duong xuong tuyen tinh theo thoi gian
        nav = nav * (1.0 + ret_shift * np.arange(len(nav)) / (len(nav) - 1))
    d = (tt - tt[0]) / np.timedelta64(1, "D")

    A = f * (1.0 - TC) * nav            # tai san (da tra phi mua)
    L = (f - 1.0) * (1.0 + c * d / 365.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(A > 0, (A - L) / A, -np.inf)
    ratio[0] = np.inf                   # ngay vao lenh khong kiem tra
    hit = np.where(ratio < maint)[0]

    if len(hit) == 0:
        R = A[-1] * (1.0 - TC) - L[-1] - 1.0
        return R, False, None, float(np.nanmin(ratio[1:]))
    k = min(int(hit[0]) + 1, len(nav) - 1)      # cuong che ban tai close ngay t+1
    R = A[k] * (1.0 - TC) * (1.0 - penalty) - L[k] - 1.0
    return max(R, -1.0), True, str(pd.Timestamp(tt[k]).date()), float(np.nanmin(ratio[1:]))


def run_grid(c, maint, penalty, ret_shift=0.0):
    out = []
    for f in F_GRID + ["kelly"]:
        Rs, calls, mins, dates = [], 0, [], []
        for _, e in ev.iterrows():
            ff = e["f_kelly"] if f == "kelly" else f
            R, called, dt, mn = sim_event(e["event"], ff, c, maint, penalty, ret_shift)
            Rs.append(R); mins.append(mn)
            if called:
                calls += 1; dates.append(f"{e['event'].date()}@{dt}")
        Rs = np.array(Rs)
        out.append(dict(f=f, n_call=calls, call_dates=";".join(dates),
                        min_EA=min(mins), g=float(np.mean(np.log1p(Rs))),
                        W=float(np.prod(1 + Rs)), mean_R=float(Rs.mean()),
                        worst_R=float(Rs.min()), R=Rs))
    return out


def boot_ruin(Rs, called_flags, blocks):
    """P(ruin) = P(co it nhat 1 margin call trong chuoi N draw) + P(terminal wealth < 0,5)."""
    rng = np.random.default_rng(SEED)
    n = len(Rs)
    uniq = np.unique(blocks)
    members = [np.where(blocks == b)[0] for b in uniq]
    lg = np.log1p(Rs)
    ruin = 0; halved = 0
    for _ in range(B):
        idx = []
        while len(idx) < n:
            idx.extend(members[rng.integers(0, len(members))])
        idx = np.array(idx[:n])
        if called_flags[idx].any():
            ruin += 1
        if lg[idx].sum() < np.log(0.5):
            halved += 1
    return ruin / B, halved / B


def main():
    lines = []; P = lines.append
    P("=" * 92)
    P("BUOC B — mo phong duong di sleeve theo NGAY, margin call kiem HANG NGAY")
    P("Ke hoach §1.2/§2 | GATE G-B §5 | ro `universe_pit`, N=17 su kien 2014+")
    P("=" * 92)
    P("Chinh sach V(f) BAT BUOC: moi su kien vay (f-1)x equity, mua ro EW, giu 60 phien")
    P("Bien the (i) — sleeve NAM IM giua cac su kien (thuan hieu ung compound cua chuoi cuoc)")
    P("")
    P("Chan fractional-Kelly co tran, f theo tung su kien (uoc luong chi tu qua khu):")
    kk = ev[["event", "f_kelly"]].copy()
    kk["event"] = kk["event"].dt.strftime("%Y-%m-%d")
    P("  " + ", ".join(f"{a}:{b:.2f}" for a, b in kk.itertuples(index=False)))
    P("")

    scen = [
        ("BASE  c=12,5% maint=30% pen=1%", 0.125, 0.30, 0.01, 0.0),
        ("ADV-G-B c=14% maint=35% pen=2%", 0.140, 0.35, 0.02, 0.0),
        ("ADV+shift duong -10% tuyen tinh", 0.140, 0.35, 0.02, -0.10),
        ("ADV+shift duong -20% tuyen tinh", 0.140, 0.35, 0.02, -0.20),
    ]

    gate_rows = None
    for name, c, mt, pen, sh in scen:
        res = run_grid(c, mt, pen, sh)
        if name.startswith("ADV-G-B"):
            gate_rows = res
        P("-" * 92)
        P(f"KICH BAN: {name}")
        P("-" * 92)
        P(f"{'f':>7}{'#call':>7}{'min E/A':>10}{'g (log)':>10}{'W_N':>9}"
          f"{'TB R':>9}{'R xau nhat':>12}   ngay bi call")
        for d in res:
            fl = f"{d['f']:.2f}" if d["f"] != "kelly" else "kelly"
            P(f"{fl:>7}{d['n_call']:>7}{d['min_EA']:>10.3f}{d['g']:>10.5f}"
              f"{d['W']:>9.2f}{d['mean_R']:>9.2%}{d['worst_R']:>12.2%}   {d['call_dates']}")
        P("")

    # ---------------------------------------------------------------- GATE G-B
    P("=" * 92)
    P("GATE G-B (§5) — kich ban dang ky: maint 35%, lai 14%/nam, penalty 2%")
    P("=" * 92)
    survivors = []
    for d in gate_rows:
        fl = f"{d['f']:.2f}" if d["f"] != "kelly" else "kelly"
        called_flags = np.zeros(len(ev), bool)   # tinh lai co called per-event
        Rs = []
        for i, (_, e) in enumerate(ev.iterrows()):
            ff = e["f_kelly"] if d["f"] == "kelly" else d["f"]
            R, cl, _, _ = sim_event(e["event"], ff, 0.140, 0.35, 0.02)
            Rs.append(R); called_flags[i] = cl
        p_ruin, p_half = boot_ruin(np.array(Rs), called_flags, BLK)
        ok_call = d["n_call"] == 0
        ok_ruin = p_ruin <= 0.01
        ok = ok_call and ok_ruin
        if ok:
            survivors.append(d["f"])
        P(f"  f={fl:>5}: #call lich su = {d['n_call']} ({'PASS' if ok_call else 'FAIL'})  |  "
          f"P(ruin) boot-khoi = {p_ruin:.4f} ({'PASS' if ok_ruin else 'FAIL'})  |  "
          f"P(W<0,5) = {p_half:.4f}  ->  {'GIU' if ok else 'LOAI'}")
    P("")
    P(f"  f song sot qua G-B: {survivors}")
    verdict = "PASS" if survivors else "FAIL -> NO-GO"
    P(f"  >>> GATE G-B: {verdict}")
    P("")
    P("  LUU Y TRUNG THUC (bat buoc doc kem): P(ruin)=0 o day la ket qua TAM THUONG —")
    P("  0 su kien lich su nao cham nguong call, nen bootstrap tu chinh 17 su kien do")
    P("  KHONG THE sinh ra call. Day la bang chung YEU ('chua tung xay ra trong 17 lan'),")
    P("  KHONG phai bang chung manh ('khong the xay ra'). Chan shift -10%/-20% o tren la")
    P("  phep do co suc phan bac thuc su; doc no truoc khi ket luan.")

    txt = "\n".join(lines)
    print(txt)
    (HERE / "step_b_sleeve.log").write_text(txt + "\n", encoding="utf-8")
    return survivors


if __name__ == "__main__":
    main()
