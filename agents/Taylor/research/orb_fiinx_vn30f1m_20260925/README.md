# VN30F1M 1-phut tu FiinProX (FiinX MCP) — mo rong backtest ORB ve 2022-02-17

Job `Taylor_20260925_111203`, VIEC 0. PAPER-ONLY, khong cham tien that.

## 1. FiinX CO du lieu VN30F1M — nhung chi tu 2022-02-17

`client.TickerList(tickers=["FU"])` liet ke DU hop dong thang tu `VN30F1708` (2017-08)
den `VN30F2512`, cong chuoi lien tuc `VN30F1M/2M/1Q/2Q`. Ten hop dong co day du ca 9 nam.

**Nhung bar 1 phut thi khong.** Do bang cach do truc tiep (`Fetch_Trading_Data`, `by="1m"`):

| Ngay do | rows | |
|---|---|---|
| 2018-01-02 (`VN30F1M` va `VN30F1801`) | 0 | khong co |
| 2020-03-09 (COVID), 2020-06/12, 2021-03/06/09/12 | 0 | khong co |
| 2022-01-14, 2022-01-24, 2022-02-08, 2022-02-15, **2022-02-16** | 0 | khong co |
| **2022-02-17** tro di | 257 | CO |

=> **Bien 1m = 2022-02-17.** Khong lay duoc sut 2018 lan sap COVID 2020. LAY DUOC bear 2022.
Doan moi: 2022-02-17..2023-09-08 = **389 phien**, truoc do vnstock khong co (vnstock bat dau
2023-09-11). Tape ghep: **1.142 phien 2022-02-17..2026-09-25** (truoc: 754).

## 2. Cung mot instrument/tape? — CO, da do tren 76 phien trung nhau

| Dai luong | Khop | maxabs | bias |
|---|---|---|---|
| `c_first` (close bar 09:00) | 76/76 | 0 | 0 |
| `entry` (close bar cuoi <=09:30) | 76/76 | 0 | 0 |
| `maxhigh` sau 09:30 | 76/76 | 0 | 0 |
| `exit` bar cuoi <=14:29 | 44/76 | 3,2d | −0,07d |
| `exit` bar cuoi <=14:30 | 7/76 | 10,0d | +0,04d |

**Quirk vendor (da tim ra nguyen nhan, khong phai khac tape):** FiinX thu gon bar **14:30**
ve MOT gia (`o=h=l=c` = gia dau bar), vnstock giu OHLC day du. Vi du 2023-09-11: vnstock
14:30 = `o1224.1 h1226.7 l1224.1 c1226.5 vol184`; FiinX = `1224.1/1224.1/1224.1/1224.1 vol184`
— **cung volume 184**, chi OHLC bi thu gon. Cac bar khac khop tung bar (da doi chieu
09:28-09:33, 11:28-13:02, 14:25-14:29).

Khac biet thu hai: FiinX **fill bar khong co lenh** (volume=0) nen 257 bar/phien, vnstock bo
nen 241-243. Khong anh huong entry/exit (da do o tren).

**Anh huong o muc KET QUA CHIEN LUOC** (chay chinh config deploy tren cung 75 trade trung nhau):
sig khac nhau **0/75**; mean FiinX +9,93bps vs vnstock +9,35bps (delta +0,58bps), Sharpe 1,54
vs 1,45. Nhieu vendor **~0,6bps**, nho hon 1 bac do lon so voi hieu ung tim thay o §3 (~13bps)
=> doan mo rong dung duoc.

Vi bar 14:30 bi hong ben FiinX, **bao cao chinh dung exit 14:29 cho CA HAI doan** (dong quy
uoc). Do lon cua chinh quy uoc do, do tren doan vnstock (co ca 2 cot): Sharpe 1,57 (14:29) vs
1,58 (14:30) — khong dang ke.

## 3. Ket qua: edge KHONG ton tai o doan moi

Config DANG DEPLOY (`orb_pt.py`: OR den 09:30, sign(or_ret), exit cuoi phien, khong stop,
khong loc |OR|, slip 1 tick/chieu + fee 0,6bps), exit 14:29:

| Doan | n | WR | mean | Sharpe | cum | MaxDD | t |
|---|---|---|---|---|---|---|---|
| **MOI** FiinX 2022-02..2023-09 | 384 | 48,4% | **+0,40bps** | **+0,05** | −2,14% | **−30,47%** | +0,06 |
| CU vnstock 2023-09..2026-09 | 745 | 52,6% | +9,13bps | +1,57 | +91,29% | −7,79% | +2,71 |
| **GOP** 2022-02..2026-09 | 1.129 | 51,2% | +6,16bps | **+0,89** | +87,19% | **−31,78%** | +1,88 |

Theo nam: 2022 +21,9% (Sh 1,01) · **2023 −14,2% (Sh −0,95)** · 2024 +11,1% · 2025 +28,5% ·
2026 +25,4%. Tach 2023: **2023-01..09 (FiinX) −12,99bps/phien, Sharpe −2,10, cum −19,7%**;
2023-09..12 (vnstock) +9,35bps. Drawdown sau nhat doan moi: **−30,47% tu 2022-10-27 den
2023-09-06, keo dai 206 phien** — ket thuc dung 3 phien truoc khi tape cu bat dau.

**DSR/PSR tren mau ghep 1.129 trade** (truoc: 745 trade): PSR(SR*=0) **0,9679** (truoc 0,9967);
**DSR(N=20) 0,4914** (truoc 0,9234). Duoi nguong fleet 0,95 rat xa.

## 4. Doc ket qua nay the nao

- Khac biet 2 doan **khong co y nghia thong ke**: Welch t=−1,11 p=0,266; Mann-Whitney p=0,152.
  De phat hien delta 8,7bps voi sd 110bps can **~2.500 quan sat/nhom** — dang co 384 vs 745.
  Nghia la **KHONG ket luan duoc "regime da doi"**; doc dung la: uoc luong mean tu hop nhat
  thap hon nhieu so voi 9,13bps, va khoang tin cay rong hon nhieu.
- "4/4 nam duong, Sharpe 1,59, MaxDD −7,8%" (finding job `Taylor_20260925_103217`) **dung cho
  cua so 2023-09-11 tro di**, va cua so do bat dau dung sau mot drawdown 206 phien −30%.
  Day la **bien gioi du lieu chon ho cua so**, khong phai ai chon.
- Gia tri lon nhat cua VIEC 0 khong phai "chien luoc tot/xau" ma la: **do lon cua MaxDD thuc te
  (−30%, khong phai −8%)** va **DSR that (0,49, khong phai 0,92)**.

## 5. Gioi han con lai

- **Van thieu 2018 + COVID 2020**: vendor khong co bar 1m truoc 2022-02-17. Phu 4,6/9,1 nam
  doi hop dong (truoc: 3,04/9,1).
- **Chi luu per-day record, khong luu bar 1m tho.** Kenh duy nhat la MCP sandbox (khong co SDK
  FiinQuant cai local — da kiem `pip list` + `import FiinQuantZ`), ma sandbox chan `os`/file I/O
  nen du lieu chi ve duoc qua stdout. 389 phien x 257 bar khong kha thi qua kenh do. Hau qua:
  **khong re-test duoc cac bien the doi exit time hay stop o do phan giai trong ngay** tren doan
  moi (cot `minlow29/maxhigh29` chi du cho stop kieu "cham la thoat", dung voi `orb_core.sim`).
- Khong dung den hang doi harvest `state/fiinprox_harvest/queue.json`: FiinX **MCP** la kenh
  KHAC voi browser-harvest (oshares/fx). Hang doi giu nguyen 34 oshares + 15 fx pending,
  khong chen, khong xoa, khong gian doan.

## File

- `fiinx_daily_gap.csv` — 389 per-day record MOI (2022-02-17..2023-09-08)
- `fiinx_daily_overlap.csv` — 80 per-day record doan trung, de doi soat vendor
- `fiinx_daily_2023Q4.csv` — ban do soat vong 1 (exit 14:30), giu de truy nguon
- `xcheck.py` / `xcheck2.py` — doi soat vendor (muc dai luong / muc ket qua chien luoc)
- `extend.py` — dung tape ghep + chay config deploy
- `analyse.py` — tach nam/nua nam, drawdown, PSR/DSR
- `orb_trades_extended_20220217_20260925.csv` — 1.129 trade tai tao duoc
