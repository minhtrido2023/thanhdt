# BUOC D — xac nhan tang ENGINE THAT cho margin/Kelly trong washout CAPIT

**Job**: `Taylor_20260803_101341` · **Ngay**: 2026-08-03 · **Trang thai**: RESEARCH-ONLY, production KHONG bi sua
**Artifact**: `mike/agents/Taylor/exp_margin_kelly/p5_engine/` (script + CSV + log, chay lai duoc)
**Chuoi truoc**: p1 `Taylor_20260803_070954` · p2 `_073714` · p3 `_082141` · plan `_082241` · p4-proxy `_091342`
(verify `mike/logs/verify_20260803_094213.log`, CONFIRMED-medium)

---

## 0. Ket luan mot doan

Lan nay **don bay THAT SU duoc kich hoat** (khac p2, noi engine chi vay 5-9% vi no uu tien tieu tien mat
co san): tai f=1,3 engine giu du no **dong thoi** dinh cao **30,55 ty tren so sach 50 ty**, **835 ngay**
co du no, lai vay thuc tra 4,48 ty. Va **ca 4 cong G-D deu PASS** o ca lai suat BASE 12,5%/nam lan adversarial
14%/nam: ΔCAGR duong o ca IS lan OOS, ΔMaxDD chi xau **0,07-0,13pp** (ngan sach 1,0pp), DSR 1,0000,
PBO 0,10-0,14 (< 0,5), va **khong su kien nao ganh ≥50% edge** (nang nhat 18,7%).

**Nhung day KHONG phai de xuat wire**, va ly do quan trong hon con so: **muc loi ich that su nho hon
nhieu lan so voi tang proxy p4 da bao** — p4 noi +1,82pp o f=1,3, engine do duoc **+0,663pp**. Toi da
truy ra co che va no **khong phai** "edge bien mat", ma la **pha loang**: don bay chi nhan len phan von
ma may thuc su dat vao washout, trung binh **0,272 NAV-book**, tren **1 trong 2 book**. Chi tiet §4.

Ngoai ra p4 da bao ΔMaxDD **xau +0,83pp** (va f=1,5 FAIL vi +1,49pp). Engine do duoc ΔMaxDD **xau
0,067pp** o f=1,3 va f=1,5 **PASS**. Hai tang lech nhau ca chieu loi lan chieu hai — nghia la **tang
proxy khong dang tin theo ca hai huong**, khong chi "bi quan an toan". §5 noi ro.

---

## 1. CAU 1 — vay bao nhieu, bang SO THAT

Nguon: ledger `*_leveraudit.csv` + `*_borrowledger.csv` do chinh engine ghi. Script `cau1_borrow_table.py`,
bang day du `cau1_borrow.log` + `cau1_summary.csv`.

### 1.1 Mot loi tinh toan toi da mac va da sua — phai doc truoc khi dung bang

Ban dau toi quy doi sang quy mo SpaceX bang he so `NAV_live / 50e9`. **Do la sai.** 50 ty la NAV **luc
bat dau** backtest; so sach tang len 1.178 ty vao cuoi ky. Nhan kieu do cho ra ket qua vo ly: khoan vay
2023-10-30 thanh **1.664 trieu VND tren mot tai khoan chi co 938 trieu**. Quy doi dung = **ty le vay/NAV
tai chinh ngay do**, roi nhan voi NAV song hom nay. Bang duoi da dung cach dung.

### 1.2 Bang vay tung su kien — f = 1,3, lai vay 12,5%/nam (`E125_f13`)

NAV SpaceX song = **938.435.711 VND** (`nav_history_SpaceX.csv`, 2026-07-31, doc song khong ghi cung).

| Su kien | NAV so sach | Vi the CAPIT | VAY (luc do) | vay/NAV | **VAY neu ap dung HOM NAY** |
|---|---:|---:|---:|---:|---:|
| 2014-05-08 | 51,9B | 58,3B | 13,5B | **25,9%** | **243,5tr** |
| 2015-08-24 | 82,9B | 4,1B | 0,9B | 1,1% | 10,7tr |
| 2016-01-18 | 85,3B | 23,6B | 5,5B | 6,4% | 60,0tr |
| 2018-05-28 | 144,5B | 29,1B | 6,7B | 4,7% | 43,6tr |
| 2018-07-05 | 135,6B | 19,8B | 4,6B | 3,4% | 31,6tr |
| 2020-02-03 | 190,5B | 31,3B | 7,2B | 3,8% | 35,6tr |
| 2020-03-11 | 185,0B | 42,8B | 9,9B | 5,3% | 50,1tr |
| 2020-07-27 | 164,5B | 8,7B | 2,0B | 1,2% | 11,5tr |
| 2022-06-15 | 534,8B | 173,8B | 40,1B | 7,5% | 70,4tr |
| 2023-10-30 | 574,5B | 384,3B | 88,7B | 15,4% | 144,9tr |
| 2024-04-17 | 667,8B | 219,9B | 50,7B | 7,6% | 71,3tr |
| 2024-08-05 | 735,2B | 229,7B | 53,0B | 7,2% | 67,7tr |
| 2025-04-03 | 841,5B | 312,5B | 72,1B | 8,6% | 80,4tr |
| 2025-10-20 | 1.182,9B | 160,2B | 37,0B | 3,1% | 29,3tr |
| 2026-03-09 | 1.200,2B | 16,1B | 3,7B | 0,3% | 2,9tr |

**Nang nhat 25,9% NAV = 243,5tr VND. Trung binh moi dot 6,8% NAV = 63,6tr VND.**

### 1.3 Ba muc f — con so live de user can nhac

| f | vay nang nhat (%NAV) | **live** | TB moi dot | **live** | lai vay ca ky (50B) | du no dong thoi dinh cao | ngay co du no |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1,1 | 8,6% | **81,2tr** | 2,3% | **21,2tr** | 1,71B | 10,34B | 835 |
| 1,2 | 17,3% | **162,3tr** | 4,5% | **42,3tr** | 3,06B | 20,38B | 835 |
| 1,3 | 25,9% | **243,5tr** | 6,8% | **63,6tr** | 4,48B | **30,55B** | 835 |
| 1,5 | 43,2% | **405,9tr** | 11,3% | **105,7tr** | 6,94B | 50,73B | 835 |

> **Canh bao bat buoc doc kem** (khong duoc bo khi trich): con so live la **CAN DUOI**. Chinh sach khong
> bat bien theo quy mo — (a) tran %ADV cua ro CAPIT chi chan o quy mo LON, o 938tr thi khong chan, nen
> ban live se vay **nhieu hon** ty le; (b) SpaceX hien ~98,5% da dau tu (p1 §5) trong khi so sach 50B
> luon con tien nhan. Ca hai deu day so live LEN.

---

## 2. Thuc thi ky thuat — da vá dung lo hong p2

p2 (VIEC 1) chi ro `MGE_CAPIT_ONLY=1 FORCE_REAL_LEVER=1` chi dat 5-9% vay that vi engine uu tien tieu
tien mat/parking nhan roi. BUOC D them knob **`CAPIT_LEVER_FORCE=f`** vao **ban sao nghien cuu**
(`p5_engine/engine_lever.py` = `p3/engine_park.py` + hunk; `p5_engine/shn_lever.py` =
`simulate_holistic_nav.py` + hunk). Phan tang them duoc khai bao la **no THEO DINH NGHIA** — shn_lever
tinh vay tren `(f-1)/f` cost-basis cua ro CAPIT moi phien giu, **khong kiem tra con tien mat hay khong**.

Chong tinh 2 lan: `_fb_extra = max(0, notional − native_neg_cash) × rate/252` — chi tinh **phan chenh**
ngoai phan lai engine da tu tru tren tien mat am.

**Bang chung don bay lan nay la THAT** (khac p2): du no **dong thoi** dinh cao **30,55B/50B** so sach,
**835 ngay** co du no, 113 phien tien mat am tu nhien. p2 chua bao gio vuot gross 1,000.

> **DINH CHINH (quant-skeptic `verify_20260803_111110`, da xac nhan doc lap va SUA).** Ban dau toi ghi
> **44,5B / 1.435 phien**. Ca hai **SAI**, va sai o chinh dong `print` cua engine: no lay
> `max(BAL)+max(LAG)` va `len(BAL)+len(LAG)`. Nhung **2 dinh roi vao 2 ngay khac nhau** (BAL 18,35B
> ngay 2024-08-12; LAG 26,12B ngay 2024-04-25) nen 44,5B la muc du no **chua bao gio dong thoi ton tai**;
> va 600 ngay co ca 2 book cung no bi dem 2 lan. Sau khi **gop theo ngay roi moi max()/dem ngay duy nhat**:
> **30,55B (2025-10-28) va 835 ngay** — thap hon 31% va 42%. Da sua `engine_lever.py` (`_fb_peak`/`_fb_days`)
> va `cau1_borrow_table.py`; so moi tai lap dung con so quant-skeptic tu tinh doc lap.
> **Ket luan dinh tinh khong doi** (30,55B/50B van la don bay that, xa han p2 gan-nhu-bang-0), nhung
> **khong duoc trich lai con so 44,5B/1.435 o bat ky dau.**
>
> Kiem tra lan 2 theo khuyen nghi cua quant-skeptic: bang per-event §1.2/§1.3 **KHONG dinh loi nay** —
> no cong `loan_vnd` cua BAL+LAG trong **cung 1 ngay su kien** (30 dong = 15 ngay × 2 book, da xac minh),
> tuc phoi nhiem dong thoi that. Da kiem chung tuong minh, khong suy doan.

**Kiem tra tinh trung thuc cua ban sao:**
- Chan control `D0_control` (f=1, knob tat) **tai lap TUYET DOI pin R3**: CAGR 28,8627% / MaxDD −17,7851% /
  Calmar 1,6229 / NAV cuoi 1.178,0099B / IS 27,0925% / OOS 30,4786%.
- **Self-check 0 VND** ca 2 book tren ca 6 chan (`cash-flow identity max err = 0 VND`).
- **Kiem tra INERT** cua knob LOO them sau: `INERT_f13` vs `E125_f13` lech **0,00 VND tren 3.107 phien**.

---

## 3. CAU 2 — vi sao co su kien LO, phan loai bang so

### 3.1 Phat hien quan trong nhat: engine chi lever **15/17** su kien

Hai su kien timing xau nhat cua bo 17 — **2022-04-19 (r=−13,20%)** va **2022-09-28 (r=−12,35%)** —
**production TU CHOI MUA**, doc thang tu log chan control:

```
[postbull] 2022-04-19 ret2y=+83% dd1y=-8% -> post-strong-bull + shallow -> size x0.00 (1.00->0.00)
washout 2022-04-19: state=1 grind=False dd52=-8.0% cool=False -> size=0.00
washout 2022-09-28: state=2 grind=True  dd52=-25.2% cool=False -> size=0.00
```

Day **KHONG phai artifact do toi tao ra**: chan control (f=1) bo dung 2 su kien do, y het. Cong
`postbull` + cong BEAR/grind cua production da lam viec cua no. Hau qua: **bo 17 su kien cua tang sleeve
va bo 15 su kien cua tang engine KHONG so sanh truc tiep duoc** — va do la mot phan cau tra loi CAU 3.

### 3.2 Bang phan ra per-event tang ENGINE (f=1,3 @ 12,5%)

Script `cau2_engine_decomp.py`, log `cau2_engine.log`, CSV `cau2_engine_<leg>.csv`.
Don vi = diem log tren toan chuoi NAV.

| Su kien | VAY (tr) | (a) thi truong/timing | (b) carry | (c) drag/tuong tac | = rong | Loai |
|---|---:|---:|---:|---:|---:|---|
| 2014-05-08 | 13.460 | +5,504% | −0,283% | −2,445% | **+2,776%** | duong |
| 2015-08-24 | 943 | +0,189% | −0,030% | +0,037% | +0,196% | duong |
| 2016-01-18 | 5.455 | +1,242% | −0,086% | −1,269% | −0,113% | CARRY |
| 2018-05-28 | 6.721 | +0,882% | −0,082% | −0,776% | +0,025% | duong |
| 2018-07-05 | 4.565 | +1,283% | −0,020% | −1,185% | +0,077% | duong |
| 2020-02-03 | 7.222 | −0,116% | −0,079% | +0,268% | +0,073% | **TIMING** |
| 2020-03-11 | 9.881 | −0,009% | −0,005% | −0,154% | −0,169% | **TIMING** |
| 2020-07-27 | 2.010 | +0,340% | −0,028% | −0,607% | −0,295% | CARRY |
| 2022-06-15 | 40.113 | +0,208% | −0,119% | −0,345% | −0,256% | CARRY |
| 2023-10-30 | 88.677 | +2,993% | −0,033% | −2,939% | +0,022% | duong |
| 2024-04-17 | 50.740 | +1,265% | −0,085% | −1,813% | −0,633% | CARRY |
| 2024-08-05 | 53.016 | +0,383% | −0,061% | −0,369% | −0,046% | CARRY |
| 2025-04-03 | 72.119 | +1,785% | −0,049% | −2,001% | −0,265% | CARRY |
| 2025-10-20 | 36.968 | +0,191% | −0,069% | +0,579% | +0,701% | duong |
| 2026-03-09 | 3.724 | −0,007% | −0,008% | +0,828% | +0,813% | **TIMING** |
| **TONG trong cua so** | | **+16,133%** | **−1,037%** | **−12,190%** | **+2,906%** | |
| **(d) NGOAI cua so (tuong quan ca so)** | | | | | **+3,492%** | |

**KIEM TRA ARITHMETIC BAT BUOC (yeu cau cua dispatch):**
- Dong nhat thuc: tong 4 cot = `+0,0639832588`; ΔlogNAV do truc tiep tu 2 chuoi = `+0,0639832588`;
  **lech = +1,39e−17 → KHOP**.
- Doi chieu headline: ΔCAGR do truc tiep = **+0,6634pp**; ΔCAGR dung lai **tu tong 4 cot** = **+0,6634pp**;
  **lech = +3,8e−15pp → KHOP**.
  (Cong thuc dung: `ΔCAGR = (1+CAGR_ctl)·(exp(Δlog/yrs)−1)`, **khong phai** `exp(Δlog/yrs)−1` — toi da
  dung nham cong thuc sau o ban dau, no lech ~0,14pp.)

### 3.3 Phan loai theo dung 5 muc dispatch yeu cau

- **(a) Chon sai thoi diem** — 3/15 su kien (2020-02-03, 2020-03-11, 2026-03-09) co cot (a) am, tuc
  **da lo ngay ca khi khong don bay**; don bay chi khuyech dai. Tong dong gop (a) am = −0,132%, **rat nho**.
  Ly do nho: 2 su kien timing te nhat da bi production loai truoc do (§3.1).
- **(b) Chi phi vay** — **−1,037%** tong (12,5%/nam), len **−1,162%** o 14%/nam. 6/15 su kien lai o (a)
  nhung **rong am sau khi tru carry+drag**. Day la nhom LON NHAT trong cac su kien am.
- **(c) Phat compounding / volatility drag** — **−12,190%**, tuc **lon gap 12 lan carry**. Do rieng o tang
  sleeve (`cau2_decomp.log`, muc "CAU 2(c)"): CAGR naive tu trung binh so hoc vs CAGR that tu compounding
  chenh **1,84pp (f=1,0) → 3,06pp (f=1,3) → 4,04pp (f=1,5)**, tang **phi tuyen** dung nhu `~f²·Var/2`.
  **Day chinh la cau tra loi cho "tai sao xac suat thang cao ma ket qua khong cao tuong xung".**
- **(d) Tuong quan voi ca so** — **+3,492%**, tuc **+54,6% cua tong edge nam NGOAI cua so nam giu**.
  Doc dung: khi mot dot levered thang, NAV so sach cao hon **vinh vien** va nen cao do compound tiep cho
  phan con lai cua mau. Day la loi ich THAT nhung **phu thuoc duong di** — nen phai kiem bang LOO su kien
  (§3.4), khong duoc nhan la edge on dinh.
- **(e) Hien vat do luong/engine** — **da vá**, khong con: p2 do sai vi engine tieu tien mat truoc khi vay;
  BUOC D ep vay theo dinh nghia (§2). Loi do luong con lai duy nhat toi tim thay la **loi cua chinh toi o
  CAU 1** (he so quy doi live), da sua va ghi lai o §1.1.

### 3.4 LOO theo SU KIEN — dong lo hong p3 §4.2

p3 da chung minh LOO **theo nam** la ao anh trong he compounding. Toi chay LOO **theo su kien** o tang
engine (5 chan rieng, moi chan tat don bay o dung 1 su kien). Script `loo_event_p5.py`.

| Bo su kien | ΔCAGR con lai | % edge mat | ΔOOS | Ket luan |
|---|---:|---:|---:|---|
| E0 2014-05-08 (dot dau, vay nang nhat) | +0,5391pp | **18,7%** | +0,8334pp | phan tan |
| E12 2023-10-30 (vay tuyet doi lon nhat) | +0,6709pp | −1,1% | +0,8468pp | phan tan |
| E14 2024-08-05 (r_i am) | +0,6634pp | 0,0% | +0,8321pp | phan tan |
| E16 2025-10-20 (r_i +33,8%) | +0,5507pp | 17,0% | +0,6119pp | phan tan |
| E17 2026-03-09 (gan cuoi mau) | +0,6650pp | −0,2% | +0,8352pp | phan tan |

**Khong su kien nao ganh ≥50% edge; nang nhat 18,7%.** Bay "1 dot ganh het" cua p3 **khong lap lai** o day.

---

## 4. CAU 3 — "chon dung, xac suat ro rang thi ket qua khong the thap"

Script `cau3_mechanism.py`, log `cau3_mechanism.log`, CSV `cau3_mechanism.csv`.

### 4.1 Menh de cua user, kiem bang chinh cong thuc Kelly: **DUNG**

Tren **15 su kien engine THUC SU mua** (khong phai 17 gia dinh), thong ke con **tot hon** so dispatch neu:

| | N | %duong | TB | Trung vi | Do lech chuan |
|---|---:|---:|---:|---:|---:|
| Bo 17 (gia dinh mua het) | 17 | 64,7% | +9,75% | — | — |
| **Bo 15 (engine thuc mua)** | **15** | **86,7%** | **+16,28%** | +15,27% | 15,70% |

`g(f) = E[log(1+f·r)]`: 0,14277 (f=1) → 0,17951 (f=1,3) → 0,20279 (f=1,5), **don dieu tang**, `f*` cham
bien tren cua luoi (**6,0**). **Vay o tang su kien, menh de cua user hoan toan dung** — voi xac suat
thang 86,7% va TB +16,28%, don bay f≤1,5 **con xa** muc Kelly toi uu, khong he qua tay.

### 4.2 Nhung toan-so chi duoc +0,663pp — **co che lam mat loi the la PHA LOANG, khong phai mat edge**

Day la cau tra loi trung tam ma dispatch doi hoi. Toi kiem dinh gia thuyet **H1**: *"cac su kien r_i cao
roi vao luc danh muc gan het tien, nen don bay nhan len vi the nho"*.

| Su kien | size gate | tien mat con | wt engine DAT | r_i tho |
|---|---:|---:|---:|---:|
| 2018-07-05 | 0,375 | 0,2993 | 0,1122 | **+53,79%** |
| 2025-10-20 | 0,750 | 0,1153 | 0,0865 | **+33,80%** |
| 2020-07-27 | 0,375 | 0,1370 | 0,0514 | +28,88% |
| 2024-04-17 | 0,500 | **0,0242** | **0,0121** | +15,47% |
| 2025-04-03 | 0,500 | **0,0015** | **0,0008** | +3,15% |
| 2026-03-09 | 0,750 | **0,0094** | **0,0070** | +0,62% |

- `corr(r_i , wt engine dat)` = **−0,001** (Pearson), **−0,011** (Spearman).
- TB wt khi r_i tren trung vi = **0,2666**; duoi trung vi = **0,2761**.

**Doc dung**: tuong quan **bang 0**, khong am. Nghia la khong phai "tien luon het dung luc co hoi tot" —
ma la **quy mo vi the hoan toan doc lap voi chat luong co hoi**. May dat trung binh **0,272 NAV-book**
bat ke su kien tot hay xau. Don bay nhan len con so 0,272 do, tren **1 trong 2 book**.

**Doi chieu dinh luong** (kiem dinh co the sai — neu lech nhieu thi co che khac dang chay):

| f | ΔCAGR sleeve | × wt_TB 0,272 × book 0,50 | Du bao | **Do thuc te** | Ty le |
|---|---:|---:|---:|---:|---:|
| 1,1 | +1,52%/nam | | +0,206pp | +0,040pp | 0,19x |
| 1,2 | +3,02%/nam | | +0,410pp | +0,170pp | 0,41x |
| **1,3** | +4,52%/nam | | +0,614pp | **+0,663pp** | **1,08x** |
| **1,5** | +7,49%/nam | | +1,017pp | **+0,920pp** | **0,90x** |

O **f=1,3 va f=1,5, mo hinh pha loang giai thich gan nhu tron ven** khoang cach sleeve → toan-so
(1,08x / 0,90x). **Ket luan: edge KHONG bien mat khi chay qua may — no bi chia cho ~7,4 lan** (0,272 ×
0,50), dung bang ty trong von thuc su chiu don bay.

**Cho toi khong giai thich duoc, noi thang**: o f=1,1 va f=1,2, thuc te chi bang **0,19x / 0,41x** du bao —
tuc con **thap hon ca muc pha loang**. Toi chua truy ra co che cho 2 diem nay; kha nang la nguong lam tron
lo/tran %ADV cat phan tang them nho, nhung **toi chua kiem chung**. Do la mot khoang ho that cua bao cao nay.

### 4.3 Tra loi truc tiep cau hoi cua user

> *"Neu chon dung, xac suat ro rang thi ket qua khong the thap"*

**Ve nguyen ly: dung, va so lieu ung ho manh hon ky vong** (86,7% thang, f* ≈ 6,0 tren sleeve).
**Ve ket qua toan-so: van thap, va ly do khong phai chien luoc sai ma la KENH TRUYEN DAN qua hep.**
Don bay dat len **rieng sleeve CAPIT**, ma sleeve do trung binh chi chiem 27,2% cua 1 book = ~13,6% NAV
tong. Muon loi ich lon hon thi phai **noi rong kenh** (tang ty trong von vao washout), **khong phai tang f** —
va do la mot cau hoi khac han, voi ho rui ro khac han, chua he duoc nghien cuu trong chuoi nay.

---

## 5. Doi chieu voi tang PROXY p4 — hai tang lech nhau ca hai chieu

| | p4 (proxy/overlay) | **p5 (engine that)** | Nhan xet |
|---|---:|---:|---|
| ΔCAGR_FULL f=1,3 | +1,82pp | **+0,663pp** | proxy **thoi phong 2,7x** |
| ΔMaxDD f=1,3 | xau +0,83pp | **xau 0,067pp** | proxy **thoi phong 12x** |
| f=1,5 | **FAIL** (DD +1,49pp) | **PASS** (DD xau 0,056pp) | **ket luan nguoc han** |

Day la **phuong phap doc lap thu ba** ma quant-skeptic doi hoi cho lo hong p4 §4.1 (viec doi cach ke toan
giua chung tu "cong-them" sang "trong cua so", lam lat verdict FAIL→PASS). Engine **khong ton tai lua chon
ke toan do**: no compound NAV native voi so vay that, nen khong co bac tu do nao de chon. Ket qua: engine
**xac nhan huong PASS** cua p4 §4.1, **nhung bac bo do lon** cua ca hai chieu.

**Ham y phai ghi nho**: tang proxy p4 **khong dang tin lam co so quyet dinh**, ke ca khi no to ra bao thu.
Moi ket luan margin tu day ve sau nen do o tang engine.

---

## 6. Cong G-D — doi chieu tung dieu kien

| Cong (§5 plan) | Nguong | Do duoc | Ket qua |
|---|---|---|---|
| ΔCAGR OOS (2020+) duong | > 0 | +0,832pp (f=1,3 @12,5%) / +0,822pp (@14%) | **PASS** |
| ΔCAGR IS duong | > 0 | +0,487pp / +0,470pp | **PASS** |
| ΔMaxDD | ≤ +1,0pp xau | xau 0,067pp (f=1,3) · 0,128pp (f=1,5 @14%) | **PASS** |
| DSR tren config chon | ≥ 0,95 | 1,0000 (N=5, N=25); 0,9999 (N=180) | **PASS** |
| PBO ho {f} | **< 0,5** | 0,100 (S=8) / 0,140 (S=12) / 0,129 (S=16) | **PASS** |
| LOO — 1 su kien ganh ≥50% | khong duoc | nang nhat 18,7% (E0) | **PASS** |
| Margin call | 0 | 0 tren moi chan | **PASS** |
| Self-check 0 VND | bat buoc | 0 VND ca 2 book × 6 chan | **PASS** |
| Control tai lap pin R3 | bat buoc | tuyet doi ca 6 chi tieu | **PASS** |
| Meta-gate trung thuc (12,5% vs 14% nguoc nhau?) | khong duoc nguoc | cung dau, cung do lon | **PASS** |
| quant-skeptic | CONFIRMED | *(xem §8)* | — |

**Do nhay lai suat** (10% / 12,5% / 14%, f=1,3): +0,686 / +0,663 / +0,650pp — **gan nhu phang**, chi phi
vay **khong** phai bien quyet dinh. Tach bien carry truc tiep (`D_f13nc`, carry=0): +0,796pp, tuc carry
"an" 0,11-0,13pp.

---

## 7. Nhung dieu bao cao nay **KHONG** chung minh

1. **Khong phai de xuat wire.** Con thieu **capacity that** (`pp0Buy` SpaceX chua he co ban ghi that,
   p1 §6 — van la gap mo) va **duyet cua user**. Toi khong de xuat bat ky thay doi production nao.
2. **`f*` ≈ 6,0 la cua rieng sleeve va la con so NGUY HIEM neu doc roi ngu canh** — no gia dinh phan phoi
   15 su kien lich su lap lai, khong co margin call, khong co truot gia khi ban thao. Khong duoc trich
   con so nay nhu khuyen nghi.
3. **N = 15 su kien doc lap** — mau nho. DSR/PBO tinh tren NAV daily (3.107 phien) **khong** cai thien
   duoc su that rang bien co goc chi co 15.
4. **Khoang ho toi khong giai thich duoc**: ty le thuc/du bao 0,19x va 0,41x o f=1,1 / f=1,2 (§4.2).
5. **Quy doi live la can duoi**, khong phai uoc luong diem (§1.3).
6. **Lech voi p4 chua duoc hoa giai hoan toan** — toi chi ra engine dang tin hon va giai thich duoc vi sao
   (khong co bac tu do ke toan), nhung **chua truy nguon tung pp** cua khoang cach 2,7x/12x.
7. **Ban dau toi bao sai 2 con so trung tam** (44,5B / 1.435 phien → dung la 30,55B / 835 ngay, §2).
   quant-skeptic bat duoc bang cach tu tinh lai tu chinh CSV toi trich. Bai hoc chung: **cac con so
   "tong hop 2 book" trong ho bao cao nay phai duoc tai tinh truoc khi trich lai**, khong tin dong
   `print` cua engine.

---

## 8. Tai lap

```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/p5_engine
bash run_p5.sh D0_control  CAPIT_LEVER_FORCE=1.0
bash run_p5.sh E125_f13    CAPIT_LEVER_FORCE=1.3 BORROW_ANNUAL=0.125 MGE=1.3 MGE_CAPIT_ONLY=1
bash run_p5.sh E140_f13    CAPIT_LEVER_FORCE=1.3 BORROW_ANNUAL=0.14  MGE=1.3 MGE_CAPIT_ONLY=1
bash run_p5.sh L13e0       CAPIT_LEVER_FORCE=1.3 BORROW_ANNUAL=0.125 MGE=1.3 MGE_CAPIT_ONLY=1 CAPIT_LEVER_LOO=0
$DNA_PYEXE metrics_p5.py ; $DNA_PYEXE cau1_borrow_table.py
$DNA_PYEXE cau2_decomp.py ; $DNA_PYEXE cau2_engine_decomp.py
$DNA_PYEXE cau3_mechanism.py ; $DNA_PYEXE loo_event_p5.py
```

Moi script deu ghi CSV + log canh no. `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`,
`BQ_CACHE_THREADS=1`, `$DNA_PYEXE` (pandas 3) — theo dung lenh pin R3 (coding_guidelines §8).
`EXP_TAG` bat buoc nen khong chan nao de len CSV canonical.

**Production khong bi sua**: `git status` tren `pt_v23_audit_2014.py`, `simulate_holistic_nav.py`,
`macro_state_live.py`, `data/trading_rules.json`, `trading_bot/` — **sach**.

---

## 9. Cong quant-skeptic — **CONFIRMED (medium)**, kem 1 loi that da sua

Log day du: `mike/logs/verify_20260803_111110.log`.

**Da tai lap doc lap (bypass script cua toi, doc thang tu CSV NAV tho):**
- `D0_control` khop pin R3 chinh thuc (doi chieu `data/results_registry.md`), CAGR 28,8627% / 29,5261%,
  Δ = +0,6634pp — **khop den do chinh xac da trich**.
- INERT check 0,00 VND / 3.107 phien; dong nhat thuc 4 cot cua CAU2; he so tuong quan CAU3; toan bo
  delta gate; DSR/PBO — **tat ca tai lap dung**.
- `look_ahead_leak`: **pass** — diff `engine_lever.py` vs `p3/engine_park.py` va `shn_lever.py` vs
  production `simulate_holistic_nav.py` tung dong: hunk chi nhan `wt` (da tinh xong, khong sua) voi
  hang so `f`, va tinh lai tren `cost_basis` **cung ngay**; khong cham cot forward nao.

**Killer objection (DUNG, da sua):** con so "44,5B dinh cao / 1.435 phien" — bang chung chu dao cho
"don bay that su kich hoat" — la **artifact cong 2 book khong dong thoi**. Xem hop DINH CHINH §2.
Con so dung: **30,55B / 835 ngay**. quant-skeptic ghi ro: *"con so da sua van vuot xa ket qua gan-inert
cua p2, nen ket luan dinh tinh 'don bay gio la that' VAN DUNG — nhung con so headline sai 31-42% va
khong duoc trich lai truoc khi sua"*. Toi da sua ca 2 script va bao cao; so moi trung khop voi so
quant-skeptic tu tinh.

**Khuyen nghi #2 cua quant-skeptic — da lam:** kiem tra bang §1.2/§1.3 co dinh cung loi khong.
**Khong dinh** — da xac minh tuong minh (30 dong = 15 ngay × 2 book, cong trong **cung 1 ngay su kien**),
khong suy doan theo cam tinh.

**Vi sao van la CONFIRMED chu khong REFUTED** (nguyen van y quant-skeptic): ket luan gate-PASS va co che
pha loang **duoc kiem chung doc lap voi bang bi loi**; bao cao "bao thu o moi cho khac" — khong de xuat
wire, tu ghi nhan so live la can duoi, tu khai bao khoang ho f=1,1/1,2 thay vi giau di.
