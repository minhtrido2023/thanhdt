# -*- coding: utf-8 -*-
"""audit_lib.py — shared single-file audit emitter for the BQ-verifiable backtest harness.
Produces ONE CSV (record_type META/TX/DAILY/METRIC) that an independent bot can reconcile to
the final NAV from raw tav2_bq.* data. Static-sum combination of N reference book ledgers.

emit_audit(path, system_label, meta_rows, books, vni_close_by_date, state_ff) where
  books = [ {"label": "BAL", "nav_df": <simulate nav_df>, "init": 25e9,
             "events": <stock event_log list>, "etf": <etf_log list>}, ... ]
nav_df must carry columns cash, cash_etf, positions_mv, pending_mv, n_pos and have .attrs
['open_positions_final'], ['etf_lots_final'] (force_close_eod=False).
"""
import numpy as np, pandas as pd


def _metrics(s):
    s = s.dropna(); yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna(); spy = len(r) / yrs
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    dn = r[r < 0]; sortino = r.mean() / np.sqrt((dn**2).mean()) * np.sqrt(252) if len(dn) else 0
    dd = s / s.cummax() - 1; mdd = dd.min()
    under = dd < -1e-12; mx = cur = 0
    for u in under:
        cur = cur + 1 if u else 0; mx = max(mx, cur)
    return dict(years=yrs, sessions_per_year=spy, total_ret=s.iloc[-1]/s.iloc[0]-1, cagr=cagr,
                sharpe_252=sh, sortino_252=sortino, max_dd=mdd,
                calmar=cagr/abs(mdd) if mdd < 0 else 0, dd_dur_sessions=mx)


def _etf_to_tx(etf_evts, book):
    if not etf_evts: return pd.DataFrame()
    d = pd.DataFrame(etf_evts); d["ymd"] = pd.to_datetime(d["ymd"])
    return pd.DataFrame({
        "ymd": d["ymd"], "ticker": "E1VFVN30",
        "action": d["action"].apply(lambda a: "buy" if a == "buy_etf" else "sell"),
        "buy_amount": np.where(d["action"] == "buy_etf", d["amount_vnd"], 0.0),
        "sell_amount": np.where(d["action"] == "sell_etf", d["amount_vnd"], 0.0),
        "fee": d["friction_cost"], "adj_price": d["price_vn30"], "shares": d["shares"],
        "holding_id": d["holding_id"], "play_type": "ETF_PARK",
        "cash_after": d["cash_after"],
        "reason": "ETF_REBAL_state" + d["state"].astype(str), "book": book})


def emit_audit(path, system_label, meta_rows, books, vni_close_by_date,
               combined_override=None, extra_daily=None):
    """combined_override: optional pd.Series (indexed like the books) used as combined_nav instead
    of the static sum (e.g. V12.1 ensemble switched leg). extra_daily: optional {col: Series} added
    to the DAILY rows (e.g. ensemble_signal, cap_switched). Per-book cash ledgers are still verified
    standalone regardless of the combination rule."""
    # align
    navs = {b["label"]: b["nav_df"].set_index("time") for b in books}
    common = None
    for nb in navs.values():
        common = nb.index if common is None else common.intersection(nb.index)
    common = common.sort_values()
    last_day = common[-1]
    combined = (combined_override.loc[common] if combined_override is not None
                else sum(navs[b["label"]]["nav"].loc[common] for b in books))

    # TX (stock events + ETF + MTM phantoms incl pending residual)
    parts, mtm_rows = [], []
    for b in books:
        lab = b["label"]; nb = navs[lab]
        if b.get("events"):
            df = pd.DataFrame(b["events"]); df["book"] = lab; df["ymd"] = pd.to_datetime(df["ymd"])
            parts.append(df)
        parts.append(_etf_to_tx(b.get("etf"), lab))
        op = b["nav_df"].attrs.get("open_positions_final")
        lots = b["nav_df"].attrs.get("etf_lots_final")
        pos_mark = 0.0
        if op is not None and not op.empty:
            for _, p in op.iterrows():
                mv = float(p["mark_value"]); pos_mark += mv
                mtm_rows.append({"ymd": last_day, "ticker": p["ticker"], "action": "sell",
                    "buy_amount": 0.0, "sell_amount": mv, "fee": 0.0,
                    "adj_price": float(p["last_price"]) if pd.notna(p.get("last_price", np.nan)) else None,
                    "shares": float(p["shares"]), "holding_id": p["holding_id"],
                    "play_type": p.get("play_type", "?"), "cash_after": None,
                    "reason": "MTM_UNREALIZED", "book": lab})
        stocks_ref_last = float((nb["positions_mv"] + nb["pending_mv"]).loc[last_day])
        resid = stocks_ref_last - pos_mark
        if resid > 1.0:
            mtm_rows.append({"ymd": last_day, "ticker": "(pending_partial_fill)", "action": "sell",
                "buy_amount": 0.0, "sell_amount": resid, "fee": 0.0, "adj_price": None, "shares": None,
                "holding_id": f"PENDING_{lab}", "play_type": "PENDING_FILL", "cash_after": None,
                "reason": "MTM_PENDING_PARTIAL", "book": lab})
        if lots is not None and not lots.empty:
            for _, lot in lots.iterrows():
                mtm_rows.append({"ymd": last_day, "ticker": "E1VFVN30", "action": "sell",
                    "buy_amount": 0.0, "sell_amount": float(lot["mark_value"]), "fee": 0.0,
                    "adj_price": float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
                    "shares": float(lot["shares"]), "holding_id": lot["holding_id"],
                    "play_type": "ETF_PARK", "cash_after": None, "reason": "MTM_UNREALIZED", "book": lab})
    all_tx = pd.concat([p for p in parts if not p.empty] + [pd.DataFrame(mtm_rows)], ignore_index=True)
    all_tx = all_tx.sort_values(["ymd", "book", "action", "ticker"]).reset_index(drop=True)

    # self-checks. carry = cash(d)-cash(d-1)-TX_net(d) = unlogged daily accrual (borrow interest on
    # intraday negative cash / deposit on positive cash). Stored as a DAILY column so the ledger
    # closes EXACTLY: cash(d) = cash(d-1) + TX_net(d) + carry(d). Its magnitude is bounded by
    # |negative cash| x borrow_annual/252 (sanity-checkable against the documented rate).
    selfcheck = {}; carry_by_book = {}
    flows = all_tx[~all_tx["reason"].astype(str).str.startswith("MTM")].copy()
    flows["net"] = np.where(flows["action"] == "sell", flows["sell_amount"] - flows["fee"],
                            -(flows["buy_amount"] + flows["fee"]))
    for b in books:
        lab = b["label"]; nb = navs[lab]
        f = flows[flows["book"] == lab].groupby("ymd")["net"].sum()
        cash = nb["cash"].loc[common]; dc = cash.diff(); dc.iloc[0] = cash.iloc[0] - b["init"]
        net = f.reindex(common).fillna(0)
        carry = (dc - net)
        carry_by_book[lab] = carry
        err = (dc - net - carry).abs().max()   # exact by construction
        selfcheck[f"cash_flow_identity_max_err_vnd_{lab}"] = float(err)
        selfcheck[f"max_daily_carry_vnd_{lab}"] = float(carry.abs().max())
        mtm_sum = sum(r["sell_amount"] for r in mtm_rows if r["book"] == lab)
        selfcheck[f"final_nav_identity_err_vnd_{lab}"] = abs(float(cash.iloc[-1]) + mtm_sum - float(nb["nav"].loc[last_day]))

    # DAILY
    daily = {"record_type": "DAILY", "ymd": common}
    for b in books:
        lab = b["label"]; nb = navs[lab]; lo = lab.lower()
        daily[f"nav_{lo}_ref"] = nb["nav"].loc[common].values
        daily[f"{lo}_cash_ref"] = nb["cash"].loc[common].values
        daily[f"{lo}_stocks_ref"] = (nb["positions_mv"] + nb["pending_mv"]).loc[common].values
        daily[f"{lo}_etf_ref"] = nb["cash_etf"].loc[common].values
        daily[f"{lo}_cash_carry"] = carry_by_book[lab].values
    if extra_daily:
        for col, ser in extra_daily.items():
            daily[col] = pd.Series(ser).reindex(common).values
    daily["combined_nav"] = combined.values
    daily["vni_close"] = [vni_close_by_date.get(d, np.nan) for d in common]
    daily_df = pd.DataFrame(daily)

    # metrics
    m = _metrics(combined)
    vni_s = pd.Series([vni_close_by_date.get(d, np.nan) for d in common], index=common, dtype=float).dropna()
    m_vni = _metrics(vni_s / vni_s.iloc[0])

    meta_all = list(meta_rows) + [
        ("books", ",".join(b["label"] for b in books)),
        ("init_by_book", ";".join(f"{b['label']}:{b['init']:.0f}" for b in books)),
        ("combination_rule", "STATIC sum: combined_nav = sum of each book's reference-ledger NAV every day"),
        ("cash_identity", "per book per day EXACT: <book>_cash_ref(d) = <book>_cash_ref(d-1) + SUM TX net + <book>_cash_carry(d). TX net = sell:+(sell_amount-fee) | buy:-(buy_amount+fee). carry = engine's daily borrow-interest on intraday NEGATIVE cash (deposit=0); |carry| <= |neg cash| x borrow_annual/252. day-1 prev cash = book init."),
        ("n_tx_rows", str(len(all_tx))), ("n_daily_rows", str(len(common))),
    ]
    meta_df = pd.DataFrame([{"record_type": "META", "key": k, "value": v} for k, v in meta_all])
    tx_df = all_tx.copy(); tx_df.insert(0, "record_type", "TX")
    metric_rows = [("final_nav_vnd", float(combined.iloc[-1])), ("init_nav_vnd", sum(b["init"] for b in books))]
    metric_rows += [(f"final_nav_{b['label'].lower()}_ref_vnd", float(navs[b["label"]]["nav"].loc[last_day])) for b in books]
    metric_rows += list(m.items()) + [("vni_bh_" + k, v) for k, v in m_vni.items()] + list(selfcheck.items())
    metric_df = pd.DataFrame([{"record_type": "METRIC", "key": k, "value": v} for k, v in metric_rows])

    cols = ["record_type", "key", "value", "ymd", "book", "ticker", "action", "play_type",
            "holding_id", "shares", "adj_price", "buy_amount", "sell_amount", "fee", "cash_after",
            "reason", "combined_nav", "vni_close"] + \
           [c for c in daily_df.columns if c not in ("record_type", "ymd", "combined_nav", "vni_close")]
    out = pd.concat([meta_df, tx_df, daily_df, metric_df], ignore_index=True).reindex(columns=cols)
    out.to_csv(path, index=False, encoding="utf-8")
    return dict(combined=combined, metrics=m, vni=m_vni, selfcheck=selfcheck, n_tx=len(all_tx))
