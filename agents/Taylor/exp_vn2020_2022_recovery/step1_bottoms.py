import pandas as pd

df = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv",
                  usecols=["time", "Close", "Volume", "Trading_Value"])
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)

def window(a, b):
    return df[(df["time"] >= a) & (df["time"] <= b)]

print("=== 2020 episode: 2019-12-01 -> 2021-12-31 (bao gom wave 2 Delta) ===")
w = window("2019-12-01", "2021-12-31")
print("N rows:", len(w))
bottom = w.loc[w["Close"].idxmin()]
print("Absolute bottom in window:", bottom["time"].date(), bottom["Close"])
# March 2020 crash window specifically
w1 = window("2020-01-01", "2020-06-30")
b1 = w1.loc[w1["Close"].idxmin()]
print("Wave1 (H1 2020) bottom:", b1["time"].date(), b1["Close"])
# peak before crash
pre = window("2019-12-01", "2020-03-31")
p1 = pre.loc[pre["Close"].idxmax()]
print("Pre-crash peak:", p1["time"].date(), p1["Close"])
# post wave1 recovery peak before any wave2 dip
w1r = window("2020-04-01", "2021-12-31")
p1r = w1r.loc[w1r["Close"].idxmax()]
print("Peak after wave1 bottom (search through end 2021):", p1r["time"].date(), p1r["Close"])

# check for a second dip (Delta wave Q3 2021)
w2 = window("2021-01-01", "2021-12-31")
print("\n2021 monthly close (check for 2nd dip):")
w2m = w2.set_index("time")["Close"].resample("ME").last()
print(w2m)

print("\n=== 2022 episode: dd52<=-20% window ===")
w22 = window("2022-01-01", "2023-06-30")
peak_before = window("2021-10-01", "2022-05-31")
p22 = peak_before.loc[peak_before["Close"].idxmax()]
print("Peak before 2022 decline:", p22["time"].date(), p22["Close"])
w22b = window("2022-04-01", "2022-12-31")
b22 = w22b.loc[w22b["Close"].idxmin()]
print("2022 bottom (Apr-Dec window):", b22["time"].date(), b22["Close"])
dd = (b22["Close"] / p22["Close"] - 1) * 100
print(f"Drawdown from peak: {dd:.2f}%")

# peak after bottom
post22 = window("2022-11-01", "2024-12-31")
p22r = post22.loc[post22["Close"].idxmax()]
print("Peak after 2022 bottom:", p22r["time"].date(), p22r["Close"])
ret = (p22r["Close"] / b22["Close"] - 1) * 100
days = (p22r["time"] - b22["time"]).days
print(f"Bottom->peak return: {ret:.2f}% over {days} calendar days")

ret20 = (p1r["Close"] / b1["Close"] - 1) * 100
days20 = (p1r["time"] - b1["time"]).days
print(f"\n2020 Bottom->peak(2021) return: {ret20:.2f}% over {days20} calendar days")
