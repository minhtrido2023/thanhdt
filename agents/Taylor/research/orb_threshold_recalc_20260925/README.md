# orb_intraday — tinh lai nguong N tren effect size HOP NHAT

Job `Taylor_20260925_120926`. PAPER-ONLY, khong cham tien that, khong doi tham so chien luoc.
Input: `../orb_fiinx_vn30f1m_20260925/orb_trades_extended_20220217_20260925.csv` (1.129 trade,
2022-02-17..2026-09-25, tape ghep FiinX + vnstock, config DANG DEPLOY, exit 14:29).

## 0. So do tren mau ghep (tinh lai tu CSV, khong chep tay)

| | |
|---|---|
| n | 1.129 trade |
| mean | **+6,16 bps/phien** |
| sd | **110,22 bps** (khong phai 110 lam tron — 110,22) |
| skew / kurtosis (khong tru 3) | −0,364 / 12,10 |
| SR/obs | 0,05592 → Sharpe nam **0,888** |
| t | **+1,879** |
| bootstrap 20k, CI95 cua mean | **[−0,20 ; +12,55] bps** — CI **cham 0** |
| P(mean ≤ 0) | 0,029 |

## 1. N can — so CU vs so MOI

Quy uoc CU (job `Taylor_20260925_103217` §5): `N = (t* · sd/mean)²` — tuc N de t-stat KY VONG
cham nguong. **Day la power 50%, khong phai 80%** (dung dung nghia: neu effect size that dung
bang uoc luong, thi 50% kha nang mau se cho t ≥ t*). Bang duoi giu ca hai quy uoc de so sanh
tao-tao, roi bo sung power 80% that.

| Tieu chi | effect CU (+9,06bps, sd 93,6) | effect HOP NHAT (+6,16bps, sd 110,2) | he so |
|---|---|---|---|
| t = 1,64 (power 50%) | **287** | **860** (3,4 nam) | ×3,0 |
| t = 2,00 (power 50%) | **427** | **1.279** (5,1 nam) | ×3,0 |
| power 80%, alpha 5% MOT phia | 660 | **1.977** (7,8 nam) | ×3,0 |
| power 80%, alpha 5% HAI phia | 838 | **2.510** (10,0 nam) | ×3,0 |

He so ×3,0 den tu hai nguon nhan nhau: mean giam 1,47× **va** sd tang 1,18× ⇒ (1,47×1,18)² ≈ 3,0.

⚠️ **N o day la TONG so quan sat, khong phai so phien paper forward.** Mau ghep da co 1.129.
Neu tinh "1.129 da co + tich luy them" thi con thieu **1.381 phien ≈ 5,5 nam** (power 80% hai
phia). Neu doi hoi rieng cua so forward phai tu no du power (cach doc chat hon, vi cua so cu
khong phai OOS) thi la **1.977 phien ≈ 7,8 nam**.

## 2. DSR — cau hoi quan trong hon, va cau tra loi la KHONG KHA THI

Giu nguyen SR/obs = 0,05592 da do (tuc gia dinh tuong lai lap lai DUNG chat luong trung binh
cua qua khu ghep, gom ca doan vnstock tot), chi tang n. Cong thuc DSR y het `analyse.py` cua
job `_111203` (Bailey–López de Prado; SR0 = E[max SR] voi N_trials, xap xi sd giua trial = 1/√n).

| n | DSR(N_trials=20) |
|---|---|
| **1.129 (hien tai)** | **0,491** |
| 1.500 | 0,603 |
| 2.000 | 0,723 |
| 2.500 | 0,811 |
| 3.000 | 0,874 |
| 4.000 | 0,947 |
| **4.075** | **0,950** ← nguong fleet |
| 5.000 | 0,979 |

**N can de DSR tu no vuot 0,95: 4.075 phien** (N_trials=12 → 3.554; N_trials=40 → 4.761).
= **16,2 nam** giao dich. Da co 1.129 ⇒ con thieu **2.946 phien ≈ 11,7 nam**.

### Diem quyet dinh: con so nay LON HON CA DOI SONG CUA HOP DONG

VN30F1M ra doi **2017-08-10**. Tinh den 2026-09-25 la **9,13 nam ≈ 2.300 phien**. Tuc la:

> **Neu co bar 1 phut cho TOAN BO lich su VN30F1M — khong thieu 2018, khong thieu COVID 2020,
> khong thieu gi ca — DSR(N=20) cung chi len toi 0,779. Van duoi 0,95.**

Nguong 0,95 khong dat duoc bang cach cho them du lieu, o effect size nay. Khong phai "lau",
ma la **vuot qua so du lieu ma thi truong nay ton tai de tao ra**.

### Nguoc lai: can EDGE bao nhieu thi moi kha thi?

| Neu co n phien | SR/obs can | = mean | = Sharpe nam | so voi da do |
|---|---|---|---|---|
| 1.129 (ngay hom nay) | 0,1073 | +11,82 bps | 1,70 | **×1,92** |
| 2.000 | 0,0801 | +8,83 bps | 1,27 | ×1,43 |
| 2.300 (toan bo doi hop dong) | 0,0747 | +8,23 bps | 1,19 | ×1,34 |

⇒ Duong ra kha thi la **edge manh gan gap doi**, khong phai **N gap bon**.

### Kiem chung nguoc (de thay con so nhay cam den muc nao)

Neu effect size that la con so CU (+9,06bps / sd 93,6 ⇒ SR/obs 0,0968), DSR(N=20) = 0,95 chi
can **1.381 phien** — tuc dang le da gan dat. Chenh 1.381 vs 4.075 (×2,95) chi vi SR/obs doi tu
0,0968 xuong 0,0559. **DSR sieu nhay voi effect size**, va effect size lai chinh la thu ta khong
do duoc chac (CI95 cua mean cham 0, va khac biet 2 doan p=0,266 — khong phan biet duoc).

## 3. Doc ket qua the nao — 3 dieu KHONG duoc noi qua

1. **KHONG duoc noi "regime da doi nen edge mat".** Welch p=0,266 (job `_111203` §4). Ca hai
   doan van tuong thich voi mot effect size chung; chi la uoc luong chung thap hon va CI rong hon.
2. **KHONG duoc noi "DSR se khong bao gio dat".** Bang tren gia dinh SR/obs tuong lai = SR/obs
   qua khu ghep. Neu doan tiep theo giong doan vnstock (+9,13bps) thi duong DSR doc hon nhieu.
   Menh de dung la: **theo uoc luong tot nhat hien co**, N can vuot qua doi song cua hop dong.
3. **Con so 4.075 khong phai muc tieu can theo duoi.** No la phep do cho thay "tich luy them N"
   da het la mot chien luoc nghien cuu hop ly cho bai nay — khong phai mot ke hoach 16 nam.

## File
- `recalc.py` / `recalc_result.json` — power + DSR solve
- `recalc2.py` / `recalc2_result.json` — kha thi so voi doi song hop dong + edge can co

Chay lai: `/home/trido/thanhdt/wc_venv/bin/python recalc.py` (system python3 thieu scipy).
