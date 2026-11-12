#!/usr/bin/env python3
"""Luồng D2(a) (job Taylor_20261112_151837): dựng lại dt5g_cand_clock THEO NGÀY từ logic clock THẬT.
Nguồn logic: dna_report.get_dt_gate_clock() = replay DT 4-gate (macro_state_live._dt_4gate qua
dt_gate_hazard_research.extract_episodes) trên chuỗi BASE v3.4b (vnindex_5state_tam_quan_v34b_clean, warm-up 2014).
Clock tại phiên t = độ dài streak candidate đang tích luỹ (k), need (10/25), progress=k/need; k=0 khi không có candidate.
Cách tính per-day = đúng vòng lặp extract_episodes (pr đếm phiên liên tiếp base==ps≠committed); commit khi pr>=need ⇒ k về 0.
GĐ2B dựng SAI: đếm phiên liên tiếp dt5g_live.state_raw≠state (đó là macro-cap, không phải candidate clock).
PIT: panel lấy giá trị tại sig_date = phiên TRƯỚC first_fill (fill T+1 Open) ⇒ chỉ dùng dữ liệu tới đóng cửa phiên < ngày vào lệnh.
Self-check: (1) committed per-day == _dt_4gate(raw); (2) k cuối mỗi episode == extract_episodes.length;
(3) chạy cùng hàm trên chuỗi base BQ tươi, so phiên cuối với get_dt_gate_clock()."""
import sys, os, json
import numpy as np, pandas as pd
W = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W); sys.path.insert(0, W + "/mike/agents/Taylor")
from dt_gate_hazard_research import extract_episodes, need_for, dt_4gate

def daily_clock(times, raw):
    raw = np.asarray(raw).astype(int); n = len(raw)
    committed = raw[0]; ps, pr = raw[0], 1
    K = np.zeros(n, int); NEED = np.zeros(n, int); CAND = np.zeros(n, int); COM = np.zeros(n, int); COM[0] = committed
    for t in range(1, n):
        s = raw[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps != committed:
            need = need_for(ps, committed)
            if pr >= need:
                committed = ps                       # commit hôm nay ⇒ không còn candidate
            else:
                K[t], NEED[t], CAND[t] = pr, need, ps
        COM[t] = committed
    return pd.DataFrame({"time": pd.to_datetime(times), "base": raw, "committed": COM, "cand": CAND, "k": K, "need": NEED,
                         "progress": np.where(NEED > 0, K / np.maximum(NEED, 1), 0.0), "active": (K > 0).astype(int)})

def main():
    b = pd.read_parquet(W + "/data/bq_cache/vnindex_5state_tam_quan_v34b_clean.parquet"); b["time"] = pd.to_datetime(b.time)
    b = b[b.time >= "2014-01-01"].sort_values("time").reset_index(drop=True)
    C = daily_clock(b.time.values, b.state.values)
    chk = {}
    chk["committed_vs_dt4gate_diffs"] = int((C.committed.values != dt_4gate(b.state.values.astype(int))).sum())
    ep = extract_episodes(b.time.values, b.state.values.astype(int)); ep["end"] = pd.to_datetime(ep["end"])
    nc = ep[ep.outcome != "commit"]
    m = C.set_index("time").k.reindex(nc.end).values
    chk["episode_end_k_mismatch(non-commit)"] = int((m != nc.length.values).sum()); chk["n_episodes"] = len(ep)
    live = pd.read_parquet(W + "/data/bq_cache/vnindex_5state_dt5g_live.parquet"); live["time"] = pd.to_datetime(live.time)
    j = C.merge(live, on="time"); chk["dt4_vs_dt5g_live_state_diffs(=macro cap)"] = int((j.committed != j.state).sum())
    chk["old_clock_def_nonzero_days(state_raw!=state)"] = int((j.state_raw != j.state).sum())
    chk["cache_last_date"] = str(C.time.iloc[-1].date())
    # (3) đối chiếu get_dt_gate_clock() trên dữ liệu BQ tươi
    try:
        import dna_report as R
        g = R.get_dt_gate_clock()
        bb = R._bq("SELECT t.time, t.state FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean t WHERE t.time>='2014-01-01' ORDER BY t.time", max_rows=8000)
        bb = bb.sort_values("time").reset_index(drop=True)
        Cb = daily_clock(pd.to_datetime(bb.time).values, bb.state.astype(int).values); last = Cb.iloc[-1]
        mine = {"active": bool(last.active), "cand": int(last.cand), "k": int(last.k), "need": int(last.need), "committed": int(last.committed),
                "asof": str(last.time.date())}
        chk["get_dt_gate_clock"] = {k: g.get(k) for k in ("active", "cand", "k", "need", "committed", "asof")} if g else None
        chk["replay_bq_last"] = mine
        chk["match_today"] = bool(g) and all(g.get(k) == mine[k] for k in (["active", "cand", "k", "need", "committed", "asof"] if g.get("active") else ["active", "committed", "asof"]))
        # vintage: cache vs BQ cùng ngày có giống nhau không
        ov = C.merge(Cb[["time", "k", "committed"]], on="time", suffixes=("", "_bq"))
        chk["cache_vs_bq_k_diffs_overlap"] = int((ov.k != ov.k_bq).sum()); chk["overlap_days"] = len(ov)
    except Exception as e:
        chk["get_dt_gate_clock_error"] = repr(e)
    C.to_csv(os.path.join(HERE, "dt_clock_daily.csv"), index=False)
    json.dump(chk, open(os.path.join(HERE, "clock_selfcheck.json"), "w"), indent=1, default=str)
    print(json.dumps(chk, indent=1, default=str)); print(C.k.describe()); print(C.active.mean())

if __name__ == "__main__":
    main()
