# Research-only patch: adds env CAPIT_FLAG_GATE to a COPY of pt_v23 (production file untouched).
import sys, re
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
anchor = '''    if e.empty:
        _basket_cache[d] = []
        return []
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]'''
assert s.count(anchor) == 1
new = '''    if e.empty:
        _basket_cache[d] = []
        return []
    e = _capit_flag_filter(d, e)
    if e.empty:
        _basket_cache[d] = []
        return []
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]'''
s = s.replace(anchor, new)
fn = '''
# ---- RESEARCH (job Taylor_20261103_024121): CAPIT flag gate, env CAPIT_FLAG_GATE ----------------
# off (default) = byte-identical. Flags read from a PIT export of tav2_mike.universe_pit_quality
# (CAPIT_FLAG_FILE). Candidate (pre-ranking) names carrying a flag in the chosen set are dropped.
CAPIT_FLAG_GATE = os.environ.get("CAPIT_FLAG_GATE", "off").lower()
_FLAGSETS = {"all": {"FLOOR_FAIL", "RATING_FAIL", "BANNED", "UNKNOWN_FLOOR", "THANH_KHOAN_CHET", "NGOAI_UNIVERSE"},
             "floor": {"FLOOR_FAIL", "UNKNOWN_FLOOR", "BANNED"},
             "rating": {"RATING_FAIL"},
             "strict": {"FLOOR_FAIL", "RATING_FAIL", "BANNED", "UNKNOWN_FLOOR", "THANH_KHOAN_CHET", "NGOAI_UNIVERSE", "UNKNOWN_RATING"}}
_flag_df = None
def _capit_flag_filter(d, e):
    global _flag_df
    # always log the ungated candidate pool with flags (diagnostic only)
    if _flag_df is None:
        _flag_df = pd.read_csv(os.environ["CAPIT_FLAG_FILE"], parse_dates=["time"])
    f = _flag_df[_flag_df["time"] == pd.Timestamp(d)].set_index("ticker")
    def _flag(t):
        if t not in f.index: return "NGOAI_UNIVERSE"
        r = f.loc[t]
        if pd.notna(r["adv3m"]) and r["adv3m"] <= 1e8: return "THANH_KHOAN_CHET"
        return str(r["quality_flag"])
    fl = {t: _flag(t) for t in e["ticker"]}
    print(f"    [capflag-pool] {d.date()} " + ",".join(f"{t}:{fl[t]}:{pz:.2f}" for t, pz in zip(e["ticker"], e["pbz"])))
    if CAPIT_FLAG_GATE == "off":
        return e
    bad = _FLAGSETS[CAPIT_FLAG_GATE]
    keep = e[[fl[t] not in bad for t in e["ticker"]]]
    print(f"    [capflag:{CAPIT_FLAG_GATE}] {d.date()} pool {len(e)} -> {len(keep)} dropped="
          + ",".join(sorted(t for t in e["ticker"] if fl[t] in bad)))
    return keep

_basket_cache = {}
def capit_basket(d):'''
a2 = '\n_basket_cache = {}\ndef capit_basket(d):'
assert s.count(a2) == 1
s = s.replace(a2, fn)
# filename tag so outputs never collide with pinned CSVs
a3 = '_div_tag = "" if CAPIT_DIV_GATE == "off" else f"_capdiv{CAPIT_DIV_GATE}{CAPIT_DIV_MINN}"'
assert s.count(a3) == 1
s = s.replace(a3, a3 + '\n_div_tag += "_capflag" + os.environ.get("CAPIT_FLAG_GATE", "off").lower() + "_exp_"')
open(p, "w", encoding="utf-8").write(s)
print("patched")
