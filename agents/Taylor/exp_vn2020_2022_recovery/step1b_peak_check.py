import pandas as pd

df = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv",
                  usecols=["time", "Close", "Volume", "Trading_Value"])
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)

def window(a, b):
    return df[(df["time"] >= a) & (df["time"] <= b)]

print("2022 monthly close:")
w = window("2022-01-01", "2022-12-31").set_index("time")["Close"].resample("ME").last()
print(w)

print("\n2022-11 to 2024-06 monthly close (post-bottom recovery path):")
w2 = window("2022-11-01", "2024-06-30").set_index("time")["Close"].resample("ME").last()
print(w2)

# find first local peak (>=10% drawdown after it, i.e. clear reversal) after 2022-11-15 bottom
sub = window("2022-11-15", "2024-12-31").reset_index(drop=True)
running_max = 0
running_max_date = None
peaks = []
for i, row in sub.iterrows():
    if row["Close"] > running_max:
        running_max = row["Close"]
        running_max_date = row["time"]
    dd = (row["Close"]/running_max - 1)*100
    if dd <= -10 and running_max_date is not None:
        peaks.append((running_max_date, running_max, row["time"], dd))
# print first occurrence of >=10% dd from a peak, dedup by peak date
seen = set()
for p in peaks:
    if p[0] not in seen:
        seen.add(p[0])
        print("Local peak with subsequent >=10% DD:", p)
