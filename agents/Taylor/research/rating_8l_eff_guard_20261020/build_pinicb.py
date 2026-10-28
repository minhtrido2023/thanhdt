"""Build rating_8l_history voi ICB_SQL doc tav2_pin.ticker_pin_202610 (vi tav2_bq.ticker thieu 243 ma 2026-10-20).
argv: <code_dir> <out_csv>. Ca CTL va EXP dung cung patch => 1 truc (guard)."""
import os, sys
code, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, code); os.chdir(code)
os.environ["R8L_HIST_OUT"] = out; os.environ["R8L_HIST_NO_BQ_REFRESH"] = "1"
import rating_8l_history as R
assert R.__file__.startswith(code), R.__file__
assert R.ICB_SQL.count("FROM tav2_bq.ticker AS t") == 1
R.ICB_SQL = R.ICB_SQL.replace("FROM tav2_bq.ticker AS t", "FROM tav2_pin.ticker_pin_202610 AS t")
print("module:", R.__file__)
R.main()
