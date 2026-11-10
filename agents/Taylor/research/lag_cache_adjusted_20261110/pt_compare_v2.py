# So papertrade pt_v22_dt5g (code main 32d65bbf6): ctrl (pkl canonical) vs adj (pkl adjusted + events/edge dẫn xuất). 1 trục = dữ liệu giá LAG.
import re, json, hashlib, pandas as pd
R = __file__.rsplit("/", 1)[0] + "/pt"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
out = {}
for t in ("ctrl", "ctrl2", "adjv2"):
    log = open(f"{R}/{t}.log").read()
    g = lambda pat: re.search(pat, log).group(1)
    out[t] = {"final_B": float(g(r"Final: ([0-9.]+)B")), "ret_pct": float(g(r"ret=(-?[0-9.]+)%")), "maxdd_pct": float(g(r"MaxDD=(-?[0-9.]+)%")),
              "BAL_final_B": float(g(r"BAL events: .*final ([0-9.]+)B")), "LAG_final_B": float(g(r"LAG events: .*final ([0-9.]+)B")),
              "LAG_events": g(r"LAG events: ([^;]+);"), "mean12_latest": g(r"mean12 latest=(-?[0-9.]+)%"),
              "logs_md5": md5(f"{R}/{t}_logs.csv"), "tx_md5": md5(f"{R}/{t}_transactions.csv")}
c, a = (pd.read_csv(f"{R}/{t}_transactions.csv") for t in ("ctrl2", "adjv2"))
bc, ba = c[c.book == "BAL"].reset_index(drop=True), a[a.book == "BAL"].reset_index(drop=True)
out["BAL_tx_identical"] = bc.equals(ba)
lc, la = c[c.book != "BAL"], a[a.book != "BAL"]
key = ["ymd", "ticker", "action"]
m = lc.merge(la, on=key, how="outer", indicator=True, suffixes=("_c", "_a"))
out["LAG_tx"] = {"ctrl": len(lc), "adj": len(la), "only_ctrl": int((m._merge == "left_only").sum()), "only_adj": int((m._merge == "right_only").sum())}
print(json.dumps(out, indent=1, ensure_ascii=False)); json.dump(out, open(f"{R}/../pt_results_v2.json", "w"), indent=1, ensure_ascii=False)
print(m[m._merge != "both"][key + ["_merge"]].head(30).to_string(index=False))
