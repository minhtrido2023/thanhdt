# Vay margin + Kelly sizing trong pha washout CAPIT — co kich ban nao dung vung khong?

**Job** `Taylor_20260803_070954` · **Ngay** 2026-08-03 · **Loai** RESEARCH-ONLY (khong wire gi)
**Cau hoi cua user (John):** production V2.4 khong dung margin. Dot CAPIT `CAPIT-2026-07-20`
(NCT/PVT/SAB/SIP/VNM, size 0,75, von thuan equity) no ra khi DT5G o NEUTRAL chu khong CRISIS/BEAR,
trong khi value_radar/8L bao "re tuong doi". Gia thuyet: **day chinh la luc nen VAY margin de tang
ty trong, sizing theo Kelly**, thay vi dung nhin.

> ## VERDICT NGAN
> **NO-GO cho moi kich ban de xuat wire.** Dieu kien CAN co dat (mot dong von vay bo vao ro CAPIT
> tai ngay washout CO thang duoc lai vay), nhung **ba mat xich sau deu dut**: khong co cong kich
> hoat on dinh (cong valuation cua user lam KET QUA XAU DI), Kelly doi don bay vuot **tran ruin**,
> va **tang danh muc da bac co che nay 2 lan** (2026-06-26 Kelly-lever REJECTED; 2026-07-12 V2.5
> NO-GO, DSR 0,18-0,56).
> **Mot quan sat MOI dang ghi so:** tien de cu cua engine ("MGE vay 0 VND vi luon con tien nhan
> roi") **khong con dung o tai khoan live** — SpaceX hom nay ~98,5% da dau tu. Khong doi verdict,
> nhung day la ly do gia thuyet cua user khong vo ly va dang theo doi tiep.

---

## 1. Doi chieu voi mach nghien cuu cu — phan nao TRUNG, phan nao MOI

Yeu cau tuong minh cua dispatch: khong tai dien 1 test da co. Ket qua doi chieu:

| Thanh phan gia thuyet cua user | Da test chua? | Ket qua cu |
|---|---|---|
| Vay margin **chi** trong washout (khong blanket) | **DA TEST** — `MGE_CAPIT_ONLY` (2026-06-23 → 06-25) | Do duoc la **vay ~0 VND**: "trong che do CAPIT-ONLY, MGE la **sizing multiplier** funded from cash, KHONG phai don bay that" (`results_registry.md`, muc CORRECTION 2026-06-25). Khi **ep** vay that (`FORCE_REAL_LEVER=1`): gross van chi cham 1,000, MaxDD tot len nhung **Calmar 1,54 → 1,31 XAU hon**. |
| **Kelly sizing** cho don bay o day | **DA TEST** — `kelly_lever_sizing.py`, 2026-06-26 | 🔴 **REJECTED**. Kelly (Bayes-shrunk, half-Kelly) doi **3,5-6,7x**; sweep thuc te MGE 1,3 → 2,0 **don dieu XAU di** (29,32% → 27,97%). Ket luan nguyen van: *"Kelly dinh gia 1 cuoc danh DON LE; danh muc that compound lien tuc — don bay tuong tac voi duong di cua ca so."* |
| Don bay co dieu kien theo **valuation re** | **DA TEST** — cong state-blind + `PE_pctile<=0,20`, 2026-06-26 | 🟢 lam **tot hon** cong theo state (+0,46pp) — nhung do la cong cho **lever-at-bottom qua parking (S2)**, KHONG phai cho arm CAPIT, va toan bo tang don bay do sau cung bi **V2.5 NO-GO** (2026-07-12). |
| Ca tang don bay (V2.5 = V2.4 + leverage) | **DA TEST** | 🔴 **NO-GO 2026-07-12**: edge +0,92pp la **IS-artifact** (IS +1,88 / **OOS −0,05**), DSR 0,18-0,56 (RED FLAG), 2/3 episode bi tran NAV vo hieu. quant-skeptic CONFIRMED. |
| **Vay vao arm CAPIT o state NEUTRAL** (chinh xac ca 2026-07-20) | ⚠️ **CHUA TEST** | Cong lever cu (`MGE_GATE=conviction`) doi `state == CRISIS`; cua NEUTRAL **chua bao gio chay**. Day la phan DUY NHAT thuc su moi → la phan toi do o §2-§4. |

**Ket luan §1:** ~80% gia thuyet trung co che da bi bac. Toi **khong** chay lai chung. Phan con lai
(cua NEUTRAL) duoc test moi duoi day.

---

## 2. Phuong phap — tang VI THE (dieu kien CAN)

Cau hoi rut gon, khong the tranh: *mot dong von VAY, bo vao **dung** ro CAPIT, tai **dung** ngay tin
hieu, giu **dung** 60 phien — co thang duoc chi phi vay khong?* Neu KHONG, moi kich ban Kelly deu sup
truoc khi can chay engine.

- **Tai lap luat production, khong dinh nghia lai** — su kien washout (`pt_v23_audit_2014.py:1133-1140`:
  `ticker_prune`, `D_RSI<0.3`, gate 0,30, cum cach ≥30 ngay) va ro CAPIT (`:1180-1210`: `ROE_Min5Y≥0,12`
  ∧ `ROIC5Y≥0,10` ∧ `FSCORE≥6` ∧ thanh khoan ≥2 ty; `pbz<−1` (≥3 ten) else `pbz<0` else all; top-15 pbz
  nho nhat). **Hold = `CAPIT_HOLD` = 60 phien.**
- **Self-check tai lap:** danh sach 26 su kien **MATCH tuyet doi** `exp_valframe/capit_events_gate0.3.csv`
  (bao cao 2026-07-29). Ro tai 2026-07-20 tai lap ra **NCT, PNJ, PVT, SAB, SIP, VNM** — dung 5 ten live
  cong PNJ (production loai PNJ bang cong due-diligence `anomaly_flags`, ngoai luat co hoc).
- **Vao lenh T+1** sau ngay tin hieu (quy uoc khong-nhin-truoc cua engine), ro **equal-weight**, bo su
  kien co <3 ten (dung luat `add_capit_arm`).
- **Gia:** `Close` da dieu chinh cho SUAT SINH LOI (§9 skill quant-research); `COALESCE(Price,Close)`
  cho loc thanh khoan — dung nhu production.
- **Chi phi that:** lai vay **12,5%/nam** (hop dong DNSE RocketX `loan_package_id=1840` ghi trong
  `results_registry.md` muc V2.5 — **chua doi chieu ban giay**, xem §7), do nhay 10,0%; phi **0,075%/chieu × 2**.
- **N khai bao trung thuc:** **N = 17 SU KIEN doc lap** trong ky DT5G (2014+), khong phai so dong CSV.
  Voi N nay, walk-forward IS/OOS la sai cong cu → dung **LOO theo su kien + bootstrap** (dung mau ma
  `v2.5-leverage-nogo.md` da dung, theo skill §5).
- **Chong thien lech song sot:** chay **hai** phien ban pool — `ticker_prune` (dung production, nhung
  danh sach thanh vien dung lai cho ca lich su = co look-ahead, da xac nhan o CLAUDE.md changelog
  2026-07-29) va **`tav2_mike.universe_pit`** (thanh vien theo tung ngay). **Moi so o duoi dung ban `universe_pit`.**

**Artifact:** `mike/agents/Taylor/exp_margin_kelly/` — `fetch.py`, `analyze.py`, `robust_pit.py`,
`gates_pit.py`, + `events.csv`, `basket.csv`, `basket_pit.csv`, `events_outcome.csv`, `compare_pit.csv`,
`kelly_oos.csv`.

---

## 3. Ket qua — dieu kien CAN co dat

**x = (loi nhuan ro CAPIT sau 60 phien) − (lai vay 12,5% × so ngay/365) − 2×0,075% phi.**

| Mau | N | TB | Trung vi | %duong | CI90 (TB) | p_boot |
|---|---|---|---|---|---|---|
| **2014+ (ky DT5G), ro `universe_pit`** | **17** | **+9,75%** | +8,28% | 64,7% | [+3,18; +16,61] | **0,013** |
| 2014+, ro `ticker_prune` (co thien lech) | 17 | +10,45% | +11,45% | 70,6% | [+3,73; +17,34] | 0,009 |
| **Thien lech song sot (pit − prune)** | 17 | **−0,70pp** | 0,00 | — | [−2,36; +0,25] | 0,730 |
| Toan bo lich su (2009+), `universe_pit` | 19 | +7,41% | +2,90% | 57,9% | [+0,96; +14,11] | 0,054 |

→ **Dieu kien CAN dat**, va **khong** phai do thien lech song sot (thien lech do duoc, chi −0,70pp,
khong y nghia thong ke).

**LOO theo su kien** (ban `ticker_prune`, chuoi Kelly-tran-1,0x): **bo bat ky su kien nao, TB con lai
van duong** (+6,99pp → +12,14pp). Khong co 1 su kien don le nao ganh het edge — khac han ca V2.5
(nơi 1 episode COVID ganh gan het).

---

## 4. Vi sao van NO-GO — ba mat xich dut

### 4.1 Khong co CONG kich hoat on dinh; cong valuation cua user lam XAU DI

| Cong (2014+, `universe_pit`) | N | TB x | p_boot |
|---|---|---|---|
| G0 moi washout | 17 | +9,75% | 0,013 |
| G1 `state<=2` (CRISIS/BEAR) | 8 | +5,11% | 0,348 |
| **G2 `state>=3` (NEUTRAL+) ← o cua cua 2026-07-20** | 9 | **+13,87%** | 0,006 |
| **G3 `pe_pctile<=0,20`** (cong valuation da validate cua V2.5) | 7 | **+6,16%** | 0,244 |
| G4 `pe_pctile>0,20` (phan bu) | 10 | **+12,26%** | 0,027 |

- **Cong valuation LAM XAU DI**, khong lam tot len: G3 (+6,16) < G4 (+12,26). Trung khop voi ket qua
  da co: `exp_value_radar/v7_washout.py` do 26 su kien CAPIT thay nhan radar **khong phan biet duoc**
  ket cuc (p_perm 0,28-1,00; Spearman radar~r6M/r12M deu khong y nghia). ⇒ **"value_radar bao re" khong
  phai co so du de vay them.**
- **2026-07-20 co `pe_pctile = 0,22`** ⇒ **CHAN** boi chinh cong valuation ma V2.5 da validate (nguong 0,20).
- **Hai truc "conviction" NGUOC NHAU:** theo state, NEUTRAL+ **thang** CRISIS/BEAR (+13,87 vs +5,11);
  nhung theo do sau drawdown, cang SAU cang TOT (`dd52<=−20%`: **+17,62%**, p=0,037; `dd52>−10%`: +2,92%,
  p=0,684). Hai lat cat gan-truc-giao cho ket luan **trai chieu** o N=17 ⇒ dau hieu **chua dinh danh
  duoc tin hieu**, khong phai "co 2 edge". Doi chieu dose-response breadth: **khong don dieu**
  (≥30%: +9,75 | ≥35%: **+3,25** | ≥40%: +8,44 | ≥45%: +11,62) — noise.
- Theo skill §10, **dose-response don dieu la bang chung manh nhat o N nho**. O day chi **truc dd52**
  co hinh don dieu; state va breadth thi khong. Mot truc don dieu tren ba, voi 2 truc mau thuan nhau,
  khong du de chot cong.

### 4.2 Kelly khong phai rang buoc — RUIN moi la

Kelly **ngoai mau** (uoc luong mo rong: tai su kien k chi dung su kien 1..k−1, toi thieu 5 mau —
tranh dung bay kinh dien "fit trong mau roi dung lai chinh mau do"):

- `f* = E[x]/Var(x)` cho **full-Kelly 2,13-3,93× NAV**, **half-Kelly 1,06-1,96× NAV** (trung vi 1,36).
- Half-Kelly 1,36× NAV vay them ⇒ **gross ≈ 2,36×**.
- **MAE xau nhat cua ro CAPIT trong ky giu = −25,1%** (2020-02-03; p10 = −20,2%).

| gross | equity/tai san sau cu MAE −25,1% | maintenance 30% | maintenance 35% |
|---|---|---|---|
| 1,30 | 69,2% | an toan | an toan |
| 1,50 | 55,5% | an toan | an toan |
| 1,80 | 40,6% | an toan | an toan |
| 2,00 | 33,2% | **sat bien** | **MARGIN CALL** |
| **2,36 (= half-Kelly)** | **23,0%** | **MARGIN CALL** | **MARGIN CALL** |

⇒ **Half-Kelly ngoai mau nam BEN KIA lan ruin.** Do nhay ro rang: neu uoc luong `E[x]` sai chi **1/3
xuong duoi** (dieu hoan toan trong CI90 [+3,18; +16,61]), `f*` giam ~1/3 va bai toan tro thanh "vay
0,4-0,7× NAV cho mot ky vong khong phan biet duoc voi 0". Do la dac trung cua Kelly: **f\* tuyen tinh
theo edge nhung edge o day co CI rong gap 4 lan diem uoc luong**. Ket luan nay **trung y nguyen** ket
luan 2026-06-26 ("binding constraint = margin-call ruin, not Kelly") — dat lai bang du lieu moi (ro
CAPIT thay vi lever-at-bottom), cung ket qua.

**Luu y quan trong hon:** MAE −25,1% do tren **ro CAPIT rieng**. Trong thuc te, luc ro CAPIT sut thi
**ca so cung sut** ⇒ equity thuc te giam nhanh hon ⇒ tran gross an toan **thap hon** bang tren.

### 4.3 Tang DANH MUC — noi 3 lan truoc "proxy duong → engine am"

Toi **khong** chay lai engine trong job nay (het ngan sach thoi gian dispatch; noi thang thay vi ngam).
Nhung ket qua tang danh muc **da co san va truc tiep dung chu de**:

- `FORCE_REAL_LEVER=1` (ep vay that tren dung slug CAPIT): gross chi cham 1,000, **Calmar 1,54 → 1,31**.
- Sweep MGE 1,3 → 2,0 voi hold-neutral: **don dieu xau di** 29,32% → 27,97%.
- V2.5 tong the: **OOS −0,05pp**, **DSR 0,18-0,56**.
- Ghi chu meta cua chinh registry (2026-06-27): *"lan thu 3 trong phien nay mot tin hieu duong o tang
  proxy/in-sample that bai o chieu risk-adjusted/duong di (hold-neutral, MGE 2.0, pbcombo)."*

⇒ **+9,75%/su kien o tang vi the la dieu kien CAN, tuyet doi khong phai dieu kien DU.** Lich su o chinh
kho nay noi rang xac suat no song sot qua tang danh muc la **thap**.

---

## 5. Quan sat MOI — dang ghi so (khong doi verdict)

**Tien de cu cua engine khong con mo ta dung tai khoan live.** Ket luan 2026-06-25 ("MGE vay 0 VND vi
luc washout luon con tien nhan roi") do o **NAV 50B** voi cau hinh recovery-park, noi de-risk giai
phong tien mat. Thuc te SpaceX:

| Ngay | NAV | Tien mat | No margin | Off-book |
|---|---|---|---|---|
| 2026-07-20 (ngay tin hieu) | 929,8tr | 3,2tr | 0 | 302,1tr |
| 2026-07-31 | 938,4tr | 14,3tr | ~0 | 0 |

Dot CAPIT tieu **~288tr (~31% NAV)** — dung bang toan bo tien nhan roi off-book. Sau do tai khoan
**~98,5% da dau tu**. ⇒ **Moi don vi CAPIT tang them tu nay chi co the den tu MARGIN.** Co che ma
backtest ket luan la "khong binding" thi **bay gio moi thuc su binding**.

Dieu nay **khong** doi verdict — mat xich yeu la **uoc luong edge/cong kich hoat**, khong phai capacity.
Nhung no la ly do gia thuyet cua user **khong vo ly**, va la ly do de **ghi so theo doi** thay vi dong hop.

---

## 6. Capacity — khong du du lieu de ket luan (noi thang)

Dispatch yeu cau kiem tra suc mua margin kha dung tai cac ngay CAPIT lich su. **Khong lam duoc:**
- `data/plan_buying_power_shadow_log.csv` (P0 shadow, WARN_ONLY) co **dung 1 ban ghi that** (2026-07-29),
  chua toi nguong ≥10 phien de danh gia.
- **SpaceX chua tung co ban ghi `pp0Buy` that** — gap da biet tu truoc (`current_ops.md`), so replay dung
  PROXY `availableCash` = **can duoi**.
⇒ Suc mua margin tai cac washout 2014-2025 **khong do duoc**. Day la gioi han cua bao cao nay, khong
phai ket luan "du suc mua".

---

## 7. Ky luat thong ke + minh bach

- **N_trials trong job nay = 17** (5 cong state/valuation + 6 nguong `dd52` + 4 nguong breadth + 2 leg
  pit-vs-prune). Cong don voi cac phep thu cu tren cung chu de (v7_washout 6, sweep MGE 4+4, ...) thi
  khong gian tim kiem da rat rong — mot ly do nua de doc CI, khong doc diem uoc luong.
- **DSR/PBO: KHONG chay** — theo skill quant-research §13, DSR/PBO chi bat buoc khi **de xuat wire mot
  config cu the**. Ket luan la "khong doi gi" ⇒ khong co config nao duoc chon ⇒ DSR/PBO khong ap dung.
  Neu sau nay co ai muon dua 1 cau hinh don bay len production, **DSR/PBO tro thanh bat buoc truoc do**.
- **quant-skeptic: khong dispatch** — khong de xuat thay doi production nao (skill §15). **Neu** ai muon
  bien §5 thanh mot buoc thu nghiem thuc te, quant-skeptic tro thanh bat buoc.
- **Chi phi vay 12,5%/nam CHUA doi chieu hop dong DNSE** (`coding_guidelines.md` §6 "estimated margin
  accrual"). Do nhay o 10,0%/nam **khong doi ket luan** (+9,75% → +10,3%).
- **ZaloPay cash-only** — moi so o day chi ap dung **SpaceX**, khong lan.
- **Production sach:** `git diff` tren `pt_v23_audit_2014.py`, `macro_state_live.py`,
  `deploy_golive_dt5g_v4/golive_recommend_v23.py`, `rating_8l.py`, `data/trading_rules.json` = **rong**.
  Khong bat margin cho CAPIT, khong sua rule nao.
- **Loi da tu bat va sua trong job:** ban dau `analyze.py` cat 2014+ bi lech nhan index sau
  `reset_index()` (cho ra G2 = +3,53% N=6). So DUNG nam o `gates_pit.py` (dung lai tu `compare_pit.csv`,
  N=9, +13,87%). **Moi so cong kich hoat trong bao cao nay lay tu `gates_pit.py`.**

---

## 8. VERDICT theo tung kich ban

| # | Kich ban | Dieu kien kich hoat do duoc | Verdict |
|---|---|---|---|
| **S1** | Vay margin + **Kelly** vao arm CAPIT (dung y user) | washout gate 0,30 ∧ Kelly `f*=E[x]/Var(x)` ngoai mau | 🔴 **NO-GO** — half-Kelly (1,06-1,96× NAV) **vuot tran ruin** (gross 2,36 ⇒ margin call ngay tai MAE lich su −25,1%). Kelly-lever da bi bac 2026-06-26 vi dung ly do. |
| **S2** | Vay margin **co dieu kien valuation** (value_radar/8L re) | washout ∧ `pe_pctile<=0,20` (hoac nhan radar RE) | 🔴 **NO-GO** — cong nay **lam xau di** (+6,16% vs +12,26% phan bu); radar tai washout da do la khong phan biet duoc ket cuc. **2026-07-20 (`pe_pctile=0,22`) bi chinh cong nay CHAN.** |
| **S3** | Vay margin o washout **NEUTRAL** (dung o cua 2026-07-20), don bay CO DINH 1,3x | washout ∧ `state>=3` | 🔴 **NO-GO (chua du bang chung, khong phai da bac)** — tang vi the manh nhat o cell nay (+13,87%, p=0,006, N=9) NHUNG (a) mau thuan truc dd52, (b) chua qua tang danh muc, (c) cung ho co che da NO-GO o V2.5. |
| **S4** | Vay margin o washout **SAU** (`dd52<=−20%`), don bay co dinh 1,3-1,5x | washout ∧ `dd52<=−20%` | 🟡 **CONDITIONAL — ung vien DUY NHAT dang test tiep, chua phai GO.** La truc **duy nhat** co dose-response don dieu (`≤−20%`: +17,62% p=0,037; `>−10%`: +2,92% p=0,684) va nam **trong** tran ruin an toan (gross 1,5 ⇒ equity/ts 55,5% sau MAE xau nhat). **Nhung N=6** va **chua chay tang danh muc**. **KHONG duoc trich nhu edge.** |

**Luu y cho S4:** no **khong** mo ra cua cho 2026-07-20 (`dd52 = −9,6%` ⇒ **CHAN**). Tuc la ngay ca ung
vien tot nhat cung **khong** ung ho hanh dong ma user hoi.

---

## 9. Buoc tiep theo cu the (neu user muon di tiep)

1. **Tang danh muc cho rieng S4** — chay `pt_v23_audit_2014.py` cau hinh production R3 hien hanh
   (`LAG_ADV_BASIS=price`, `PARK_STATES="3:0.7"`, `NAV_TOTAL_B=50`, `threads=1`, `$DNA_PYEXE`) voi
   `MGE=1.3/1.5 MGE_CAPIT_ONLY=1 FORCE_REAL_LEVER=1` + cong `dd52<=−20%`, doi chieu chan control tai
   lap **dung** 28,86%. **Gate:** OOS duong ∧ DSR ≥0,95 ∧ MaxDD khong xau di. Neu rot bat ky cai nao →
   dong han huong margin-washout.
2. **Do capacity that** — de P0 shadow log chay du ≥10 phien va **lay cho duoc `pp0Buy` that cua SpaceX**
   (gap da biet). Khong co so nay thi moi ban ve "vay bao nhieu" van la gia dinh.
3. **Cho `CAPIT-2026-07-20` du 60 phien** (~2026-10-15) roi cham diem su kien nay vao phan phoi §3 —
   them 1 quan sat that vao N=17. Re, khach quan, khong ton gi.

*(Muc 2-3 la thu thap du lieu, khong phai thu nghiem tien that. Muc 1 la R&D paper, khong dung tien that.)*

---

## 10. Doi chieu voi cac ket luan lan can (skill §12)

- **"CAPIT co lam an duoc khong?"** — CO (+9,75%/su kien o tang vi the). Khong mau thuan voi viec
  **khong nen VAY** de lam nhieu hon: von **equity** con nhan roi thi trien khai duoc voi rui ro huu han;
  von **VAY** them mang theo (a) chi phi carry, (b) rui ro cuong che ban tai dung day, (c) tuong tac
  duong di voi ca so. Chenh lech giua "dang lam" va "nen vay de lam nhieu hon" nam o (b)+(c), khong
  nam o ky vong loi nhuan.
- **Bao cao 2026-07-29 (`fundamental_valuation_framework`)** ket luan valuation tai CAPIT co tin hieu
  (tercile PB re r12M +20,4% vs dat +5,6%) nhung **0/56 qua BH** → NO-GO tilt. Bao cao nay **nhat quan**:
  cung tim thay valuation khong dung duoc lam cong, va manh hon — o dinh dang "vay theo valuation" thi
  cong valuation **dao dau** (G3 < G4).
- **`lag-adv-filter-tracking.md`** dang mo voi moc cung 2026-12-15/2027-03-31 — khong lien quan truc tiep,
  nhung cung tinh than: **khong ket luan khi so lieu chua du**, ghi so va cho.

---

## 11. Tra loi thang cau hoi cua user

> *"Dot washout nay la luc nen vay margin de tang ty trong theo Kelly, thay vi dung nhin — dung khong?"*

**Truc giac dung o cho: co that mot phan thuong o day** (mot dong von vay bo vao ro CAPIT trong 60 phien
lich su lai +9,75% sau chi phi vay, N=17, p=0,013 — va khong phai ao anh song sot). **Nhung ba dieu can,
khong cai nao dat:**

1. **Khong biet luc nao nen vay.** Cong ma truc giac de xuat (valuation re) **lam xau di**, khong lam tot len
   — va chinh no **chan** ngay 2026-07-20. Truc duy nhat con hinh dang tin duoc (`dd52<=−20%`) cung **chan**
   ngay nay (`−9,6%`).
2. **Kelly noi so lon hon muc song sot duoc.** Half-Kelly ngoai mau = gross 2,36× ⇒ **margin call ngay tai
   cu sut xau nhat da tung xay ra** cua chinh ro nay. Kelly gia dinh biet chinh xac edge; o day CI cua edge
   rong gap 4 lan diem uoc luong.
3. **Tang danh muc da tra loi 2 lan roi va deu la khong** — voi ly do khong phai "so rui ro" ma la do duoc:
   OOS −0,05pp, DSR 0,18-0,56, va don bay cao hon **don dieu xau di**.

**Dieu dang lam thay vi bat margin:** cho `CAPIT-2026-07-20` du 60 phien roi cham diem no vao phan phoi
tren (mien phi, khach quan), do cho ra suc mua margin that cua SpaceX, va **neu** muon test tiep thi test
dung S4 (`dd52<=−20%`, don bay co dinh, khong Kelly) o tang danh muc voi gate DSR ≥0,95.
