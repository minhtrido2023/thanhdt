"""TCH DD v2 (31/10/2026) — NAV dự án dựng lại theo phản biện.

Chạy: /home/trido/thanhdt/wc_venv/bin/python -I tch_valuation_v2.py > tch_valuation_v2_out.txt
Đầu vào: số BCTC đọc từ ảnh (calc/notes_read.md; BCTC riêng TM9 in 22 kiểm lại 31/10 v2), GAPS.md, BQ.
Mọi tham số NAV là ƯỚC LƯỢNG. Đơn vị: tỷ đồng, đ/cp.

Thay đổi so v1 (tch_valuation.py):
 1. Phần mẹ theo PHÁP NHÂN: Green River/H2/150 Tô Hiệu là HTK công ty mẹ (100%); NC-II + I.14 qua CRV (68,02%).
 2. PV theo Ke báo cáo 12,85% (tâm 12,3–13,4%): backlog NC-II ~1 năm, Green River ~1,5 năm, H2 ~2 năm, HTK còn lại ~4 năm.
 3. Biên ròng sau thuế backlog 30 / 33,5 / 36% (biên gộp 51,9% − CPBH chờ phân bổ 7–12% − thuế 20%).
 4. Tách chiết khấu: holding chỉ áp phần qua công ty con (CRV/HHS); quản trị áp toàn bộ. Bỏ "NCI" khỏi lý do (đã loại khi lấy phần mẹ).
 5. Thặng dư HTK: 15 / 40 / 55% (đối xứng quanh biên lịch sử 51,9% ⇔ s≈70% và quỹ đất mới mỏng hơn) + ma trận.
"""
SH = 1003.312808       # tr cp (TM21d)
PX = 11850             # đóng cửa 30/10/2026
KE = 0.1285            # tâm Ke nội địa 12,3–13,4%
pv = lambda y, ke=KE: 1 / (1 + ke) ** y
VAT = 1.08             # VAT bình quân sau phần đất (ước lượng)
GM = 0.519             # biên gộp BĐS 6T FY26 [TM23/25]

EQ_ME = 15279.65 - 3120.54           # VCSH thuộc cổ đông mẹ 30/09/2026
EQ_DIRECT = 10530.2 - 4571.6         # BCTC riêng: VCSH − đầu tư con thuần (GAPS mục 4)
EQ_SUBS = EQ_ME - EQ_DIRECT          # phần mẹ trong VCSH các công ty con (sổ, hợp nhất)
print(f"VCSH me {EQ_ME:.1f} = truc tiep {EQ_DIRECT:.1f} + qua cong ty con {EQ_SUBS:.1f}")

# NMTT 30/09/2026 [TM16]; HTK BĐS [TM9(*)] hợp nhất; HTK mẹ [RIÊNG TM9 in 22]
proj = {  # name: (NMTT, share, năm tới bàn giao, nhóm)
    "NC-II": (3099.20, 0.6802, 1.0, "sub"),
    "Green River": (1837.75, 1.0, 1.5, "me"),
    "H2": (617.83, 1.0, 2.0, "me"),
    "H1+khac": (38.15 + 6.88, 0.80, 1.0, "sub"),
}
HTK = {"me": 759.57 + 2557.50 + 555.53 + 1677.51 + 1.71,       # 5.551,8: GR TP+CPDD, H2, Tô Hiệu, khác
       "crv": 7390.37 + 1328.75}                                  # NC-II + I.14 (Đại Lộc, qua CRV)
HTK_ALL = 14630.92
HTK["khac"] = HTK_ALL - HTK["me"] - HTK["crv"]
print("HTK BDS: me %.1f | CRV %.1f | khac %.1f" % (HTK["me"], HTK["crv"], HTK["khac"]))
cost_bl = {"me": 0, "crv": 0, "khac": 0}
for k, (n, sh, y, g) in proj.items():
    c = n / VAT * (1 - GM)
    cost_bl["crv" if k == "NC-II" else ("me" if g == "me" else "khac")] += c
rest = {k: HTK[k] - cost_bl[k] for k in HTK}
SHARE = {"me": 1.0, "crv": 0.6802, "khac": 0.80}
print("HTK con lai sau gia von backlog:", {k: round(v, 1) for k, v in rest.items()}, "tong", round(sum(rest.values()), 1))
PV_HTK = pv(4)
print(f"PV he so: 1 nam {pv(1):.3f} | 1,5 nam {pv(1.5):.3f} | 2 nam {pv(2):.3f} | HTK 4 nam {PV_HTK:.3f}")


def nav(m, s, hold, gov, ke=KE):
    """trả (NAV trước CK, NAV sau CK) tỷ đồng, phần mẹ."""
    bl_me = bl_sub = 0.0
    for k, (n, sh, y, g) in proj.items():
        v = n / VAT * m * sh * pv(y, ke)
        if g == "me":
            bl_me += v
        else:
            bl_sub += v
    p4 = pv(4, ke)
    sur_me = rest["me"] * s * SHARE["me"] * p4
    sur_sub = (rest["crv"] * SHARE["crv"] + rest["khac"] * SHARE["khac"]) * s * p4
    direct = EQ_DIRECT + bl_me + sur_me
    subs = EQ_SUBS + bl_sub + sur_sub
    pre = direct + subs
    post = (direct + subs * (1 - hold)) * (1 - gov)
    return pre, post, dict(direct=direct, subs=subs, bl=bl_me + bl_sub, sur=sur_me + sur_sub)


SC = {"tieu cuc": dict(m=0.30, s=0.15, hold=0.30, gov=0.15, p=0.25),
      "co so": dict(m=0.335, s=0.40, hold=0.20, gov=0.10, p=0.50),
      "tich cuc": dict(m=0.36, s=0.55, hold=0.10, gov=0.05, p=0.25)}
res = {}
for k, p in SC.items():
    pre, post, d = nav(p["m"], p["s"], p["hold"], p["gov"])
    res[k] = post / SH * 1000
    print(f"{k}: bien rong backlog {p['m']:.1%}, thang du {p['s']:.0%}, CK holding {p['hold']:.0%} (chi phan qua cty con), CK quan tri {p['gov']:.0%}"
          f" | backlog +{d['bl']:.0f}, thang du +{d['sur']:.0f}; truc tiep {d['direct']:.0f} + qua con {d['subs']:.0f} = truoc CK {pre:.0f}"
          f" ({pre/SH*1000:,.0f} d/cp) -> sau CK {post:.0f} = {res[k]:,.0f} d/cp; CK hieu dung {1-post/pre:.1%}")
w = sum(SC[k]["p"] * res[k] for k in SC)
print(f"Trong so 25/50/25: {w:,.0f} d/cp; gia {PX} lech {PX/w-1:+.1%}")
wb = 0.35 * res["tieu cuc"] + 0.45 * res["co so"] + 0.20 * res["tich cuc"]
print(f"Nghieng theo doc nganh 35/45/20: {wb:,.0f} d/cp; gia lech {PX/wb-1:+.1%}")

print("\nDo nhay Ke (co so):")
for ke in (0.123, 0.1285, 0.134):
    pre, post, _ = nav(0.335, 0.40, 0.20, 0.10, ke)
    print(f"  Ke {ke:.1%}: {post/SH*1000:,.0f} d/cp")

print("\nMa tran: thang du HTK (dong) x chiet khau tong hieu dung (cot) -> d/cp; bien rong backlog 33,5%")
cks = [0, 0.10, 0.15, 0.20, 0.25, 0.30]
rows = []
print("s\\CK  " + "  ".join(f"{c:>6.0%}" for c in cks) + "   | CK ngam dinh trong gia 11.850")
for s in (0.10, 0.25, 0.40, 0.55, 0.70):
    pre, _, _ = nav(0.335, s, 0, 0)
    vals = [pre * (1 - c) / SH * 1000 for c in cks]
    imp = 1 - PX * SH / 1000 / pre
    g = (s + 0.08) / (s + 0.8)
    rows.append((s, g, vals, imp))
    print(f"{s:>4.0%} (bien gop ~{g:.1%}) " + "  ".join(f"{v:>6,.0f}" for v in vals) + f"   | {imp:.1%}")
print("Quy doi thang du sau thue s <-> bien gop g (CPBH 10% DT, thue 20%): s(1-g)=0,8(g-0,1) => g=(s+0,08)/(s+0,8);"
      f" bien gop 51,9% <=> s={0.8 * (0.519 - 0.1) / (1 - 0.519):.1%}")

print("\nNet cash:")
cash_hn = 1035.35 + 2203.19 + 57.78
cash_me = 852.2 + 1392.0
cash_sub = cash_hn - cash_me
cash_share = cash_me + cash_sub * 0.68
print(f"  Tien+HTM HN {cash_hn:.1f} ({cash_hn/SH*1000:,.0f} d/cp); trong do cty me {cash_me:.1f}; phan me uoc {cash_share:.0f} ({cash_share/SH*1000:,.0f} d/cp)")
net = cash_hn - 1086.79 - 198.8
print(f"  Sau no tai chinh (phai tra NB/khac, TM36) 1.086,8 + thue phai nop 198,8: {net:.0f} ty HN ({net/SH*1000:,.0f} d/cp); vay = 0")
print(f"  Sacombank (Sai Gon Tai Loc) 678,32 = {678.32/cash_hn:.0%} tien+HTM HN; 694,23 -> 678,32 (it rut)")

print("\nPhep thu cheo:")
bq_bv = 14481 * 912.109224 / 1000
bq_bvps = bq_bv / SH * 1000
print(f"  P/B cung co so BQ: BV BQ {bq_bv:.0f} ty / {SH:.1f} tr cp = {bq_bvps:,.0f} d/cp; TCH P/B {PX/bq_bvps:.2f} vs trung vi peer 0,72 (+{PX/bq_bvps/0.72-1:.0%}) -> gia tai 0,72x = {0.72*bq_bvps:,.0f}")
crv_np6t = 162.64 / 0.20 * 0.80  # LNST CRV 6T suy tu thue TNDN hien hanh CRV (uoc luong, ETR 20%)
sotp = 5958.7 + 2894.4 + 2380.4
sotp2 = sotp + 0.3819 * crv_np6t
print(f"  SOTP hon hop (GAPS): {sotp:.0f} ty = {sotp/SH*1000:,.0f} d/cp; + 38,19% LNST CRV 6T uoc {crv_np6t:.0f} -> {sotp2:.0f} ty = {sotp2/SH*1000:,.0f} d/cp ({PX/(sotp2/SH*1000)-1:+.1%} gia)")
for lo, hi in ((675, 775),):
    print(f"  P/E chuan hoa 10-16x x EPS {lo}-{hi}: {10*lo:,}-{16*hi:,}; 13x x 729 = {13*729:,}")
print(f"  HHS von hoa 4.082 vs phan HHS trong VCSH CRV ~51,2% x 7.579 = {0.512*7579:.0f} (uoc luong) -> thi truong chiet khau tang HHS")

print("\nKH FY26 (LNST HN 2.000, DT 5.000; NQ26 tr.34 'chi tieu hop nhat'):")
q2_bds = 1954.52 - 203
print(f"  DT BDS Q2 ~{q2_bds:.0f} (6T 1.954,5 - Q1 ~203 [SHS]); DT rieng cty me Q2 chi 57,61 => ~toan bo tu cty con, NC-II ~1.650-1.750 (uoc luong)")
print(f"  NMTT NC-II giam 1.033 (gom VAT) = {1033.03/VAT:.0f} ex-VAT => ~{q2_bds-1033.03/VAT-50:.0f} DT Q2 thu luc ban giao/phai thu (uoc luong)")
print(f"  NMTT NC-II con 3.099 / toc do -1.033/quy = {3099.2/1033.03:.1f} quy")
print(f"  Can H2 FY26: DT {5000-2414:.0f}, LNST HN {2000-914.29:.0f}; neu giu nhip DT BDS ~1.700/quy x LNST/DT Q2 {750.54/1958.18:.1%}: 2 quy ~ {2*1700*750.54/1958.18:.0f}")
