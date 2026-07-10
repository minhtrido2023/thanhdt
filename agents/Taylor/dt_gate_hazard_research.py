# DT 4-gate hazard/survival research — exploratory, job Taylor_20260710_122230
# Research only: no production code touched, no BQ tables created.
#
# Mechanism modeled (macro_state_live.py::_dt_4gate, = DT_10_25_25):
#   candidate streak pr = consecutive sessions the raw base state differs from committed;
#   commit when pr >= need, where need = enC=25 (into CRISIS), enX=25 (into EX-BULL),
#   exC=10 (leave CRISIS), exX=10 (leave EX-BULL), default=10 (other NEUTRAL/BEAR/BULL moves).
#   NOTE: the user's "7 sessions" figure matches NOTHING in the live pipeline — the
#   governing threshold for BEAR/BULL commits is 10 (default), 25 for CRISIS/EX-BULL entry.
#
# Episode definition (causal, from base series only):
#   an episode starts the first session the raw base state != current committed state and
#   ends either at COMMIT (streak reaches `need`) or REVERT (raw state changes — back to
#   committed, or to a different candidate, which starts a new episode).
#   Every quantity at session t uses only data up to t (the gate itself is causal);
#   the episode LABEL (commit/revert) is known only at episode end — noted in report.

import numpy as np
import pandas as pd

BQC = "/home/trido/thanhdt/WorkingClaude/data/bq_cache"
STATE_NAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
rng = np.random.default_rng(20260710)


def dt_4gate(states, default=10, enC=25, exC=10, enX=25, exX=10):
    out = states.copy(); committed = states[0]; ps, pr = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed:
            out[t] = committed; continue
        need = (enC if ps == 1 else enX if ps == 5
                else exC if committed == 1 else exX if committed == 5 else default)
        if pr >= need: committed = ps
        out[t] = committed
    return out


def need_for(cand, committed, default=10, enC=25, exC=10, enX=25, exX=10):
    return (enC if cand == 1 else enX if cand == 5
            else exC if committed == 1 else exX if committed == 5 else default)


def extract_episodes(times, raw, default=10, enC=25, exC=10, enX=25, exX=10):
    """Walk the gate exactly as _dt_4gate does, recording candidate episodes."""
    episodes = []
    committed = raw[0]; ps, pr = raw[0], 1
    cur = None  # active episode dict
    for t in range(1, len(raw)):
        s = raw[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed:
            if cur is not None:          # candidate streak broke by returning to committed
                cur["outcome"] = "revert"; episodes.append(cur); cur = None
            continue
        # ps is a candidate != committed
        if cur is not None and (cur["cand"] != ps):
            # streak broke by switching to a DIFFERENT candidate -> old episode reverted
            cur["outcome"] = "revert"; episodes.append(cur); cur = None
        if cur is None:
            cur = dict(start=times[t], committed_from=int(committed), cand=int(ps),
                       need=need_for(ps, committed, default, enC, exC, enX, exX), length=0)
        cur["length"] = pr
        cur["end"] = times[t]
        need = need_for(ps, committed, default, enC, exC, enX, exX)
        if pr >= need:
            committed = ps
            cur["outcome"] = "commit"; episodes.append(cur); cur = None
    if cur is not None:
        cur["outcome"] = "censored"; episodes.append(cur)   # still running at data end
    return pd.DataFrame(episodes)


def hazard_table(ep, need, kmax=None):
    """Per-k: n_at_risk (episodes reaching streak k), reverts at k, commits at k,
       revert hazard h(k), and P(eventual commit | reached k)."""
    kmax = kmax or need
    rows = []
    for k in range(1, kmax + 1):
        at_risk = ep[ep["length"] >= k]
        n = len(at_risk)
        rev_k = int(((ep["length"] == k) & (ep["outcome"] == "revert")).sum())
        com_k = int(((ep["length"] == k) & (ep["outcome"] == "commit")).sum())
        cen_k = int(((ep["length"] == k) & (ep["outcome"] == "censored")).sum())
        # P(commit | reached k): among episodes that reached k and are resolved
        res = at_risk[at_risk["outcome"] != "censored"]
        p_commit = (res["outcome"] == "commit").mean() if len(res) else np.nan
        rows.append(dict(k=k, n_at_risk=n, revert_at_k=rev_k, commit_at_k=com_k,
                         censored_at_k=cen_k,
                         hazard_revert=rev_k / n if n else np.nan,
                         p_commit_given_k=p_commit, n_resolved=len(res)))
    return pd.DataFrame(rows)


def bootstrap_pcommit(ep, need, n_boot=2000):
    """Episode-level bootstrap CI for P(commit | reached k)."""
    ep_r = ep[ep["outcome"] != "censored"].reset_index(drop=True)
    ks = np.arange(1, need + 1)
    if len(ep_r) == 0:
        return pd.DataFrame(dict(k=ks, lo=np.nan, hi=np.nan))
    L = ep_r["length"].values; C = (ep_r["outcome"] == "commit").values
    boot = np.full((n_boot, len(ks)), np.nan)
    for b in range(n_boot):
        idx = rng.integers(0, len(ep_r), len(ep_r))
        Lb, Cb = L[idx], C[idx]
        for j, k in enumerate(ks):
            m = Lb >= k
            if m.sum(): boot[b, j] = Cb[m].mean()
    lo = np.nanpercentile(boot, 2.5, axis=0); hi = np.nanpercentile(boot, 97.5, axis=0)
    return pd.DataFrame(dict(k=ks, lo=lo, hi=hi))


# NOTE: everything below is the ad-hoc analysis driver. It is guarded by __main__ so the
# gate functions above (dt_4gate / need_for / extract_episodes / hazard_table) can be imported
# by other code (e.g. dna_report.py's candidate-streak clock) WITHOUT re-running the analysis
# or hitting the parquet cache. Running `python dt_gate_hazard_research.py` behaves unchanged.
if __name__ == "__main__":
    # ── load base v3.4b, warm up from 2014 exactly like production ──
    base = pd.read_parquet(f"{BQC}/vnindex_5state_tam_quan_v34b_clean.parquet")
    base["time"] = pd.to_datetime(base["time"])
    base = base[base["time"] >= "2014-01-01"].sort_values("time").reset_index(drop=True)
    raw = base["state"].values.astype(int)
    times = base["time"].values

    # ── self-check 1: replicated DT4 vs published dt5g_live ──
    dt4 = dt_4gate(raw)
    live = pd.read_parquet(f"{BQC}/vnindex_5state_dt5g_live.parquet")
    live["time"] = pd.to_datetime(live["time"])
    chk = base[["time"]].copy(); chk["dt4_repl"] = dt4
    chk = chk.merge(live.rename(columns={"state": "dt5g", "state_raw": "live_raw"}), on="time", how="inner")
    print(f"[selfcheck] overlap {len(chk)} rows; replicated-DT4 vs dt5g_live.state diffs: "
          f"{(chk['dt4_repl'] != chk['dt5g']).sum()} (expected ~49 macro-cap sessions)")
    print(f"[selfcheck] replicated-DT4 vs dt5g_live.state_raw diffs: {(chk['dt4_repl'] != chk['live_raw']).sum()}")
    n_trans_base = int((np.diff(raw) != 0).sum())
    n_trans_dt4 = int((np.diff(dt4) != 0).sum())
    print(f"[selfcheck] base transitions 2014+: {n_trans_base}; DT4 transitions: {n_trans_dt4}")

    # ── self-check 2: episode extraction consistency with gate ──
    ep = extract_episodes(times, raw)
    ep["start"] = pd.to_datetime(ep["start"]); ep["end"] = pd.to_datetime(ep["end"])
    n_commit = (ep["outcome"] == "commit").sum()
    print(f"[selfcheck] episodes: {len(ep)} total | commit {n_commit} | revert {(ep['outcome']=='revert').sum()} "
          f"| censored {(ep['outcome']=='censored').sum()} — commits must equal DT4 transitions: {n_commit == n_trans_dt4}")

    ep["group"] = np.where(ep["need"] == 25, "need25_into_CRISIS_EXBULL", "need10_other")
    ep["year"] = ep["start"].dt.year
    ep["period"] = np.where(ep["year"] <= 2019, "IS_2014_2019", "OOS_2020_now")

    print("\n=== episode summary by group/outcome ===")
    print(ep.groupby(["group", "outcome"]).size().unstack(fill_value=0))
    print("\n=== episodes by candidate state ===")
    print(ep.assign(cand_name=ep["cand"].map(STATE_NAME)).groupby(["group", "cand_name", "outcome"]).size().unstack(fill_value=0))

    for g, need in [("need10_other", 10), ("need25_into_CRISIS_EXBULL", 25)]:
        sub = ep[ep["group"] == g]
        print(f"\n================ {g} (need={need}) — FULL 2014+ ================")
        ht = hazard_table(sub, need)
        ci = bootstrap_pcommit(sub, need)
        out = ht.merge(ci, on="k")
        print(out.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        out.to_csv(f"/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/data_dt_hazard_{g}_full.csv", index=False)
        for per in ["IS_2014_2019", "OOS_2020_now"]:
            s2 = sub[sub["period"] == per]
            ht2 = hazard_table(s2, need)
            ci2 = bootstrap_pcommit(s2, need)
            o2 = ht2.merge(ci2, on="k")
            print(f"\n---- {g} · {per} (episodes={len(s2)}, commits={(s2['outcome']=='commit').sum()}) ----")
            print(o2[["k", "n_at_risk", "n_resolved", "p_commit_given_k", "lo", "hi"]]
                  .to_string(index=False, float_format=lambda x: f"{x:.3f}"))
            o2.to_csv(f"/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/data_dt_hazard_{g}_{per}.csv", index=False)

    # ── streak-length distribution of reverted episodes (where do candidates die?) ──
    print("\n=== revert length distribution (need10 group) ===")
    print(ep[(ep.group == "need10_other") & (ep.outcome == "revert")]["length"].value_counts().sort_index())
    print("\n=== revert length distribution (need25 group) ===")
    print(ep[(ep.group == "need25_into_CRISIS_EXBULL") & (ep.outcome == "revert")]["length"].value_counts().sort_index())

    # ── per-year commit counts: is any single year carrying the pattern? (LOO flavor) ──
    print("\n=== commits per year ===")
    print(ep[ep.outcome == "commit"].groupby(["year", "group"]).size().unstack(fill_value=0))

    ep.to_csv("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/data_dt_gate_episodes.csv", index=False)
    print("\nsaved: data_dt_gate_episodes.csv + per-group hazard CSVs")
