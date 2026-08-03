# Margin/Kelly trong washout CAPIT — PHAN 2: engine-tier cho S4 + "co pattern tao day roi di len khong?"

**Job** `Taylor_20260803_073714` · **Ngay** 2026-08-03 · **RESEARCH-ONLY** (production `git status` sach)
**Noi tiep** `margin_kelly_feardriven_washout_20260803.md` (job `Taylor_20260803_070954`) — dung lai
nguyen bo 26 su kien washout / ro `universe_pit` / dinh nghia `x` cua bao cao do, khong dinh nghia lai gi.

> ## VERDICT NGAN
> **VIEC 1 — S4 o tang portfolio-engine: 🟡 gate GO/NO-GO PASS ve SO, nhung phai doc la KHONG-GO
> cho margin, vi phep do KHONG CHAM TOI don bay.** Ca 3 dieu kien tuong minh deu dat (OOS +0,88pp;
> DSR 1,0000; MaxDD **khong** xau di; LOO 0/13 nam am). Nhung do duoc: **chi 5-9% phan vi the tang
> them la tien VAY that**, 91-95% la **tai phan bo von san co** (parking → CAPIT). Gross **gop chua
> bao gio vuot 1,000**. Tuc la chan nay do "dich them von vao washout sau", **khong** do "vay margin".
> **VIEC 2 — tin hieu "da tao day va dang di len": 🔴 NO-GO, va co pattern that nhung NGUOC chieu.**
> Cang co dau hieu da hoi tai ngay kich hoat thi ket cuc **cang kem** (don dieu). Doi xac nhan roi moi
> vao thi **mat 3,5-4,1pp** loi nhuan tren cung tap su kien, va **khong** giam duoc MAE — phan "giam
> MAE" nhin thay ban dau la **ao anh selection**, khong phai timing.
>
> **Phat hien phu dang gia nhat cua job nay** (khong nam trong 2 cau hoi, khong can vay dong nao):
> **dich them von san co tu parking sang CAPIT o washout sau** = **+0,61pp CAGR**, MaxDD **khong doi**,
> LOO **0/13** nam am. Day moi la thu nen test tiep, chu khong phai margin.

---

## VIEC 1 — S4 (`dd52<=-20%`, don bay CO DINH) o tang PORTFOLIO-ENGINE

### 1.1 Harness + bang chung tai lap

Lenh pin R3 **nguyen van** (`data/results_registry.md`, muc 2026-08-03): `NAV_TOTAL_B=50
ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7"
AUDIT_END=2026-06-19`, snapshot dong cung `data/bq_cache_asof20260729_postrestate`,
`BQ_CACHE_THREADS=1`, `$DNA_PYEXE` (pandas 3), `LAG_ADV_BASIS` de mac dinh (= `price`).

**Engine = BAN SAO NGHIEN CUU** `exp_margin_kelly/p2/engine_dd52.py`. Ly do phai copy: engine **khong
co** cong `dd52` san; dispatch cam sua production. Diff so voi `pt_v23_audit_2014.py` = **3 hunk thuan
THEM**, tat ca inert khi `MGE_GATE != "dd52"`.

| Chan | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | self-check |
|---|---|---|---|---|---|---|---|---|
| **L0 control** (khong bat gi) | **28,86%** | 1,83 | **−17,79%** | **1,62** | **1.178,01B** | **27,09%** | **30,48%** | 0 VND |
| **L1b** MGE 1,3 + cong `dd52<=−20%` | 29,47% | 1,87 | −17,79% | 1,66 | 1.249,14B | 27,42% | 31,35% | 0 VND |
| **L2b** MGE 1,5 + cong `dd52<=−20%` | 29,50% | 1,87 | −17,79% | 1,66 | 1.253,21B | 27,46% | 31,38% | 0 VND |
| X1 MGE 1,3 **khong** cong | 29,66% | 1,87 | −17,84% | 1,66 | 1.271,96B | 27,69% | 31,47% | 0 VND |
| X2 MGE 1,5 **khong** cong | 29,93% | 1,88 | −17,81% | 1,68 | 1.306,02B | 28,18% | 31,54% | 0 VND |

**Chan control tai lap TUYET DOI ca 5 chi tieu + ca 2 so IS/OOS** cua pin chinh thuc 2026-08-03
(28,86 / 1,90* / −17,8 / 1,62 / 1.178,01B / 27,09 / 30,48). Doi chung doc lap tu CSV tho
(`extract_peryear.py`): FULL 28,86% / IS 27,09% / OOS 30,48% — khop ban in.
⇒ harness hop le, ban sao nghien cuu **trung thuc** voi production.

*(\*) Sharpe 1,83 o bang tren la so toi tu tinh lai tu chuoi NAV ngay (`dsr_pbo_annex.load_nav`),
registry pin 1,90 tu ban in cua engine — khac quy uoc gom NAV theo ngay, **khong** phai chenh lech
ket qua; delta giua cac chan trong cung 1 cot moi la thu duoc doc.*

### 1.2 Gate GO/NO-GO tuong minh cua dispatch — cham diem thang

| Dieu kien | L1b (MGE 1,3) | L2b (MGE 1,5) | Ket |
|---|---|---|---|
| OOS (2020+) duong | +0,88pp | +0,90pp | ✅ PASS |
| DSR ≥ 0,95 | **1,0000** (N=4 va N=21) | **1,0000** | ✅ PASS |
| MaxDD khong xau di so voi R3 | −17,79% (control −17,79%, **cung ngay day 2018-07-05**) | −17,79% | ✅ PASS |
| *(them, khong yeu cau)* LOO per-year | 0/13 nam am, min +0,24pp (bo 2022) | 0/13, min +0,30pp | ✅ ROBUST |

**Ve so, gate PASS.** Nhung ba diem duoi day noi rang **khong duoc doc no la GO cho margin.**

### 1.3 VI SAO KHONG DOC LA GO — phep do khong cham toi don bay

**(1) Do truc tiep: 91-95% phan tang la TAI PHAN BO, khong phai VAY.**
Trich tu chinh log engine (`[force-real-lever]` + `[borrow-audit]`), so sanh chi phi lai **thuc** voi
chi phi lai **neu toan bo phan `wt` tang them duoc tai tro bang vay**:

| Chan | so su kien co tang wt | lai NEU VAY HET | **lai VAY THUC (engine ghi)** | **% thuc vay** |
|---|---|---|---|---|
| L1b (1,3 + cong) | 9 | 350,4 tr VND | **32,0 tr** | **9,1%** |
| L2b (1,5 + cong) | 9 | 581,8 tr | **32,2 tr** | **5,5%** |
| X1 (1,3 khong cong) | 26 | 1.529,8 tr | 82,4 tr | 5,4% |
| X2 (1,5 khong cong) | 26 | 2.548,4 tr | 199,6 tr | 7,8% |

`[borrow-audit]` L1b: *"max gross BAL 1.000 LAG 1.067 **combined 1.000**; borrow-days BAL 7 LAG 79"*.
**Gross gop chua bao gio vuot 1,000 trong suot 12 nam.** Phan `wt` tang them chu yeu duoc lay bang cach
**dich von uu tien thap hon** (parking custom30V) sang tier CAPIT (uu tien 95), khong phai bang tien vay.
⇒ Day la **tai lap y nguyen** ket luan CORRECTION 2026-06-25 (*"trong che do CAPIT-ONLY, MGE la sizing
multiplier funded from cash, KHONG phai don bay that"*) — lan nay tren **spec engine hien hanh** va
**da bat `FORCE_REAL_LEVER=1`**, tuc la co gang ep vay that **van khong** ep duoc o NAV 50B.

**(2) Khong co dose-response o tang danh muc.** 1,3× → 1,5× cho **+0,61pp → +0,64pp** (phang). Neu day
la don bay that, tang boi so phai lam thay doi ket qua theo boi so. Phang = **bi chan boi luong von san
co**, khong phai boi so don bay. (Doi chieu: chinh dose-response don dieu la thu da lam `dd52` thanh ung
vien duy nhat o tang vi the — o tang danh muc, don bay **khong** co no.)

**(3) Mau thuan truc lap lai.** Chan **KHONG cong** (+0,80 / +1,07pp) **tot hon** chan **co cong `dd52`**
(+0,61 / +0,64pp). Nguoc han ket luan tang vi the (`dd52<=−20%` la truc tot nhat, +17,62% vs +5,46%).
Doc dung: cai lam ra so o tang danh muc la **TONG LUONG von dua vao CAPIT** (ungated lever 15 su kien,
gated chi 6), **khong** phai **chat luong cong**. Mot lan nua, day la hieu ung **sizing**, khong phai
hieu ung **tin hieu**.

**(4) Khong ap dung duoc cho tai khoan LIVE.** Backtest @50B luon con parking/tien nhan de dich sang
CAPIT. SpaceX hom nay **~98,5% da dau tu** (p1 §5). Live muon tang the nay thi **bat buoc phai vay that**
— dung phan ma phep do nay gan nhu **khong cham vao**.

### 1.4 BAY DA DO DUOC trong engine (bao cao rieng, khong sua production)

`pt_v23_audit_2014.py`: dinh nghia **that** cua `_mge_gate_m` nam **ben trong khoi `if RECOVERY_PARK:`**
(dong ~1541), trong khi placeholder `_mge_gate_m = (lambda dd: 1.0)` o dong ~490. O cau hinh R3
(`RECOVERY_PARK` **TAT**), placeholder song sot ⇒ **moi gia tri `MGE_GATE` deu VO HIEU IM LANG**.
Do duoc bang log: lan chay dau tien in `m=1.00` cho ca nhung su kien `dd52=−7,5%` (2024-04-17),
`−7,96%` (2025-04-03), `−13,1%` (2026-03-09) — dang le phai bi chan. Da phat hien va chay lai (chan
X1/X2 giu lai lam **doi chung ungated**, khong vut di).

- **Khong sua production** (research-only, dung pham vi dispatch). Ban sao nghien cuu va bang cach dinh
  nghia `_mge_gate_m` o **muc module** ngay sau khi `vni_hist` duoc dung.
- **Can bao cho bat ky ai dinh dung `MGE_GATE=conviction|deposit|fedborrow|deposit_eyield`** o mot cau
  hinh **khong bat `RECOVERY_PARK`**: cong se im lang khong hoat dong. Cac ket qua `MGE_GATE` cu
  (2026-06-24) chay o cau hinh co `RECOVERY_PARK` nen **khong** ket luan la chung sai — nhung ai muon
  tai su dung phai kiem lai dieu kien nay truoc.

### 1.5 Ket luan VIEC 1

**KHONG doc la GO cho margin.** Doc dung la:
- Huong **vay margin trong washout** o tang danh muc **van CHUA duoc kiem chung** — phep do nay khong
  cham toi no (5-9% thuc vay). Khong co bang chung moi **ung ho** lan **bac bo**.
- Phat hien phu **co that va dang gia**: **dich them von san co (parking → CAPIT) o washout sau**
  = **+0,61pp CAGR**, Sharpe +0,04, **MaxDD khong doi** (cung ngay day), OOS +0,88pp, DSR 1,0,
  **LOO 0/13 nam am**. Day la de xuat **khong can vay mot dong nao** — va la thu xung dang chay tiep,
  khac han thu user hoi.
- **Gioi han bat buoc doc kem** (nhu dispatch da yeu cau noi ro du ket qua the nao): cong `dd52<=−20%`
  chi chon **6 su kien**; day la 1 test XAC NHAN/BAC BO tin hieu tang vi the, **khong** phai co so de
  tu tin ket luan GO. Va o day no **bac bo** chieu doc "don bay": no chi xac nhan chieu "sizing".

---

## VIEC 2 — "Khong co dau hieu nao dot sut sau da TAO DAY va DI LEN de thanh pattern a?"

Cau hoi cua user **dung cho** va **chua tung duoc thu**: `dd52` do **DO SAU** (da sut bao nhieu tu dinh),
khong do **XAC NHAN DAO CHIEU** (da tao day va bat dau di len chua). Toi test ca hai dang.

**Du lieu:** 17 su kien washout 2014+ co ket cuc 60 phien (**y nguyen** tap cua p1), ro `universe_pit`,
`x` = loi the RONG cua 1 dong von vay (60 phien, lai 12,5%/nam, phi 2×0,075%). Nen G0 = **+9,75%**.
**Khong nhin truoc:** moi gia tri cong lay tai ngay `T` (biet duoc luc dong cua T), vao lenh `T+1`.

### 2.1 Quan sat CO CAU — tra loi truc tiep truoc khi thong ke

| Do o MUC THI TRUONG (VNINDEX) tai ngay fire | So su kien |
|---|---|
| VNINDEX **dung tai day 21 phien** ngay hom fire (`dsince_lo21 = 0`) | **24/26** |
| Da hoi > 1% tu day 1 thang | **1/26** |
| MACDdiff VNINDEX > 0 | **1/26** |
| Momentum 3 phien duong | **1/26** |

⇒ **Cong washout theo THIET KE fire dung luc thi truong DANG tao day, khong phai sau do.** Do la ly do
"dau hieu da tao day va di len" **khong ton tai** tai ngay kich hoat — khong phai vi khong ai tim, ma vi
**dinh nghia su kien neo vao dung ngay day**. Muon co xac nhan thi bat buoc phai **doi** (§2.3).

### 2.2 Dang (a) — tin hieu dao chieu lam GATE tai ngay T

Dung `C_L1M`/`C_L1W` **da xac minh thuc nghiem**: dictionary ghi "0..1" la **SAI** — do thuc te
`C_L1M ∈ [1,00; 8,33]`, TB 1,118 ⇒ `C_L1M − 1` = **% da hoi tu day 1 thang** (dung ung vien user goi y).

| Cong (mean tren ro tai T) | N | TB `x` | p_boot |
|---|---|---|---|
| G0 moi washout | 17 | +9,75% | 0,014 |
| ro da hoi tu day 1M **≥ 0,5%** | 13 | +8,94% | 0,035 |
| ro da hoi tu day 1M **≥ 1,0%** | 11 | +7,02% | 0,115 |
| ro da hoi tu day 1M **≥ 2,0%** | 6 | +4,31% | 0,600 |
| ro da hoi tu day 1M **≥ 3,0%** | 3 | +1,15% | 0,827 |
| **phan bu (da hoi < 3,0%)** | 14 | **+11,59%** | **0,004** |
| ro da hoi tu day 1W ≥0,5 / ≥1,0 / ≥2,0% | 12/9/5 | +7,74 / +4,16 / **+0,01%** | 0,077 / 0,411 / 0,974 |
| % ten trong ro co MACDdiff>0 ≥ 20% | 4 | **−2,21%** | 0,777 |
| CMB_XFast TB ≤3 / ≤5 / ≤8 | 9/14/17 | +12,31 / +7,53 / +9,75% | 0,003 / 0,060 / 0,015 |

- **`C_L1M` va `C_L1W` co dose-response DON DIEU — nhung NGUOC chieu**: cang co dau hieu "da hoi" tai
  ngay kich hoat thi ket cuc **cang kem**, den muc `C_L1W ≥ 2%` cho **+0,01%** (bang khong).
- **`CMB_XFast` khong don dieu** (12,31 → 7,53 → 9,75) ⇒ nhieu, khong dung lam cong.
- Kiem bang **tuong quan hang** (1 phep thu, khong cat nguong, permutation 20.000 lan): **ca 5 bien deu
  rho AM** (−0,10 → −0,34), khong bien nao dat y nghia (`p_perm` 0,19-0,69). Tuc la: **huong thi nhat
  quan (am), cuong do thi khong du manh de khang dinh o N=17** — nhung chac chan **khong** co bang chung
  cho chieu duong ma truc giac de xuat.

### 2.3 Dang (b) — DOI XAC NHAN roi moi vao lenh (dung nghia "da tao day va di len")

Day moi la dang dung ve khai niem: vao lenh o ngay **dau tien sau T** thoa dieu kien dao chieu (cua so
toi da 30 phien; khong thoa ⇒ bo su kien), giu 60 phien **tu ngay vao**.

**Tren CUNG TAP su kien** (loai bo hieu ung selection — day la phep kiem then chot):

| Xac nhan | N cung tap | `x` vao T+1 | `x` doi xac nhan | **Hieu** | so su kien tot len |
|---|---|---|---|---|---|
| VNINDEX hoi ≥8% tu day 1M (tre TB 14 phien) | 13 | +11,77% | +7,67% | **−4,09pp** (p=0,192) | **3/13** |
| VNINDEX > MA20 (tre TB 14 phien) | 15 | +12,44% | +8,96% | **−3,48pp** (p=0,108) | **2/15** |

⇒ **Doi xac nhan LAM MAT tien.** Ty le dau cuc ky lech (2/15, 3/13) noi manh hon ca p-value o N nay.
Co che ro rang: xac nhan den sau **trung binh 13-14 phien**, va **phan hoi chinh la thu ban tra tien de
doi**.

### 2.4 Cai bay toi suyt bao cao sai — "doi xac nhan giup giam MAE"

Doc **so tho** (bang tinh dau tien, `analyze_rev2.py`) thi rat hap dan, va no danh dung **rang buoc troi**
cua bai toan don bay (RUIN, khong phai ky vong):

| Chan | MAE xau nhat | MAE p10 | tran gross an toan (maint 35%) |
|---|---|---|---|
| T+1 ngay lap tuc | −25,14% | −21,26% | 1,90 |
| doi VNINDEX hoi ≥8% | **−12,51%** | −10,50% | **2,30** |
| doi Close > MA20 | −14,82% | −12,15% | 2,20 |

**Nhung do la AO ANH SELECTION.** Tren **cung tap su kien**, hieu ung **bien mat hoan toan**:
hieu MAE = **+0,41pp** (p=0,790, 7/13 nong hon) va **+0,32pp** (p=0,848, 7/15). Nguyen nhan co hoc:
**dung 2 su kien co MAE sau nhat — 2020-02-03 (−25,14%) va 2022-09-28 (−24,44%) — KHONG BAO GIO co xac
nhan trong 30 phien**, nen bi **loai khoi mau** chu khong phai duoc **cai thien**. (Chan `reb1m≥8%` bo
them 2022-06-15 va 2025-10-20; chan `MA20` chi bo dung 2 su kien tren.)
Noi cach khac: **luat "doi xac nhan" tu choi giao dich dung nhung dot no dinh bao ve.** Va no cung bo
luon `2025-10-20` — su kien co ket cuc **tot nhat bang** (`x = +30,70%`).

*(Ghi lai o day vi day la loai loi de tin nhat: bang so dau tien "co lam sao" theo dung huong minh mong
doi, va chi lo ra khi ep so sanh tren cung tap.)*

### 2.5 Dang (c) — TO HOP do sau ∧ dao chieu

| Cong | N | TB `x` | p_boot |
|---|---|---|---|
| `dd52<=−20%` (S4 goc) | 6 | **+17,62%** | 0,036 |
| `dd52<=−20%` **∧** ro da hoi ≥1% | 5 | +11,01% | 0,118 |
| `dd52<=−20%` **∧** ro da hoi ≥2% | 3 | +11,88% | 0,517 |
| `dd52<=−20%` **∧** CMB_XFast ≤5 | 5 | +11,01% | 0,115 |
| `dd52<=−20%` **∧** %MACDdiff>0 ≥40% | **0** | — | — |

⇒ **Them chieu "da dao chieu" vao `dd52` deu lam XAU DI.** Gia thuyet cua dispatch (rang mau thuan truc
S3-vs-S4 o p1 la do **ca hai** deu thieu chieu dao chieu) **khong duoc du lieu ung ho**: bo sung chieu do
khong hoa giai duoc mau thuan, no chi lam giam ca N lan TB.

### 2.6 Co mo cua cho 2026-07-20 khong?

| Cong | Gia tri 2026-07-20 | Ket |
|---|---|---|
| `dd52 <= −20%` | −9,57% | **CHAN** |
| ro da hoi tu day 1M ≥ 1% / ≥ 2% | 2,28% | PASS |
| RSI ro da hoi tu day 1W ≥ 5 | 5,25 | PASS |
| CMB_XFast ≤ 5 | 4,33 | PASS |
| % ten MACDdiff>0 ≥ 40% | 16,7% | **CHAN** |

Cac cong dao chieu **co** mo cho 2026-07-20 — **nhung do khong phai su ung ho**: chinh nhung o "da hoi
≥1-2%" la **nhung o KEM NHAT** trong bang §2.2 (+7,02% / +4,31% so voi nen +9,75%). PASS mot cong da do
duoc la **lam xau di** thi khong phai ly do de vay them.

### 2.7 Ket luan VIEC 2

**Tra loi thang cau hoi cua user:** *co* mot pattern that trong lich su — nhung no **nguoc chieu truc giac**.
Phan thuong cua rổ CAPIT nam o viec mua **dung luc so hai nhat, khi chua co gi xac nhan**; moi hinh thuc
"cho thi truong xac nhan da tao day" ma toi do duoc deu **tra tien** cho su xac nhan do, **khong** duoc bu
lai bang rui ro thap hon. Va cai ve "rui ro thap hon" nhin thay ban dau la **selection**, khong phai timing.

**KHONG co gate dao chieu nao du dieu kien de chay tiep o tang portfolio-engine.** Khong mo them huong nao.

---

## 3. Ky luat thong ke + minh bach

- **N_trials VIEC 2 = 27** (16 nguong o §2.2 + 6 luat xac nhan o §2.3 + 5 to hop o §2.5); cong don voi
  17 cua p1 ⇒ **44** tren cung chu de. Tat ca deu bao cao, khong chon-loc-sau. Ket luan la **NO-GO**
  nen khong gian tim kiem rong khong lam sai lech theo huong nguy hiem (rong ⇒ cang de tim ra thu
  "duong" gia; toi **khong** tim duoc thu nao duong).
- **N_trials VIEC 1 = 4 chan**; ho don bay CAPIT tich luy ~21. **DSR = 1,0000 o CA N=4 va N=21** —
  nhung xin doc dung: DSR o day cao vi chuoi NAV la **ca he V2.4** (Sharpe 1,8+), khong phai vi **rieng**
  lop don bay co edge. DSR **khong** tach duoc dong gop cua lop don bay; no chi noi "chuoi tong the khong
  phai san pham cua dò tham so". Delta +0,61pp moi la thu can doc, va §1.3 giai thich no den tu dau.
- **LOO per-year VIEC 1**: 0/13 nam am (min +0,24pp khi bo 2022) ⇒ khong co 1-2 nam ganh het edge.
  Day la diem **manh** that cua chan L1b — nhung la manh cho luan diem **sizing**, khong phai cho margin.
- **quant-skeptic: khong dispatch** — job nay **khong de xuat thay doi production nao**. Neu ai muon
  bien §1.5 (dich von parking → CAPIT) thanh de xuat wire, **quant-skeptic + DSR/PBO tren dung cau hinh
  do tro thanh bat buoc truoc**.
- **Chi phi vay 12,5%/nam** van **chua doi chieu hop dong DNSE** (nhu p1 §7). Khong doi ket luan nao o
  day: chan engine chi thuc su vay 5-9%, con tang vi the thi 10,0% cung khong doi dau.
- **Bay du lieu da xac minh, ghi de ai sau con dung:**
  (a) `C_L1M`/`C_L1W` **KHONG** nam trong [0,1] nhu `bigquery_dictionary.json` va CLAUDE.md ghi — do
  thuc te [1,00; 8,33], nghia la **Close / day**, nen `−1` de ra % da hoi.
  (b) `D_CMB_Peak_T1` **KHONG** phai co −1/0/1 nhu tai lieu mo ta — trong `tav2_bq.ticker` no la **float
  lien tuc** (gia tri quanh 1, va vo so gia tri le); **khong dung duoc** lam co "day/dinh" neu chua lam
  ro lai dinh nghia. Toi da dung no o dang `<0` va no khong cho tin hieu.
  (c) `VNINDEX_RSI` / `VNINDEX_MACDdiff` / `VNINDEX_CMF` **KHONG ton tai** trong `tav2_bq.ticker` (da
  kiem schema) du CLAUDE.md liet ke o muc "VNINDEX mirror" — chi co `VNINDEX` va `VNINDEX_PE`. Toi tu
  tinh RSI(14)/MACDdiff tu chuoi Close cua VNINDEX.
- **Production sach:** `git status --porcelain` **rong** tren `pt_v23_audit_2014.py`,
  `macro_state_live.py`, `rating_8l.py`, `data/trading_rules.json`, `deploy_golive_dt5g_v4/`,
  `simulate_holistic_nav.py`. Moi CSV ket qua deu co `EXP_TAG` (`§8` coding_guidelines), canonical
  `..._wtnamecap.csv` **khong bi dung toi**.

**Artifact:** `mike/agents/Taylor/exp_margin_kelly/p2/` — `engine_dd52.py` (ban sao nghien cuu),
`run_s4.sh`, `fetch_rev.py`, `analyze_rev.py`, `analyze_rev2.py`, `analyze_rev3.py`, `metrics.py`,
`rev_signals.csv`, `px_pit.parquet`, 5 log chay (`s4p2_*.log`, ke ca 2 log X1/X2 giu lam doi chung
ungated + bang chung cua bay `MGE_GATE` im lang).

---

## 4. Buoc tiep theo de xuat (khong tu lam trong job nay)

1. **[Uu tien cao, KHONG can vay]** Test rieng gia thuyet **"dich them von san co tu parking sang CAPIT
   o washout sau"** — day la thu chan L1b thuc su do duoc (+0,61pp, MaxDD khong doi, LOO 0/13). Lam dung
   cach thi phai **tach bien**: dung `CAPIT_SIZE_BASE=park:f` (dose-response theo f) thay vi di qua `MGE`
   — vi `MGE` tron lan hai co che (sizing + vay) va da chung minh la **do nham** cai thu hai. Kem
   DSR/PBO + quant-skeptic truoc khi noi den wire.
2. **[Chan bat buoc neu con muon theo huong margin]** Do capacity that: `pp0Buy` that cua SpaceX + P0
   shadow log ≥10 phien (p1 §6, van chua co). Khong co so nay thi moi ban ve "vay bao nhieu" van la gia dinh.
3. **[Re, khach quan]** Cho `CAPIT-2026-07-20` du 60 phien (~2026-10-15) roi cham diem no vao phan phoi
   §3 cua p1 — them 1 quan sat that vao N=17.
4. **[Ve sinh, khong gap]** Bao/ghi so **bay `MGE_GATE` im lang** o §1.4 vao noi ai do se doc truoc khi
   dung lai `MGE_GATE` — do la mot cai bay "code chay, khong bao loi, ket qua sai im lang" dung mau
   `coding_guidelines` §14.
