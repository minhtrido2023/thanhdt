# KET QUA — do hieu qua margin qua CA CHU KY (thuc thi buoc A+B+C)

**Job** `Taylor_20260803_091342` · **Ngay** 2026-08-03 · **RESEARCH-ONLY, production KHONG bi cham**
**Ke hoach nguon** `margin_kelly_full_cycle_plan_20260803.md` (job `Taylor_20260803_082241`) — gate
dang ky TRUOC, khong sua trong khi chay.
**Artifact** `mike/agents/Taylor/exp_margin_kelly/p4_fullcycle/`

---

## 0. TL;DR — chay het A→C, ca ba gate PASS o `f ∈ {1,1; 1,2; 1,3}`; `f=1,5` bi loai

| Gate | Ket qua | Chi tiet quyet dinh |
|---|---|---|
| **G-A** (giai tich, g(f)) | **PASS** | `f*_geo = 2,00 > 1,0`; `P_boot(g(1,3)>g(1,0))` = **0,971 iid / 0,949 khoi** (nguong 0,90) |
| **G-B** (duong di sleeve) | **PASS** | **0 margin call** o MOI `f ≤ 1,5`; min equity/tai san = **0,547** vs nguong 0,35 |
| **G-C** (toan so) | **PASS `f≤1,3`** · **FAIL `f=1,5`** | `f=1,5` lam MaxDD xau di **+1,35..1,49pp** > tran +1,0pp |

**Tra loi thang cau hoi cua user (John):** voi thong ke da do, phep nhan hinh hoc noi **CO** — mot
chinh sach vay co dinh o muc **vua phai (f ≤ 1,3)** cho toc do tang truong hinh hoc cao hon khong vay,
va khong cham margin call trong 17 lan lich su. Phe binh phuong phap luan cua user la **DUNG**: p1 do
"ruin 1 lan cuoc" chu chua bao gio do "toc do tang truong qua chuoi cuoc lap lai", va khi do dung dai
luong do thi ket qua doi chieu.

**NHUNG** — day la ket qua o **TANG PROXY (overlay toan hoc)**, dung tang ma chinh kho nay da 4 lan
ghi nhan "proxy duong → engine am" (§6.1). Deliverable toi da cua job nay la **ung cu vien cho buoc D**,
**KHONG phai de xuat wire**, va **KHONG dao nguoc** verdict NO-GO cua p1 (mat xich dut cua p1 la *cong
kich hoat* + *tang engine*, hai thu job nay khong dung toi).

---

## 1. SUA LOI NGUYEN LIEU — job suyt chay tren sai chan universe

Dispatch chi toi `events_outcome.csv`. Kiem tra dau vao cho thay file do co **TB x = +10,45%, 70,6%
duong** — do la chan **`ticker_prune`** (co thien lech song sot), KHONG phai chan headline
**`universe_pit`** (+9,75%, 64,7%) ma **§4 guard #5 cua ke hoach BAT BUOC** dung lam so chinh.

Da dung lai duong NAV ngay theo PIT tu `basket_pit.csv` + `p2/px_pit.parquet` (`build_pit_paths.py`),
tai lap y nguyen co hoc `robust_pit.py:outcome()`:

```
SELF-CHECK tai lap r_pit: 19 su kien, sai so max = 9,7e-17   (nguong 1e-9)
SELF-CHECK so ten trong ro: 0 su kien lech
N (2014+, ket cuc day du) = 17    TB x = +9,7491%    %duong = 64,7%    MAE xau nhat = -25,1406%
```

Khop tuyet doi pin p1. **Moi so trong bao cao nay la chan `universe_pit`.** Chan `prune` chi chay
sensitivity (cho `f*_geo` cao hon — tuc chan sai se **phong dai** loi ich vay, dung huong canh bao).

---

## 2. BUOC A — duong cong tang truong hinh hoc `g(f)`

`R_i(f) = f·(r_i − φ) − (f−1)·c·d_i/365`, `g(f) = (1/N)·Σ log(1+R_i(f))`, N=17, φ=0,15%.

| Kich ban | `f*_geo` | g(1,0) | g(f*) | g(1,3) | #call@1,5 |
|---|---|---|---|---|---|
| BASE (c=12,5%, maint 30%, pen 1%) | **2,00** | 0,10853 | 0,16401 | 0,12735 | 0 |
| ADV lai (c=14%) | 2,00 | 0,10853 | 0,16087 | 0,12639 | 0 |
| ADV maint (35%/2%) | 1,85 | 0,10853 | 0,15696 | 0,12735 | 0 |
| ADV full (14%/35%/2%) | 1,85 | 0,10853 | 0,15429 | 0,12639 | 0 |
| **ADV edge (r − 6,6pp = can duoi CI90)** | **1,20** | 0,04676 | 0,04731 | 0,04722 | 0 |

**Bootstrap B=10.000, c=12,5%:**

| Don vi resample | P(g(1,3)>g(1,0)) | CI90 cua hieu | P(f* ≤ 1,0) |
|---|---|---|---|
| iid | **0,9710** | [+0,0026; +0,0346] | 0,027 |
| **theo khoi** (8 khoi/17 su kien) | **0,9489** | [−0,0002; +0,0368] | 0,051 |

→ **G-A PASS.** Meta-gate khong kich hoat: ca 5 kich ban deu ket luan cung chieu ("nen vay"),
`P_boot` tai lai suat 14% = 0,9392 (van ≥0,90).

**Doc dung do manh:** chan `ADV edge` la chan dang chu y nhat — keo edge ve can duoi CI90 thi `f*`
tut tu 2,00 xuong **1,20** va bien loi the gan nhu bien mat (g(1,2) 0,04731 vs g(1,0) 0,04676).
Tuc **ket luan "nen vay" khong ben truoc sai so uoc luong edge** — dung nhu p1 §4.2 canh bao.
Bien do an toan nam o *muc* f, khong o *dau* cua ket luan.

---

## 3. BUOC B — duong di sleeve, kiem margin call HANG NGAY

Chinh sach V(f) bat buoc, gia that, kiem `E_t/A_t < maint` moi phien.

| Kich ban | f=1,1 | f=1,2 | f=1,3 | f=1,5 | kelly (1,0–1,5) |
|---|---|---|---|---|---|
| #call, BASE | 0 | 0 | 0 | 0 | 0 |
| #call, **ADV (35%/14%/2%)** | 0 | 0 | 0 | **0** | 0 |
| min E/A, ADV | 0,876 | 0,773 | 0,686 | **0,546** | 0,546 |
| g (log), ADV | 0,11455 | 0,12050 | 0,12622 | 0,13705 | 0,12496 |
| W_N (17 su kien), ADV | 7,01 | 7,76 | 8,55 | 10,28 | 8,37 |

**P(ruin) bootstrap khoi = 0,0000 o moi f** → **G-B PASS**.

**Canh bao trung thuc bat buoc doc kem:** `P(ruin)=0` la ket qua **TAM THUONG** — 0/17 su kien lich su
cham nguong, nen bootstrap tu chinh 17 su kien do *khong the* sinh ra call. Day la bang chung YEU
("chua tung xay ra trong 17 lan"), khong phai bang chung manh ("khong the xay ra"). Phep do co suc
phan bac that la chan shift duong gia:

| Chan stress | f=1,0 | f=1,2 | f=1,3 | f=1,5 |
|---|---|---|---|---|
| duong gia −10% | g +0,0030 | −0,0058 | −0,0105 | **−0,0210** |
| duong gia −20% | g −0,1148 | −0,1503 | −0,1691 | **−0,2089** |

→ Ngay khi edge bien mat, don bay **don dieu lam xau di** va `f` cang cao cang te. Van khong co margin
call (vi MAE ro CAPIT chua bao gio du sau), nhung **ruin khong phai kenh thiet hai chinh** — kenh chinh
la **nhan lo khi edge sai**.

---

## 4. BUOC C — tich hop toan so, VA mot AO ANH DO LUONG da phat hien va sua

### 4.1 Lan chay dau cho FAIL — nhung la loi cua PHEP DO, khong phai cua chien luoc

Lan chay dau (`step_c_wholebook.py`, overlay cong-them) cho **`ΔCAGR_OOS` AM o moi f** va **LOO: 2025
ganh 71% edge** → doc thang la FAIL G-C. Kiem tra lai theo guard #10 phat hien **ca hai deu la ao anh
ke toan**:

- Trong ban cong-them, lai cua giai doan IS bi de lai duoi dang **tien mat 0%/nam** chay suot OOS →
  keo tut toc do tang truong do trong cua so OOS. `ΔCAGR_OOS` am **khong** co nghia "don bay het tac
  dung sau 2020", ma co nghia "phep do mang von ky truoc sang ky sau roi phat no".
- Cung co che do lam LOO lech nang: mot khoan lai **cuoi chuoi** (2025-10-20) roi thang vao NAV cuoi,
  trong khi lai **dau chuoi** nam chet duoi dang tien mat → LOO gan het trong so cho su kien cuoi.

**Phep do sach** (`step_c3`): overlay CHI voi su kien cua tung cua so, do CAGR trong DUNG cua so do.
Ket qua doi chieu, va **LOO doi hoan toan**: su kien gong nhat tro thanh **2018-07-05 (26,8%)**, khong
phai 2025-10-20 (72%).

> **Tu bao cao thang:** viec sua nay **lat verdict cua chinh toi tu FAIL sang PASS**, va bien the sua
> la bien the **co loi cho phia "margin tot"**. Toi neu ro de quant-skeptic soi dung cho nay. Ly do
> toi cho rang sua la dung chu khong phai chieu theo ket qua mong doi: gia dinh "lai nam im 0%" khong
> mo ta chuong trinh that (lai sleeve quay ve so va duoc trien khai tiep), va **ca hai** ban ke toan
> cho **cung ket luan** khi do sach trong cua so (chenh <0,05pp) — tuc ket luan khong phu thuoc lua
> chon ke toan nua, do moi la kiem dinh that.

### 4.2 Gate G-C chung cuoc — on dinh tren CA 4 to hop truc fragility

`ΔMaxDD` = **muc XAU DI** (duong = te hon control). Nguong §5: ≤ +1,0pp.

| Lai/maint/pen | Ke toan | f | ΔCAGR_IS | ΔCAGR_OOS | ΔCAGR_FULL | ΔMaxDD xau | LOO nam | LOO sk | #call | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE 12,5/30/1 | cong-them | 1,3 | +2,51% | +1,31% | +1,82% | +0,83pp | 37,3% | 25,1% | 0 | **PASS** |
| BASE 12,5/30/1 | tai dau tu | 1,3 | +2,59% | +1,32% | +1,94% | +0,88pp | 38,9% | 26,1% | 0 | **PASS** |
| ADV 14/35/2 | cong-them | 1,3 | +2,47% | +1,23% | +1,77% | +0,85pp | 38,2% | 25,9% | 0 | **PASS** |
| ADV 14/35/2 | tai dau tu | 1,3 | +2,54% | +1,23% | +1,87% | +0,90pp | 39,8% | 26,8% | 0 | **PASS** |
| ADV 14/35/2 | tai dau tu | **1,5** | +4,18% | +2,02% | +3,07% | **+1,49pp** | 39,6% | 26,5% | 0 | **FAIL** |

`f=1,1` va `f=1,2` PASS o ca 4 to hop (ΔMaxDD +0,29..0,30pp va +0,57..0,60pp). **`f=1,5` FAIL o ca 4
to hop** (ΔMaxDD +1,35..1,49pp). **Khong co truc nao cho ket luan nguoc → meta-gate FRAGILE khong
kich hoat.** 0 margin call toan-so o moi cell.

### 4.3 Guard #10 — so VUOT tran ky vong §2.2, da audit theo yeu cau

`ΔCAGR_FULL` o `f=1,5` = **+2,81..+3,07pp/nam**, vuot tran §2.2 (+2,1pp). Da dung lai audit truoc khi
bao cao (dung nhu guard #10 yeu cau). Nguyen nhan, phan ra bang so thuc do:

| Thanh phan | Gia tri |
|---|---|
| sleeve TB **thuc do** | **37,5% NAV** (§2.2 gia dinh 31%) |
| edge sau lai vay 14% | +9,39%/su kien |
| tan suat su kien | 1,36/nam |
| → tran tinh lai (tich cua TB), f=1,5 | **+2,40pp/nam** |
| dong gop **hiep phuong sai** (sleeve lon ↔ edge tot, corr **+0,243**) | **+0,225pp/nam** |
| → tong arithmetic thuc | **+2,63pp/nam** — phan con lai la lai kep cua chinh cac gia so qua 12,5 nam |

⇒ Vuot tran duoc **giai thich het**, khong phai bug. Nhung **hiep phuong sai +0,243 la mot canh bao
that**: rieng viec `capit_size` lon roi trung vao su kien ket cuc tot da dong gop ~0,2pp/nam, va voi
N=17 thi corr 0,24 la **bang chung mong** (co the la may). Khong duoc trich phan nay nhu edge co che.

### 4.4 Guard #6 — tuong quan sleeve vs ca so (bay tuong quan)

| | sleeve MAE | NAV_L0 cung ky | NAV_L0 min/entry |
|---|---|---|---|
| Trung binh 17 su kien | −6,99% | +0,46% | **−2,87%** |

`corr(sleeve MAE, NAV_L0 min)` = **+0,545** — ca so **co** sut cung luc sleeve sut (2020-02: sleeve
−25,1% / so −5,4%; 2022-09: −24,4% / −6,5%). Da tinh vao maintenance toan-so (day la ly do ban toan-so
la so quyet dinh, khong phai sleeve-alone). Do lon con dem (so sut ~1/4 do sau cua sleeve) la ly do
0 margin call van dung o tang toan-so.

---

## 5. Ky luat thong ke — khai bao dung theo §4 guard #3 va §6

**N_trials.** Ke hoach khai ~40 cell. **Thuc chay ~87 cell** — khai bao thang phan vuot:
- **Chinh sach thuc su duoc tim kiem = 6** (`f ∈ {1,0; 1,1; 1,2; 1,3; 1,5}` + fractional-Kelly).
  Khong them chinh sach nao ngoai luoi ke hoach.
- Phan vuot (~47 cell) **KHONG phai search config moi** ma la **do lai CUNG 6 chinh sach** duoi phep
  do da sua (`step_c3/c4/c5`: 3 cua so × 2 ban ke toan × 2 lai suat) — bat buoc phat sinh tu audit
  guard #10 va tu viec phat hien ao anh do luong o §4.1. LOO/bootstrap la **phan ra robustness cua 1
  cau hinh**, khong phai lua chon giua nhieu cau hinh.
- **Rui ro selection thap theo huong ngac nhien**: gate loai dung cau hinh **loi nhuan cao nhat**
  (`f=1,5`, ΔCAGR +3,07pp) vi drawdown — neu dang toi uu hoa theo ket qua thi da giu no.
- Cong don chu de margin+Kelly: p1 (44) + p2 + p3 + job nay (~87) ⇒ **~180+**. Day la **vong 4 tren
  CUNG 17 su kien**.

**DSR/PBO**: chua tinh — theo §4 guard #4 chi bat buoc **neu** de xuat wire 1 config, va job nay
**khong** de xuat wire. La viec cua buoc D.

**Bon diem tu phe binh §6 — da kiem the nao:**

1. *Satellite-ledger phong dai loi ich vay* → **Da xu ly.** So quyet dinh lay tu ban **toan-so**
   (§4.2), sleeve-alone (§3) chi dung lam chan doan. Sleeve-alone qua that dep hon (g 0,137 o f=1,5)
   so voi ΔCAGR toan-so +0,83pp/nam — dung huong da du bao.
2. *MC dung lai 17 draw da biet la duong → trung vi chac chan tang* → **Da xu ly.** Gate dat o
   `P(g(1,3)>g(1,0))`, `P(ruin)`, tail va LOO — khong o trung vi. Trung vi co bao cao nhung
   phi-quyet-dinh. Han che "bootstrap cho phan phoi cua UOC LUONG, khong phai cua tuong lai" giu
   nguyen hieu luc.
3. *Vong 4 tren cung du lieu, ap luc "user muon ket qua khac"* → **Rui ro CON NGUYEN va da hien
   thuc hoa mot phan**: job nay **lat FAIL→PASS** bang mot lua chon mo hinh hoa. Toi da (a) neu thang
   viec do o §4.1, (b) chung minh ket luan khong con phu thuoc lua chon do (ca 2 ban ke toan trung
   nhau), (c) yeu cau quant-skeptic review **bat ke chieu ket luan**. Day la diem can soi ky nhat.
4. *Lua chon khoi/maint/penalty/lai suat co the thien vi* → **Da xu ly.** Moi tham so chay ca chan
   adversarial dang ky truoc; ket qua on dinh tren 4 to hop (§4.2). Chan `ADV edge` (§2) la chan duy
   nhat lam ket luan yeu di ro ret — da bao cao noi bat, khong chon giau.

---

## 6. Vi sao ket qua nay **KHONG** phai "margin duoc bat den xanh"

### 6.1 Day la tang PROXY — dung tang da 4 lan that bai o kho nay
Overlay toan hoc **khong phai** engine. p1 §4.3 da ghi san bang chung nguoc o tang engine:
`FORCE_REAL_LEVER=1` → **Calmar 1,54 → 1,31**; sweep MGE 1,3→2,0 → **don dieu xau di** 29,32% → 27,97%;
V2.5 tong the **OOS −0,05pp, DSR 0,18–0,56**. Ghi chu meta cua registry: *"lan thu 3 ... mot tin hieu
duong o tang proxy/in-sample that bai o chieu risk-adjusted/duong di"*. **Job nay vua tao ra tin hieu
duong o tang proxy lan thu 4.** Buoc D (tang engine) chinh la phep thu da tung giet 3 lan truoc — va
no **chua chay**.

### 6.2 Cai job nay KHONG dung toi
- **Cong kich hoat** (p1 §4.1): van khong co cong on dinh; cong valuation cua user (`pe_pctile≤0,20`)
  van lam **xau di** (+6,16% vs +12,26% phan bu). Job nay ap chinh sach cho **moi** washout — tuc gia
  dinh khong can cong. Neu thuc te phai co cong, ket qua nay khong ap dung.
- **Capacity that** (p1 §6): `pp0Buy` SpaceX van chua co ban ghi that; P0 shadow chua du 10 phien.
  Khong biet co vay duoc that khong.
- **`capit_size=0` o 2022-09-28** (mot trong 3 su kien lo, r=−12,4%) la **luat production co san**,
  khong phai gate fit — nhung no **co** lam dep ket qua overlay. Da giu nguyen (khong duoc sua luat
  production de test), chi ghi ro de nguoi doc biet.

### 6.3 Do nhay voi sai so edge la diem yeu that
Keo edge ve can duoi CI90 → `f*` tut 2,00 → 1,20, loi the gan bang 0. Voi N=17 va CI90 rong
[+3,18; +16,61], **uoc luong edge chinh la mat xich yeu nhat**, dung nhu p1 ket luan. Ket qua "nen vay"
chi ben trong pham vi edge that ≈ edge da do.

---

## 7. Trang thai va viec tiep theo (KHONG tu quyet)

- **Khong cham production.** `git status` vung `WorkingClaude` khong co file production nao doi; moi
  output nam trong `mike/agents/Taylor/exp_margin_kelly/p4_fullcycle/`.
- **Khong de xuat wire** (dung ranh gioi dispatch). Ket qua toi da: `f ∈ {1,1; 1,2; 1,3}` la **ung cu
  vien cho buoc D**, uu tien doc so o `f=1,2` (ΔCAGR +1,21..1,30pp, ΔMaxDD +0,57..0,60pp — bien an
  toan gap ~1,7 lan tran DD, khac `f=1,3` chi con ~1,15 lan).
- **Buoc D (chua chay, can dispatch rieng Opus/high):** xac nhan tang engine bang ban sao
  `engine_dd52.py` (guard #9: KHONG dung `MGE_GATE` production khi `RECOVERY_PARK` tat) + DSR/PBO tren
  ho {f} + **quant-skeptic bat buoc**. Neu tang engine lai am nhu 3 lan truoc → dong chu de margin,
  khong mo lai bang lens moi.
- **Kien nghi rieng cua toi cho nguoi duyet:** cho quant-skeptic soi truoc het vao **§4.1** (cho toi tu
  lat verdict) va **§4.3** (hiep phuong sai sleeve↔edge). Do la hai cho ket luan de sai nhat.

---

## 8. Tai lap

```bash
cd mike/agents/Taylor/exp_margin_kelly/p4_fullcycle
PY=/home/trido/thanhdt/wc_venv/bin/python     # pandas 3 — KHONG dung python3 he thong
$PY build_pit_paths.py        # dung chan universe_pit + SELF-CHECK tai lap r_pit (1e-17)
$PY step_a_gcurve.py pit      # BUOC A  -> step_a_gcurve_pit.log
$PY step_b_sleeve_path.py     # BUOC B  -> step_b_sleeve.log
$PY step_c_wholebook.py       # BUOC C ban dau (co ao anh do luong, giu lam bang chung)
$PY step_c3_clean_isoos.py    # AUDIT guard #10 + phep do sach
$PY step_c5_final_gate.py     # GATE G-C chung cuoc, 4 to hop fragility
```
Khong dung BQ (`p2/px_pit.parquet` phu 50/50 ten PIT). Khong dung cot `profit_*` o bat ky buoc nao.
