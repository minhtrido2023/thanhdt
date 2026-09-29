"""Gan nhan theo LUAT §3/§4 da khoa trong PREREG.md (khong sua ngưỡng), roi chay phep kiem tach nhom §5.
Nhan dinh tinh (A) lay tu bang tin tuc vi mo da tra o README §2 — ghi TAY o day, co nguon."""
import pandas as pd, numpy as np, sys
D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_mechanism_classifier_20260823"
E = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"

arm  = pd.read_csv(f"{D}/earnings_basket.csv")
trg  = pd.read_csv(f"{D}/earnings_basket_trough.csv")
ep   = pd.read_csv(f"{E}/episodes_dd52.csv")
stk  = pd.read_csv(f"{E}/trough_stock_forward.csv")

# --- bang chung A: nhan dinh tinh, tra bang WebSearch (nguon liet ke trong README §2)
A = {  # episode -> (nhan A, ly do ngan)
 "2007-04": ("MIXED",              "2007: Chi thi 03 siet cho vay CK (chinh sach) + xa bong bong; 2008: CPI ~28%, SBV nang lai suat co ban 7,5%->13-14% + du tru bat buoc + tin phieu bat buoc (chinh sach) DONG THOI GFC lam giam cau xuat khau + BDS dong bang -40%, DN khong ban duoc hang (thuc)"),
 "2009-11": ("LIQUIDITY_POLICY",   "IMF Art IV 2010: 11/2009 SBV nang lai suat chinh sach +100bp, pha gia VND 5,4%, cham dut goi cap bu lai suat 4pp -> cu soc CHINH SACH tien te thuan tuy, khong phai thu nhap DN"),
 "2011-05": ("FUNDAMENTAL_REAL",   "Nghi quyet 11 (24/02/2011) siet tin dung <20%, cat tin dung BDS/CK; lai suat vay 20-25%; BDS dong bang -> no xau he thong NH bung 2012. Toi 05/2011 cu soc DA vao doanh thu/bien LN/no xau"),
 "2012-08": ("LIQUIDITY_POLICY",   "21/08/2012 bat bau Kien (ACB) -> rut tien hang loat tai ACB, SBV bom 17.000 ty VND lien NH; HNX -5,24% ngay cong bo, TT -9,2% trong tuan. KICH HOAT la bank-run, KHONG phai bao cao KQKD"),
 "2018-05": ("LIQUIDITY_POLICY",   "Khoi ngoai rut khoi EM + margin call sau nhip tang 48% (2017) va +22% toi dinh 09/04/2018; chien tranh thuong mai My-Trung + Fed nang lai suat. Cu soc DONG VON/dinh gia, khong co khung hoang NH hay suy giam LN trong nuoc"),
 "2020-03": ("LIQUIDITY_POLICY",   "Dai dich COVID-19 — cu soc NGOAI he thong tai chinh theo dung dinh nghia §1, keo theo noi long tien te toan cau quy mo lon"),
 "2022-05": ("LIQUIDITY_POLICY",   "Bat Trinh Van Quyet (03/2022) + huy lo trai phieu Tan Hoang Minh (04/2022) + bat Truong My Lan/Van Thinh Phat (10/2022) -> rut tien hang loat tai SCB (SBV bom tien); SBV nang lai suat +200bp T9/T10 chong ap luc ty gia (Fed +425bp); thi truong trai phieu DN DONG BANG; margin call day"),
}

rows = []
for _, r in arm.iterrows():
    e = r["ep"]
    a_lab, a_why = A[e]
    t = trg[trg.ep == e].iloc[0]
    out = []
    for tag, src in [("arm", r), ("trough", t)]:
        m2 = src["m2_ratio_k4"]; roe0 = src["m1_roe_q0"]; roe4 = src["m1_roe_q4"]
        n   = int(src["n_np0"])
        roe_drop = 1 - roe4/roe0 if roe0 > 0 else np.nan
        if n < 30:
            b = "KHONG_KET_LUAN(n<30)"
        elif (m2 <= 0.80) or (roe_drop >= 1/3):
            b = "FUNDAMENTAL_REAL"
        elif (m2 >= 0.95) and (roe_drop < 1/3):
            b = "LIQUIDITY_POLICY"
        else:
            b = "KHONG_KET_LUAN(vung giua)"
        out.append((b, m2, roe_drop, n))
    b_arm, b_trg = out[0][0], out[1][0]
    # §4: nhan cuoi cung dua tren bang chung B PRE-DECLARED = neo tai ARM
    if b_arm.startswith("KHONG_KET_LUAN"):
        final = a_lab if a_lab != "MIXED" else "AMBIGUOUS"
        flag  = "(chi-dinh-tinh)"
    elif a_lab == "MIXED" or a_lab != b_arm:
        final, flag = "AMBIGUOUS", f"(A={a_lab} vs B={b_arm})"
    else:
        final, flag = a_lab, ""
    er = ep[ep.episode == e].iloc[0]
    sr = stk[stk.trough == er["trough_date"]].iloc[0]
    rows.append(dict(episode=e, arm=er["arm_date"], trough=er["trough_date"],
        A=a_lab, B_arm=b_arm, B_trough=b_trg,
        m2_k4_arm=round(out[0][1],3), roe_drop_arm=round(out[0][2],3), n_arm=out[0][3],
        m2_k4_trough=round(out[1][1],3), roe_drop_trough=round(out[1][2],3), n_trough=out[1][3],
        NHAN=final, co=flag,
        med12_stock=sr["med12"], vni_fwd12_arm=er["fwd12_arm"], vni_fwd12_trough=er["fwd12_trough"],
        why_A=a_why))
res = pd.DataFrame(rows)
res.to_csv(f"{D}/classification.csv", index=False)
pd.set_option("display.width", 300, "display.max_columns", 40)
print(res[["episode","arm","trough","A","B_arm","B_trough","m2_k4_arm","roe_drop_arm","n_arm",
           "m2_k4_trough","roe_drop_trough","NHAN","co","med12_stock","vni_fwd12_arm"]].to_string(index=False))

# ---- §5 phep kiem TACH HOAN TOAN (chi nhan sach, loai AMBIGUOUS)
print("\n=== §5 PHEP KIEM TACH NHOM (chi nhan sach) ===")
for metric in ["med12_stock", "vni_fwd12_arm"]:
    L = res[res.NHAN == "LIQUIDITY_POLICY"][["episode", metric]]
    F = res[res.NHAN == "FUNDAMENTAL_REAL"][["episode", metric]]
    amb = list(res[res.NHAN == "AMBIGUOUS"].episode)
    print(f"\n-- {metric}: LIQ={dict(zip(L.episode,L[metric]))} | FUND={dict(zip(F.episode,F[metric]))} | AMBIGUOUS(loai)={amb}")
    if len(L) and len(F):
        ok = L[metric].min() > F[metric].max()
        print(f"   min(LIQ)={L[metric].min():+.3f} vs max(FUND)={F[metric].max():+.3f} -> TACH HOAN TOAN: {'CO' if ok else 'KHONG'}")
        viol = L[L[metric] <= F[metric].max()]
        print(f"   so episode LIQ di NGUOC gia thuyet (<= max FUND): {len(viol)} -> {list(viol.episode)}")

# ---- mo ta them (KHONG p-value, N=7 theo §6.1)
sub = res.dropna(subset=["m2_k4_trough","med12_stock"])
rho = sub["m2_k4_trough"].rank().corr(sub["med12_stock"].rank())
print(f"\nSpearman rho (M2 k=4 neo tai DAY  vs  median co phieu fwd-12m) = {rho:.3f}  [N=7, MO TA, KHONG p-value]")
