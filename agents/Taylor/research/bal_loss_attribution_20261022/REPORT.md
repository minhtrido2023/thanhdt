# REPORT — Chẩn đoán lỗ sổ BAL (job Taylor_20261022_093122)

PREREG: `PREREG.md` (md5 `bbecd438c5406406f99fbbdef561b58d`, ghi trước khi chạy số). READ-ONLY: không sửa
production, không pin, không chạy engine. Script + output: `live_attrib.py` → `live_attrib.json`;
`recent_window.py` → `recent_window.json` (**ngoài PREREG**); `backtest_compare.py` → `backtest_compare.json`;
`q4_exposure_adj.py` → `q4_exposure_adj.json` (**ngoài PREREG**). Mọi số dưới đây lấy từ các file đó.

## TL;DR
1. **Sổ BAL live chỉ có ĐÚNG MỘT lệnh từ 01/07: VPI** (Văn Phú Invest, ICB 8633 bất động sản), ở cả 2 TK.
   Mua 17-18/09 giá bình quân 62.375 (SpaceX 800cp) / 62.450 (ZaloPay 400cp). Bán 16/10 do stop-loss −20%
   trên giá vốn (`auto_exit_inject.py`, mirror `pt_v23_audit_2014.py:2008`), bình quân 49.425 / 49.413.
   Lỗ ròng **−10.446.757đ (−1,069% NAV) SpaceX** và **−5.258.403đ (−0,554% NAV) ZaloPay**; return lệnh
   −20,9% / −21,0% sau phí. Fill journal khớp dnse_raw 0đ chênh (cả KL và giá trị).
2. "Lỗ nặng" ở mức **lệnh** (−21%), không phải ở mức NAV: BAL chỉ chiếm 5,1% / 2,6% NAV lúc vào.
3. Lỗ gần như toàn bộ là **riêng mã**: β VPI 0,51 ⇒ phần beta −2,9pp, phần dư −17,9pp (β=1: −15,0pp).
4. **Không phải momentum crash trong nhịp bật 21/10**: BAL không còn vị thế nào từ 16/10. Cái giá thật là
   bán ở đáy: 16/10 là Close thấp nhất của VPI trong cả cửa sổ; 21/10 VPI đóng 54.100, +9,5% so với giá bán.
5. So với backtest R3 pin0%: lệnh VPI ở **phân vị 11,3%** phân phối lệnh BAL (trong dải). Theo thước đo
   "P&L sổ BAL 21 phiên / NAV toàn hệ", **SpaceX −1,07% rơi vào phân vị 4,4% ⇒ chạm ngưỡng cảnh báo <5% đã khai
   trong PREREG (vừa đủ)**; ZaloPay −0,55% ở phân vị 8,8% (trong dải). Lý do: dồn 5,1% NAV vào một mã duy
   nhất; sổ BAL trong backtest luôn đa dạng hoá nhiều mã.
6. Lịch sử (Q4): BAL−VNINDEX thô âm trong nhịp bật (tiêu chí PREREG KHÔNG đạt ở ngưỡng chính, đạt ở ngưỡng
   độ nhạy), nhưng **hiệu chỉnh phơi nhiễm thì xoá hết** — sổ BAL thường phần lớn là tiền, nên tụt sau
   VNINDEX ngày tăng mạnh là chuyện cơ học. Không có bằng chứng BAL kém trong nhịp bật.

## Q1 — Cửa sổ lỗ (số đo)
**MaxDD toàn lịch sử theo PREREG** (cột `nav` của nav_history; chưa có dòng 21/10 ở cả 2 TK, nên dòng cuối là 20/10):

| TK | Đỉnh | Đáy | MaxDD | BAL có vị thế? |
|---|---|---|---|---|
| SpaceX | 02/07 990,30tr | 27/07 897,13tr | **−9,41%** | Không (lệnh BAL đầu tiên 17/09) |
| ZaloPay (NAV a, gồm DGC legacy) | 08/07 996,80tr | 27/07 833,86tr | **−16,35%** | Không |
| ZaloPay phần bot (`nav_sleeve_history` nav_b) | 08/07 | 27/07 | **−10,81%** | Không |

⇒ Đợt sụt sâu nhất của 2 TK là tháng 7, khi **BAL = 0**. Ở cửa sổ đó các sổ gây lỗ là PARK (ngân hàng
custom30V) và CAPIT; SpaceX: PARK −73,97tr, CAPIT −24,65tr (`window_pnl_by_ticker_SpaceX.csv`). Phân rã
ZaloPay tháng 7 không đáng tin: residual −512tr, vì DGC/VPB legacy không có trong verified_snapshot.

**Đợt vừa rồi (NGOÀI PREREG, gắn nhãn)**: cửa sổ cố định 16/09 (trước lệnh BAL) → 20/10, P&L theo sổ:

| Sổ | SpaceX | ZaloPay |
|---|---|---|
| ΔNAV | −5,49tr (−0,56%) | −18,39tr (−1,94%) |
| **BAL** | **−10,45tr (−1,07%)** | **−5,26tr (−0,55%)** |
| PARK | −6,72tr (−0,69%) | −3,51tr (−0,37%) |
| LAG | +3,41tr | +32,24tr |
| CAPIT | +11,64tr | +0,58tr |
| DISCRETIONARY | +1,59tr | +0,51tr |
| residual (tiền/lãi trứng/ngoài bot) | −4,96tr | −42,95tr ≈ DGC legacy (chênh MTM nav−snapshot 386,3tr→344,4tr = −41,9tr) |

BAL là sổ lỗ lớn nhất ở cả 2 TK trong cửa sổ này, nhưng ở cấp NAV chỉ khoảng 1% / 0,5%. Đỉnh→đáy từ 01/09:
SpaceX 08/10→15/10 −1,84%; ZaloPay 04/09→15/10 −7,24%, phần lớn nằm ở residual −91,4tr (DGC). Lưu ý: dòng SCL
(LAG) −43,2tr ở cửa sổ SpaceX 08/10→15/10 là **artifact snapshot**, không phải lỗ thật — SCL biến khỏi
verified_snapshot 15/10 mà không có FILL bán, và residual +44,1tr bù đúng khoản đó (liên quan việc xử lý
quyền mua đang sửa ở nhánh lag-rights).

## Q2 — Phân rã lỗ BAL (N = 1 lệnh × 2 TK; mô tả, không suy rộng)
- (a) Beta: β VPI/VNINDEX = **0,512** (OLS log-return 250 phiên trước 17/09, corr 0,38). Cùng kỳ VNINDEX
  1.810,11 → 1.705,91 = **−5,76%**. Phần beta = −2,95pp.
- (b) Phần dư (riêng mã/momentum) = **−17,85pp** trên tổng −20,80% gross (β=1: −15,04pp). Khoảng 85% lỗ
  nằm ở phần riêng mã.
- (c) Top mã / ngành: chỉ có 1 mã. Tập trung 100% vào BĐS (ICB 8633). Đây là rủi ro tập trung, không phải
  lỗ lan rộng.
- (d) Thời điểm vào: giá mua bình quân 62.400 = **−0,32% so với max Close 20 phiên và cả 250 phiên**, tức
  mua sát đỉnh 1 năm, sau khi mã đã tăng +15,9% trong 60 phiên trước. Đây đúng là bản chất tín hiệu
  RE_BACKLOG_BUY momentum. Ghi chú: tín hiệu VPI đã có từ 20/08 nhưng bị hoãn (thiếu tiền + signal_hold
  paper-track tới 16/09) nên vào trễ khoảng 1 tháng. Chưa đo được tác động của độ trễ này. Có cutloss:
  stop −20% chạy đúng luật, bán 16/10.
- (e) Momentum crash trong nhịp bật: **số liệu KHÔNG ủng hộ**. BAL có 0 vị thế ngày 21/10 (verified_snapshot
  21/10, cả 2 TK). VNINDEX 21/10 +2,76% (BQ, sau sync), VPI +5,46%. Thiệt hại liên quan nhịp bật là
  **chi phí cơ hội của stop**: bán ở Close thấp nhất cửa sổ (48.100 ngày 16/10). Nếu giữ tới Close 21/10 thì
  lỗ khoảng −13,3% thay vì −20,8% (ước lượng từ Close, chưa tính phí). Một ca không đủ để đánh giá luật stop.

## Q3 — So với backtest R3 pin0% (ledger md5 `4707bcbe…`, 2014-01-02→2026-06-19)
| Thước đo (cùng loại) | Backtest | Live | Phân vị live |
|---|---|---|---|
| Return per-lệnh BAL cổ phiếu (N=266 holding đã đóng) | trung vị +4,0%; p10 −21,4%; p05 −25,3%; 12,4% lệnh ≤ −20%; 32 lệnh STOP trung vị −22,2% | VPI −20,9% | **11,3%** — trong dải |
| P&L sổ BAL 21 phiên / NAV toàn hệ (N=113 cửa sổ không chồng lấn, bỏ 34 cửa sổ có REBAL) | trung vị +0,22%; p05 −0,70%; p01 −3,50%; min −4,28% | SpaceX −1,07% / ZaloPay −0,55% | **4,4%** ⚠️ / 8,8% |
| MaxDD NAV toàn hệ | pin −14,6%, bootstrap 5th −25,2% (pin0%) | SpaceX −9,41%; ZaloPay a −16,35%; ZaloPay bot −10,81% | SpaceX và ZaloPay-bot nằm trong pin; ZaloPay-a sâu hơn pin nhưng trong dải bootstrap (do DGC ngoài bot). Cả 3 đều ở tháng 7, không phải đợt BAL |
| MaxDD riêng sổ BAL (nav_bal_ref) | −20,9% | không định nghĩa được (sổ live 1 lệnh, không có vốn sổ riêng) | — |

**Phán theo PREREG §4**: ⚠️ **chạm ngưỡng cảnh báo ở SpaceX (4,4% < 5%), vừa đủ**. Đây là tín hiệu cảnh báo,
nói thẳng. Đọc đúng: một lệnh −21% là chuyện thường của BAL (12,4% lệnh backtest ≤ −20%, ~1/8). Cái hiếm là **một lệnh duy nhất
chiếm 5,1% NAV**, nên lỗ của nó thành lỗ của cả sổ. Kiểm tính nhất quán ledger: `combined_nav − nav_bal −
nav_lag` lệch tới 9,6% NAV ở một số ngày (có cấu phần ngoài 2 sổ, nhiều khả năng là pool CAPIT). Mẫu số
combined_nav vì thế lớn hơn BAL+LAG, làm phân vị live trông tệ hơn chút (thận trọng, chưa đo tách).

## Q4 — Lịch sử: BAL trong nhịp VNINDEX bật mạnh sau giảm sâu
Định nghĩa PREREG: VNINDEX ret(t) ≥ +2,0% và Close(t−1) ≤ 92% max 60 phiên; episode cách nhau ≥20 phiên.
**N = 27 episode, 25 dùng được** (2 ca nhiễm REBAL). Độ nhạy (−10%, +2,5%): N = 17. Danh sách từng episode:
`q4_episodes_*.csv`.

| | Chính (−8%, +2%) | Độ nhạy (−10%, +2,5%) |
|---|---|---|
| Trung vị excess 5 phiên BAL−VNI (thô) | −1,34% (không điều kiện +0,02%) | −1,89% |
| Số episode dưới trung vị không điều kiện | 15/25 (binom một phía 0,21) | 13/17 (0,025) |
| Phân vị resample (10.000 lần, seed 20261022) | 0,05% | 0,0% |
| **Tiêu chí PREREG "BAL tụt hậu"** | **KHÔNG đạt** (15 < 17 = ⌈2N/3⌉) | đạt |

**Nhưng đây là ảo ảnh phơi nhiễm (chẩn đoán NGOÀI PREREG)**: ngày trước episode, sổ BAL chỉ có trung vị
29-40% cổ phiếu, hoặc 45-59% nếu cộng ETF park. Trong ngày VNINDEX +2% thì bất kỳ sổ nào phơi nhiễm < 1
cũng "tụt hậu". Hiệu chỉnh `r_BAL − w(t−1)·r_VNI` (giả định ETF park β≈1):

| | Chính (N=26) | Độ nhạy (N=17) |
|---|---|---|
| Trung vị excess-hiệu chỉnh 1 phiên / 5 phiên | +0,01% / +0,05% | 0,00% / 0,00% |
| Số dưới trung vị không điều kiện (5 phiên) | 8/26 | 7/17 |
| Phân vị resample (5 phiên) | 63% | 53% |

⇒ **Không có bằng chứng BAL lỗ hơn bình thường trong nhịp bật sau giảm sâu** khi đã tính phơi nhiễm. Sổ chỉ
tham gia ít hơn vì đang cầm tiền. Đây là mô tả với N nhỏ, không phải kiểm định edge, nên không gán p-value.

## Q5 — Kết luận
**Nguyên nhân chính**: một lệnh momentum đơn lẻ (VPI, BĐS) mua sát đỉnh 1 năm, rồi dính cú sụt riêng mã
khoảng −15 đến −18pp, trong khi VNINDEX chỉ −5,8%. Lệnh bị stop −20% đúng luật, bán đúng đáy, 3 phiên trước
nhịp bật. Lỗ ở cấp lệnh thì thường gặp (phân vị 11%). Lỗ ở cấp sổ thì hiếm (phân vị 4,4% ở SpaceX), **vì sổ BAL
live = 1 mã**. Không phải momentum crash, không phải beta thị trường, và không liên quan nhịp bật 21/10
(BAL không còn vị thế).

**Nhánh xử lý KHÔNG bị bằng chứng bác** (đề xuất nghiên cứu, KHÔNG đổi production):
- **Rủi ro tập trung khi sổ BAL live có ít mã** (1 mã = 5,1% NAV). Đây là chỗ live lệch backtest rõ nhất.
  Hướng đáng đo: trần % NAV mỗi lệnh BAL khi n_bal nhỏ, hoặc so sizing live với sizing backtest lúc sổ chỉ
  1-2 mã. Chưa đo.
- **Đọc kỹ thuật trong due diligence**: chưa có bằng chứng ủng hộ hay bác ở đây (N=1). Lưu ý: job
  entry_risk_tech_20261022 đã cho Q1 timing NO-GO; ở ca này tín hiệu "mua sát đỉnh 250 phiên" là bản chất
  của RE_BACKLOG_BUY, không phải lỗi.
- **Chỉnh tỉ lệ BAL**: không được bằng chứng ở đây hỗ trợ. Lỗ BAL ở cấp NAV chỉ khoảng 1%, và đợt sụt sâu nhất
  của TK (tháng 7) xảy ra khi BAL = 0.
- Luật stop −20%: ca này cho thấy chi phí cơ hội (bán ở đáy). Với N=1 thì không kết luận gì; muốn xét phải
  dựng thí nghiệm riêng trên 32 lệnh STOP của backtest.

**Bị bằng chứng bác**: "BAL momentum crash trong nhịp bật" (BAL 0 vị thế ngày 21/10; lịch sử đã hiệu chỉnh
phơi nhiễm không cho thấy tụt hậu) · "lỗ do beta thị trường" (beta chỉ khoảng 14% lỗ).

## Không đo được / giới hạn
- nav_history chưa có dòng 21/10 ở cả 2 TK, nên không có NAV sau nhịp bật.
- Phân rã theo sổ cửa sổ tháng 7 ZaloPay không tin được (legacy DGC/VPB nằm ngoài snapshot, residual −512tr).
- Ánh xạ mã → sổ cho fill tháng 7 không có tag, phải lấy từ plan; tháng 7 BAL = 0 nên không ảnh hưởng BAL.
- Q4 dùng `nav_bal_ref` = sổ BAL backtest (gồm ETF park + CAPIT-B), không tách riêng phần momentum.
  Hiệu chỉnh 5 phiên cộng excess ngày (xấp xỉ).
