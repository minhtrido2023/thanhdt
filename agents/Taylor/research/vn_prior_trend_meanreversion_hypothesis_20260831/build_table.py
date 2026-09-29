import pandas as pd
from datetime import date

df = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv", usecols=["time","Close"])
df["time"] = pd.to_datetime(df["time"]); df = df.sort_values("time").set_index("time")

def c(d):
    idx = df.index.asof(pd.Timestamp(d))
    return df.loc[idx, "Close"], idx

pairs = [
    ("2007-2009 Wave1 (decline)", "2007-03-12", "2009-02-24"),
    ("2007-2009 Wave1 (recovery)", "2009-02-24", "2009-10-22"),
    ("2011-2012 (decline, peak->abs false bottom)", "2009-10-22", "2012-01-06"),
    ("2011-2012 (decline, peak->true bottom leading recovery)", "2009-10-22", "2012-11-02"),
    ("2011-2012 (recovery, true bottom->clean reversal)", "2012-11-02", "2013-06-07"),
    ("2018 (decline)", "2018-04-09", "2018-10-30"),
    ("2018 (weak-recovery to pre-COVID peak)", "2018-10-30", "2020-01-22"),
    ("2020 (decline)", "2020-01-22", "2020-03-24"),
    ("2020 (recovery to next peak)", "2020-03-24", "2022-01-06"),
    ("2020 (recovery to 1st shallow peak)", "2020-03-24", "2020-06-10"),
    ("2022 (decline)", "2022-01-06", "2022-11-15"),
    ("2022 (recovery to clean reversal peak)", "2022-11-15", "2023-09-06"),
]
for name, d1, d2 in pairs:
    c1, i1 = c(d1); c2, i2 = c(d2)
    days = (i2 - i1).days
    ret = (c2/c1 - 1) * 100
    print(f"{name}: {i1.date()}({c1:.2f}) -> {i2.date()}({c2:.2f}) = {ret:+.2f}% trong {days} ngày ({days/30.44:.1f} thang)")
