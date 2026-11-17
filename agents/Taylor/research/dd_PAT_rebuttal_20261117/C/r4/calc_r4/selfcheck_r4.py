"""Self-check r4: tái tính TÂM bằng đường độc lập (không import model_r4/model_r3, không cây lá).
E[mức] dạng đóng (assumptions r3 §3, giữ ở r4), E[EBIT] tuyến tính, tồn kho: tích phân liên tục theo τ_B (không xô).
"""
import json, math
rev = 1366.520 / 0.75
k = 1.37 / 1.13 * 3857 * 1e-8
u27, r27 = 0.5520 + 68 * k, 0.4864 + 567 * k
o3, o2, o1 = 0.5520 - 215 * k, 0.4864 + 284 * k, 0.4660 + 334 * k
lam = math.log(1 / 0.70) / 6.5
elec = 0.985 * (1 + 0.0105 + 0.015 - 0.002)
step = 1 - 0.85 / 0.90
fr = 22843840946 / 487507728152                       # cước/DT nước ngoài 9T/26 (p29, p31)
pT = [(1.0, 0.35, 0.65), (0.35, 0.35, 0.25), (0.135, 0.135, 0.10)]
pX15 = 0.97
E_p = 0.9384 * 0.32 + 0.9961 * 0.58 + 1.0670 * 0.10
E_f = sum(w * (pX15 * (1 - s * step) + (1 - pX15)) for s, sx, w in pT)
E_fsx = sum(w * sx * (pX15 * (1 - s * step) + (1 - pX15)) for s, sx, w in pT)
cash = (1.246 + 558.069 - 67.218 - 76.690) - (70 - 70 * 0.048 / 0.135) - 0.06 * 215.713
r, g = 0.135, 0.02

def E_level(m, yr):
    if m < 7.5: return u27 if yr == 2027 else o3
    PA = 0.5 if m >= 10.5 else 0.0
    PB = 1 - math.exp(-lam * m)
    un, re = (u27, r27) if yr == 2027 else (o3, o2)
    v = un + (re - un) * (0.5 * PA + 0.5 * PB)
    if yr >= 2028: v += (o1 - o2) * 0.5 * PA * PB
    return v

def E_nvl(yr, steps=2400):
    a = 1.5 if yr == 2027 else 13.5 + 12 * (yr - 2028)
    b = 13.5 if yr == 2027 else a + 12
    h = (b - a) / steps
    return sum(E_level(a + (i + 0.5) * h, yr) for i in range(steps)) / steps

def E_ebit(yr):
    return rev * E_f * E_p - rev * (E_nvl(yr) + 0.2508 * elec + 0.0582) - (fr * rev * E_fsx * E_p + 28.3)

# tồn kho dư: 120,190 − TB(84,700; 67,712; 74,843), giải phóng tại t = max(7,5; min(τ_B; 10,5 nếu A giải))
inv = 120.190 - (84.700 + 67.712 + 74.843) / 3
disc = lambda t: (1 + r) ** (-t / 12)
# τ_B ~ Exp(lam): P(τ_B ≤ 7,5) => t = 7,5 ; τ_B ∈ (7,5, x] => t = τ_B ; tích phân số
def E_disc(cap):
    p75 = 1 - math.exp(-lam * 7.5); acc = p75 * disc(7.5)
    if cap is None:   # A không giải: tích phân (7,5, ∞)
        T = 7.5; h = 0.01
        while T < 2000:
            acc += lam * math.exp(-lam * (T + h / 2)) * h * disc(T + h / 2); T += h
        return acc
    T = 7.5; h = 0.001
    while T < cap:
        acc += lam * math.exp(-lam * (T + h / 2)) * h * disc(T + h / 2); T += h
    return acc + math.exp(-lam * cap) * disc(cap)
E_inv = inv * (0.5 * E_disc(10.5) + 0.5 * E_disc(None))

pv = 53.844 * 0.95 * 0.94 * (1 + r) ** -0.13 + E_ebit(2027) * 0.893 * (1 + r) ** -0.63
y, e = 2028, None
while y <= 2045:
    t = 0.05 if y <= 2030 else (0.10 if y <= 2032 else 0.20)
    e = E_ebit(y) * (1 + g) ** (y - 2028)
    pv += e * (1 - t) * 0.94 * (1 + r) ** -(1.63 + y - 2028)
    y += 1
pv += e * (1 + g) * 0.8 * 0.94 / (r - g) * (1 + r) ** -(1.63 + 2045 - 2028)
indep = (pv + cash + E_inv) / 25 * 1000
tree = json.load(open('model_out_r4.json'))['center']
d = indep / tree - 1
print(f"TAM cay {tree:,.1f} | duong doc lap {indep:,.1f} | lech {100*d:+.4f}%  => {'DAT' if abs(d) < 0.005 else 'KHONG DAT'} (<0,5%)")
print(f"kiem: E_p {E_p:.5f} E_f {E_f:.5f} fr {fr:.6f} E_nvl 2027 {E_nvl(2027):.4f} 2028 {E_nvl(2028):.4f} 2045 {E_nvl(2045):.4f} cash {cash:.3f} E_inv {E_inv:.3f} ebit27 {E_ebit(2027):.2f}")
