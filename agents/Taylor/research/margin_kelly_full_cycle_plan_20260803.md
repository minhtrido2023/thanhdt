# KE HOACH THI NGHIEM — do hieu qua margin qua CA CHU KY (tra loi phe binh phuong phap luan cua user)

**Job** `Taylor_20260803_082241` · **Ngay** 2026-08-03 · **Loai: PLAN-ONLY** (job nay KHONG chay BQ/backtest nao)
**Noi tiep** `margin_kelly_feardriven_washout_20260803.md` (p1) + `_p2.md` (p2). Ke hoach nay la
DELIVERABLE de Mike dispatch buoc thuc thi ma khong can hoi lai.

---

## 0. Phe binh cua user dich thanh 3 menh de DO DUOC — va thua nhan cho p1/p2 thieu

User noi: *"margin lam maxDD cao len, nhung neu do qua MOT CHU KY thi hieu qua vuot troi neu nam bat
duoc ty le thanh cong; xac suat thanh cong cao thi loi nhuan % duoc NHAN LEN nhieu qua compounding."*

Dich thanh 3 menh de kiem chung duoc:

- **M1**: metric dung cho don bay lap lai nhieu lan la **toc do tang truong hinh hoc (geometric
  growth) cua von qua CA CHUOI su kien**, khong phai ky vong/rui ro cua 1 lan cuoc don le.
- **M2**: mot **chinh sach vay CO DINH ap dung xuyen suot** (khong bi tien mat san co "hut" mat nhu p2)
  co the cho terminal wealth vuot troi phien ban khong vay — can do PHAN PHOI terminal wealth, khong
  phai 1 con so diem.
- **M3**: voi thong ke da do (N=17, TB +9,75%, 64,7% duong, p_boot 0,013), cau hoi "nhan len co dang
  khong" co dap so DINH LUONG — khong duoc tra loi dinh tinh.

**Thua nhan thang cho ho cua p1/p2** (phe binh CO CO SO):
1. p1 tinh Kelly `f*=E[x]/Var(x)` tren TUNG su kien va bac bo bang 1 tinh huong MAE toi te nhat ap vao
   1 thoi diem — do la phep thu "ruin 1 lan cuoc", KHONG phai "xac suat song sot + toc do tang truong
   qua 12 nam cua mot chinh sach co dinh". Kelly goc (Kelly 1956, Thorp) toi uu E[log growth] qua
   CHUOI cuoc lap lai — p1 chua bao gio tinh dai luong nay.
2. p2 do dung tang danh muc nhung phat hien phep do KHONG cham toi don bay (5-9% thuc vay) — tuc la
   cau hoi cua user **chua tung duoc do that**, khong phai da bi bac. Bao cao p2 tu noi dieu nay
   (§1.5: "khong co bang chung moi ung ho lan bac bo").
3. Chua co phep do nao dung terminal wealth distribution / MC bootstrap tren chuoi su kien.

**Dong thoi giu nguyen ky luat**: ke hoach nay KHONG ha chuan. Moi gate quyet dinh duoc DANG KY TRUOC
o §5 — job thuc thi bi cam doi gate sau khi thay so.

---

## 1. Metric DUNG cho "hieu qua qua ca chu ky" (tra loi cau 1 cua dispatch)

### 1.1 Dai luong trung tam: g(f) — toc do tang truong hinh hoc theo he so don bay f

Cho chuoi su kien washout i = 1..N (N=17, 2014+, ro `universe_pit`, ket cuc 60 phien — Y NGUYEN tap
cua p1, khong dinh nghia lai). Goi:
- `r_i` = loi nhuan tho cua ro CAPIT su kien i sau 60 phien (cot `r` trong `events_outcome.csv` —
  KHAC cot `x`; `x` da tru lai vay cua 1 dong von vay, khong dung duoc lam nguyen lieu cho f khac 1).
- `d_i` = so ngay lich nam giu (cot `cal_days`).
- `c` = lai vay/nam (12,5% base; 14% adversarial), `phi` = 0,075%/chieu × 2.

**Loi nhuan tren VON TU CO (equity) cua sleeve khi dung don bay gop f** (f = tong tai san / von tu co,
f=1 la khong vay):

```
R_i(f) = f · (r_i − phi) − (f − 1) · c · d_i/365        [neu khong cham margin call]
```

**Toc do tang truong hinh hoc**: `g(f) = (1/N) · Σ log(1 + R_i(f))`, va terminal wealth qua chuoi
lich su = `W_N(f) = Π (1 + R_i(f))`.

Day chinh la ham muc tieu goc cua Kelly. Tinh chat then chot lam no KHAC voi moi metric p1/p2 da dung:
`log` phat nang loss lon phi tuyen (compounding drag ~ f²·Var/2), va **margin call la trang thai hut
(absorbing)** — mot lan bi cuong che ban gan day lam mat vinh vien phan von, khong "trung binh bu lai"
duoc. CAGR/Sharpe diem-cuoi cua ca he KHONG nhin thay dieu nay vi sleeve chi chiem ~30% NAV va cac
episode thua/thang bi tron lan.

### 1.2 Margin call la RANG BUOC DUONG DI, khong phai dieu chinh diem cuoi

Trong moi su kien, kiem tra HANG NGAY (dung duong gia that tu `px_pit.parquet`, EW rebalance-free):
- Tai san ngay t: `A_t = f · (1 + path_i(t))` ; No: `L_t = (f−1)·(1 + c·(t−t0)/365)` ; Equity `E_t = A_t − L_t`.
- Neu `E_t / A_t < maint` (30% base / 35% adversarial) → **cuong che ban tai close ngay t+1 voi penalty
  slippage** (1% base / 2% adversarial — ban vao ngay hoang loan, khong duoc gia mid). Su kien do ket
  thuc bang equity con lai, KHONG duoc dung `r_i` diem cuoi nua.

p1 da co MAE per-event (xau nhat −25,1%) nhung chi dung diem MAE; o day dung ca duong di de lai vay
tich luy + thoi diem call + gia thanh ly deu that.

### 1.3 Phan phoi thay vi con so diem — Monte Carlo bootstrap THEO KHOI su kien

- **Path lich su thuc** (1 duong duy nhat, thu tu that): bao cao rieng, la con so "chuyen gia doc dau tien".
- **Bootstrap**: resample co hoan lai de tao B=10.000 chuoi gia lap do dai N, tinh phan phoi
  `W_N(f)`, `g(f)`, P(ruin). **Bat buoc chay CA HAI phuong an don vi resample**:
  (a) iid tung su kien; (b) **theo KHOI** — su kien cach nhau <6 thang la 1 khoi (2020-02/03/07 la 1
  khoi; 2022-04/06/09 la 1 khoi; ...) vi ket cuc cac su kien lien ke tuong quan (cung 1 con gau).
  iid danh gia THAP rui ro chuoi thua lien tiep; khoi giu duoc cluster. **Neu ket luan doi chieu giua
  (a) va (b) → doc la FRAGILE, gate that bai** (dang ky truoc, §5).
- Voi N=17, bootstrap cho ta phan phoi cua uoc luong — KHONG phai phan phoi that cua tuong lai. Bao
  cao phai noi ro han che nay; do cung la ly do gate dat o percentile 5 va P(ruin), khong dat o trung vi.

### 1.4 Vi sao KHONG dung CAGR/Sharpe/DSR diem-cuoi lam gate o tang nay

- CAGR/Sharpe cua ca he (nhu p2) pha loang sleeve vao 100% NAV → khong tach duoc cau hoi cua user.
- DSR van BAT BUOC **neu** sau nay de xuat wire 1 config (§5), nhung DSR do "chuoi tong the co phai
  san pham do tham so khong", khong do "chinh sach vay co toi uu hinh hoc khong" — 2 cau hoi khac nhau,
  can ca hai, khong thay the nhau.

---

## 2. Co che de DON BAY THUC SU kich hoat (tra loi cau 2) — thiet ke SO KE TOAN VE TINH (satellite ledger)

Bai hoc p2: di qua engine thi `MGE` bi tien mat/parking hut mat (91-95% la tai phan bo). De do DUNG
cau hoi cua user, tach sleeve ra mot so ke toan rieng voi **chinh sach vay BAT BUOC, khong tuy nghi**:

- **Chinh sach V(f)**: tai MOI su kien washout (T+1 close), sleeve vay dung `(f−1) × equity_sleeve`
  tai lai suat c, mua ro PIT equal-weight, giu 60 phien (hoac den margin call), ban, tra no + lai.
  KHONG co dieu kien "neu con tien thi dung tien" — day chinh la diem khac p2, va la CO Y: ta muon do
  chinh sach vay, khong phai do thoi quen dung tien nhan cua engine.
- **Luoi f**: {1,0 (control); 1,1; 1,2; 1,3; 1,5} — tran 1,5 lay tu bang ruin p1 §4.2 (gross 1,5 ⇒
  equity/tai san 55,5% sau MAE lich su xau nhat, con cach xa maint 35%). **KHONG test f≥1,8** — da biet
  truoc la vuot tran ruin, test them chi tang N_trials vo ich.
  + 1 chan **fractional-Kelly co tran**: `f_k = min(1 + 0.25·(f*_oos − 1), 1.5)` dung `kelly_oos.csv`
    (uoc luong mo rong, chi dung qua khu) — de tra loi truc tiep "Kelly co dung duoc khong neu chiu
    cat con 1/4 va doi tran".
- **Giua cac su kien**: 2 bien the, ca hai deu bao cao:
  (i) sleeve nam im (do THUAN hieu ung compound cua chuoi cuoc — dung nghia cau hoi Kelly);
  (ii) **tich hop toan so** (§2.1) — day moi la bien the QUYET DINH.

### 2.1 Bien the QUYET DINH: tich hop toan so (whole-book overlay)

Nguoi cho vay (DNSE) nhin **toan tai khoan**, khong nhin sleeve. Va khi ro CAPIT sut thi ca so cung
sut (bay tuong quan, cau 4 dispatch). Cach do:

- Lay chuoi NAV ngay cua chan L0 control (CSV `..._exp_s4p2_L0_control_univpit.csv` + `dsr_pbo_annex.load_nav`
  — da tai lap TUYET DOI pin 28,86%) lam "phan con lai cua so".
- Overlay P&L sleeve (co vay) len: `NAV_tong(t) = NAV_L0(t) + P&L_sleeve(t)`; sleeve size = dung luat
  production `NAV_book_LAG × capit_size` (user da chot 07-20), KHONG chon size tuy y.
- **Maintenance check tren TOAN tai khoan**: `E_tong/A_tong` — day la cach broker cuong che that.
  Luu y trung thuc 2 chieu: (a) toan-so lam margin call KHO xay ra hon sleeve-alone (phan 70% con lai
  la dem) → co loi cho phe "margin tot"; (b) nhung tuong quan sleeve↓ ∧ so↓ lam equity tong giam nhanh
  hon phep do sleeve-alone → bat loi. Phai bao cao CA HAI muc do (sleeve-alone va toan-so), khong duoc
  chi chon muc co loi.
- Metric quyet dinh o tang nay: ΔCAGR toan-so, ΔMaxDD toan-so, LOO per-year, va **P(margin call toan
  so) = 0 tren path lich su / ≤1% bootstrap adversarial**.

### 2.2 Tran ky vong — tinh truoc de khong tu lua (expectation bound, thuan so hoc)

Sleeve ~31% NAV (episode 07-20 thuc te). f=1,5 ⇒ phan MUA THEM bang vay = 0,5 × 31% ≈ 15,5% NAV,
song ~60 phien/su kien × ~1,4 su kien/nam ≈ 1/3 nam. Loi the rong da do +9,75%/su kien ⇒ dong gop
TRAN (khong drag, khong ruin, khong tuong quan):
`0,5 × 31% × 9,75% × 1,4 ≈ +2,1pp CAGR/nam`. Con so THUC se thap hon do variance drag + nhung nam
khong co su kien. **Ai doc ket qua phai neo vao tran nay**: day la quyet dinh co bien do +1..2pp/nam,
KHONG phai thu "vuot troi" gap ruoi gap doi — neu mo phong ra so vuot tran nay thi mo phong SAI o dau
do, phai dung lai tim loi (guard tu dong, §4).

---

## 3. Phep tinh "xac suat thanh cong co du de nhan len khong" (tra loi cau 3) — BUOC A, re nhat, lam TRUOC

Truoc khi mo phong duong di, tinh giai tich tren 17 gia tri `r_i` da co (thuan Python, vai phut):

1. **Duong cong g(f)** cho f ∈ [1,0; 2,5] buoc 0,05, voi margin-call overlay xap xi bang MAE per-event
   (da co san cot `mae`): su kien i bi call tai f neu `(1 + f·mae_i − (f−1)) / (f·(1+mae_i)) < maint`
   → thay `R_i(f)` bang equity thanh ly. Ve/bang: `f*_geo = argmax g(f)`, va `f_break` = f lon nhat
   ma `g(f) ≥ g(1)`.
2. **CI cua g(f)** bang bootstrap 17 diem (iid + khoi) — tra loi "voi CI rong nhu da do (edge
   [+3,18; +16,61]), f toi uu hinh hoc nam o dau, va co chac chan > 1 khong".
3. **Chan adversarial**: tinh lai voi `E[r]` keo ve can duoi CI90 (shrink toan bo phan phoi xuong
   −6,6pp) — Kelly voi edge uoc luong sai la nguon ruin kinh dien (p1 da noi dung; o day dinh luong hoa).

**Y nghia quyet dinh cua buoc A**: neu `f*_geo ≤ 1` hoac `P_boot(g(1,3) > g(1,0)) < 0,90` thi cau tra
loi cho user la dap so toan hoc sach se — *"voi ty le thang 64,7% va bien do lai/lo NAY, phep nhan
hinh hoc noi KHONG nen vay"* — va dung o do, khong can buoc B/C/D. Nguoc lai thi di tiep. Framing
chuyen gia: nha quan ly quy gioi khong phai nguoi dam vay khi nguoi khac so — la nguoi tinh dung
`f*` va chap nhan ca khi dap so la "khong vay"; dat cuoc co tinh toan nghia la CON SO quyet, khong
phai su gan da.

---

## 4. Guard chong bay DA BIET (tra loi cau 4 — bat buoc nhac lai)

| # | Bay | Guard cu the trong thiet ke |
|---|---|---|
| 1 | Look-ahead `profit_*` | Moi ket cuc tinh tu duong gia `px_pit.parquet` (fetch tu `Close` lich su), KHONG cham cot `profit_*`. Vao lenh T+1 sau ngay tin hieu (giu quy uoc p1). |
| 2 | Selection bias kieu §2.4-p2 ("doi xac nhan giam MAE" = ao anh loai mau) | Ke hoach nay KHONG co gate dieu kien nao loai su kien — chinh sach V(f) ap dung cho MOI su kien washout, cung tap 17 su kien o moi f. So sanh giua cac f luon tren CUNG TAP. Margin call KHONG loai su kien khoi mau — no thay ket cuc bang ket cuc thanh ly (te hon), nguoc huong voi bay selection. |
| 3 | N_trials | Khai bao TRUOC: 5 muc f × 2 maint × 2 lai suat × 2 don vi bootstrap × 2 pham vi ledger (sleeve/toan-so) + 1 chan fractional-Kelly + 2 bien the idle ≈ **~40 cell**, trong do **2 cell quyet dinh** (f=1,3 va f=1,5, toan-so, adversarial); phan con lai la sensitivity khai bao san. Cong don chu de margin+Kelly voi p1+p2: 44 + ~40. Job thuc thi CAM them cell ma khong ghi tang N_trials. |
| 4 | DSR/PBO | Chi bat buoc NEU buoc D de xuat 1 config wire (skill §13). PBO tinh tren ho {f} neu den buoc do. Ghi ro: DSR tren NAV toan-so KHONG tach duoc dong gop sleeve (bai hoc p2 §3) — phai doc kem Δ so voi control. |
| 5 | universe_pit vs ticker_prune | Ro su kien dung `basket_pit.csv` (universe_pit) lam headline — thien lech prune da do o p1 (−0,70pp, khong y nghia) nhung van chay prune lam sensitivity, khong lam so chinh. |
| 6 | Tuong quan voi drawdown ca so | Chinh la ly do ton tai bien the toan-so §2.1: maintenance tinh tren tong tai khoan voi NAV_L0 that (khong gia dinh doc lap). Them 1 bang chan doan: trong 10 ngay MAE sau nhat cua sleeve, NAV_L0 thay doi bao nhieu (do tuong quan thuc nghiem, bao cao thang). |
| 7 | Lai suat 12,5% chua doi chieu hop dong | Van chua doi chieu (ke thua p1 §7) — chay ca 14%/nam lam adversarial. Neu ket luan doi dau giua 12,5% va 14% → doc la FRAGILE. |
| 8 | 2 su kien chua du 60 phien (2026-03-09 outcome ngan, 2026-07-20 chua co) | Giu dung tap 17 su kien co ket cuc day du cua p1. 2026-07-20 cham diem sau ~2026-10-15 (viec da ghi so o p1 §9.3), KHONG dua vao mo phong bay gio. |
| 9 | Bay `MGE_GATE` im lang (p2 §1.4) | Buoc D (neu chay) dung ban sao `engine_dd52.py` da va loi, KHONG dung `MGE_GATE` cua production khi `RECOVERY_PARK` tat. |
| 10 | So vuot tran ky vong §2.2 | Bat ky cell nao cho ΔCAGR toan-so > +2,1pp/nam → tu dong nghi van, dung lai audit truoc khi bao cao (khong phai "tin tot"). |

---

## 5. GATE QUYET DINH — dang ky TRUOC khi chay (job thuc thi khong duoc sua)

Doc theo thu tu; rot gate nao dung o gate do.

- **G-A (buoc A, giai tich):** `f*_geo > 1,0` VA `P_boot(g(1,3) > g(1,0)) ≥ 0,90` o ca iid LAN khoi,
  tai lai suat 12,5%. Rot → **NO-GO chung cuoc**, dap so toan hoc, bao cao va dong.
- **G-B (buoc B, duong di sleeve):** tren path lich su thuc: **0 margin call** tai f ≤ 1,5 (maint 35%,
  lai 14%, penalty 2%); bootstrap khoi: `P(ruin) ≤ 1%`. Rot tai f nao → loai f do; moi f rot → NO-GO.
- **G-C (buoc C, toan-so):** ΔCAGR > 0 o CA IS (2014-19) lan OOS (2020+); ΔMaxDD toan-so ≤ +1,0pp
  (xau di khong qua 1pp); LOO per-year: khong co 1 nam nao ganh ≥50% tong edge; 0 margin call toan-so
  tren path lich su adversarial.
- **G-D (chi khi A-C deu PASS):** xac nhan tang engine (1-2 run) + **DSR ≥ 0,95 tren config duoc chon
  + PBO ho {f} + quant-skeptic CONFIRMED**. Va ke ca PASS het: **van chua duoc wire** — con thieu
  capacity that (`pp0Buy` SpaceX + P0 shadow ≥10 phien, van la gap mo tu p1 §6) va **duyet cua user**.
  Deliverable cua ca chuoi toi da la "candidate da kiem chung cho quyet dinh cua user", khong hon.

**Meta-gate trung thuc:** neu ket qua iid va khoi, hoac 12,5% va 14%, cho ket luan NGUOC nhau o bat ky
gate nao → ket luan chung la INCONCLUSIVE-FRAGILE, xu ly nhu NO-GO (khong chon phuong an dep hon).

---

## 6. TU PHE BINH ke hoach nay — cach no co the thien vi "margin tot" va cach phat hien (tra loi cau 5)

1. **Thiet ke satellite-ledger CO Y go bo co che cash-priority** — dung co che do lam engine khong vay
   (p2), va backtest @50B luon co parking de dich. Do sleeve co lap se PHONG DAI loi ich vay so voi
   tai khoan mo phong 50B. *Phat hien/xu ly*: bien the toan-so (§2.1) la so quyet dinh, sleeve-alone
   chi la chan doan; dong thoi ghi ro tension nguoc lai — tai khoan LIVE (98,5% da dau tu, p1 §5)
   giong the gioi "phai vay" hon the gioi backtest, nen khong duoc dung lap luan "backtest khong can
   vay" de gat bo cau hoi, cung khong duoc dung so sleeve-alone de tra loi no. Bao cao PHAI in ca hai
   va noi ro con so nao tra loi cau hoi nao.
2. **MC dung lai 17 draw da biet la duong (+9,75%)** — resample tu mau duong thi trung vi terminal
   wealth gan nhu CHAC CHAN tang theo f o muc vua. Neu de trung vi lam headline thi ket luan "margin
   tot" da duoc dinh san tu truoc khi chay. *Phat hien/xu ly*: gate CHI dat o duoi tail (pct-5, P(ruin),
   MaxDD, LOO) — trung vi bao cao nhung phi-quyet-dinh (dang ky ngay tai day).
3. **Day la vong 3 tren CUNG bo du lieu 17 su kien** — moi vong them lens moi la garden-of-forking-paths
   o tang meta; ap luc "user muon thay ket qua khac" la mot dang motivated reasoning nguoc voi 2 job
   truoc. *Phat hien/xu ly*: gate dang ky truoc trong file nay; bao cao cuoi bat buoc ghi cau "vong 3
   tren cung du lieu, N_trials cong don ~84+"; quant-skeptic review bat buoc BAT KE ket luan chieu nao
   (ke ca NO-GO lan nua — de bat ca thien vi chieu nguoc lai: bac bo cho nhanh de khoi phai lam tiep).
4. **Lua chon khoi bootstrap / maint / penalty / lai suat** deu co the chon vo tinh theo huong dep.
   *Phat hien/xu ly*: moi tham so co chan adversarial dang ky san (35% / 2% / 14% / edge-shrink can
   duoi CI90); meta-gate FRAGILE o §5 bat truong hop ket luan phu thuoc lua chon.

---

## 7. NGAN SACH THUC THI (tra loi cau 6) — cho Mike dispatch

| Buoc | Viec | Du lieu | BQ? | Goi y model/effort |
|---|---|---|---|---|
| **A** | Duong cong g(f) + bootstrap + adversarial (§3) | `events_outcome.csv` (co san `r`, `mae`, `cal_days`) | **KHONG** | Sonnet / medium. ~1 script ~150 dong. Nhanh. |
| **B** | Sim duong di sleeve, daily MTM + margin call (§1.2, §2) | `px_pit.parquet` (da phu 2008→2026-08-03), `basket_pit.csv`, `events.csv` | **Hau nhu khong** — kiem `set(ticker basket_pit) ⊆ set(px_pit)`; thieu ten nao thi 1 query nho top-up | Sonnet / high (hoac Opus / medium). Phan nang nhat ~300-400 dong Python, khong can engine. |
| **C** | Toan-so overlay + LOO + bang tuong quan (§2.1) | `data/v23_..._exp_s4p2_L0_control_univpit.csv` + `dsr_pbo_annex.load_nav` (da co) | **KHONG** | Cung job voi B. |
| **D** | (Chi khi A-C PASS) xac nhan tang engine 1-2 run + DSR/PBO + quant-skeptic | snapshot `bq_cache_asof20260729_postrestate`, `engine_dd52.py` | Cache dong cung, khong BQ live | Opus / high. ~30-60'/run. KHONG can fable. |

A+B+C gop duoc thanh **1 dispatch duy nhat** (Sonnet/high la du; Opus/medium neu muon chac). Fable
KHONG can cho thuc thi — thiet ke da chot o day, phan con lai la code may moc + doc gate co san.
Moi output ghi vao `exp_margin_kelly/p3/` voi `EXP_TAG` (§8 coding_guidelines), khong cham canonical.

**Dieu kien dung som tiet kiem nhat**: chay A truoc trong dispatch; A rot G-A thi dung ngay, bao cao
NO-GO toan hoc — khong dot budget vao B/C/D.

---

## 8. Ranh gioi (ke thua dispatch, nhac de job thuc thi khong truot)

- KHONG sua production, KHONG bat margin live, ZaloPay (cash-only) ngoai pham vi.
- Moi ket luan chi ap dung SpaceX ve mat khai niem; wire thuc te bi chan boi capacity data + user.
- `profit_*` khong duoc dung lam filter o bat ky buoc nao.
- Gate §5 la bat bien cua chuoi thi nghiem nay; sua gate = job moi + khai bao lai N_trials.
