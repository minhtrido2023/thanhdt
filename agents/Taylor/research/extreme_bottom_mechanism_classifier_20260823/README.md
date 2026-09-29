# extreme_bottom_mechanism_classifier_20260823 — "cú sốc THANH KHOẢN/CHÍNH SÁCH" vs "cú sốc CƠ BẢN THẬT"

Job `Taylor_20260823_110750`. Nghiên cứu **CƠ CHẾ**, Phase-0 tier. **KHÔNG** chạm production,
**KHÔNG** backtest tối ưu tham số, **KHÔNG** đề xuất wire. Không tính vào `N_trials` của
`plan_margin_valuation_spread_20260823.md`.

**Prereg `PREREG.md` commit `538b4df4` — TRƯỚC mọi truy vấn ROE/NP và trước mọi nhãn.**

---

## VERDICT NGẮN — giả thuyết **KHÔNG ĐƯỢC ỦNG HỘ**. NO-GO.

Tiêu chí bác bỏ đã khoá ở PREREG §5 (tách hoàn toàn theo thứ hạng, **không** ngưỡng) **THẤT BẠI
trên cả hai thước đo**, và đúng **2/7 episode đi ngược giả thuyết** — chạm đúng điều kiện NO-GO
mà dispatch của Mike đặt ra.

| Thước đo | Nhóm LIQUIDITY_POLICY | Nhóm FUNDAMENTAL_REAL | Tách hoàn toàn? |
|---|---|---|---|
| median **cổ phiếu** fwd-12m từ đáy | 2009-11 **−46,8%** · 2018-05 **+0,8%** · 2020-03 +96,7% | 2011-05 **+21,2%** | **KHÔNG** (min LIQ −46,8% < max FUND +21,2%) |
| VNINDEX fwd-12m từ arm | 2009-11 **−8,9%** · 2018-05 **+4,3%** · 2020-03 +44,2% | 2011-05 **+7,2%** | **KHÔNG** |

Hai episode đi ngược (giống hệt nhau ở cả hai thước đo): **2009-11** và **2018-05** — được gán
`LIQUIDITY_POLICY` **sạch, cả hai nguồn bằng chứng đồng thuận**, nhưng cho kết quả 12 tháng tệ
hơn episode `FUNDAMENTAL_REAL` duy nhất.

**Hai phản chứng đắt nhất — giá và lợi nhuận chạy NGƯỢC chiều nhau ở đúng hai ca cực đoan:**

| | 12 tháng sau | median TTM lợi nhuận rổ | median ROE rổ | **median cổ phiếu** |
|---|---|---:|---:|---:|
| Đáy **2010-08-25** | →2011-08 | **−7,5%** (gần như giữ) | −21,3% | **−46,8%** |
| Đáy **2022-11-15** | →2023-11 | **−31,6%** (sụt mạnh nhất trong 7) | −42,6% | **+42,4%** |

⇒ Trong 12 tháng sau đáy 2022, giá **phục hồi XUYÊN QUA** một đợt suy giảm lợi nhuận thật; trong
12 tháng sau đáy 2010, giá **sụt gần một nửa** trong khi lợi nhuận gần như giữ nguyên. Cơ chế
"lợi nhuận giữ ⇒ giá bật lại" **không mô tả đúng** hai ca này. Spearman rho giữa lợi nhuận
forward và lợi suất forward = **+0,29** (N=7, MÔ TẢ, **không tính p-value** theo PREREG §6.1).

---

## Bảng phân loại đầy đủ (`classification.csv`)

Nhãn gán bằng **luật khoá trước** (PREREG §3 ngưỡng, §4 luật hợp nhất), code `label_and_test.py`
— không có ngưỡng nào được sửa sau khi thấy kết quả.

| Episode | Arm | Đáy | **A** (nguyên nhân vĩ mô) | **B** (số lợi nhuận, neo tại ARM) | M2 k=4 | ΔROE | **NHÃN** | med12 cổ phiếu |
|---|---|---|---|---|---:|---:|---|---:|
| 2007-04 | 2007-04-23 | 2009-02-24 | **MIXED** | không kết luận (n=28<30) | 1,301 | +88% | **AMBIGUOUS** *(chỉ-định-tính)* | +130,0% |
| 2009-11 | 2009-11-26 | 2010-08-25 | LIQUIDITY_POLICY | LIQUIDITY_POLICY | 1,180 | +3,6% | **LIQUIDITY_POLICY** | **−46,8%** |
| 2011-05 | 2011-05-23 | 2012-01-06 | FUNDAMENTAL_REAL | FUNDAMENTAL_REAL | 0,668 | −50,5% | **FUNDAMENTAL_REAL** | +21,2% |
| 2012-08 | 2012-08-27 | 2012-11-02 | LIQUIDITY_POLICY | FUNDAMENTAL_REAL | 0,715 | −45,0% | **AMBIGUOUS** *(A≠B)* | +26,3% |
| 2018-05 | 2018-05-28 | 2019-01-03 | LIQUIDITY_POLICY | LIQUIDITY_POLICY | 0,987 | −16,9% | **LIQUIDITY_POLICY** | **+0,8%** |
| 2020-03 | 2020-03-11 | 2020-03-24 | LIQUIDITY_POLICY | LIQUIDITY_POLICY | 0,996 | −12,9% | **LIQUIDITY_POLICY** | +96,7% |
| 2022-05 | 2022-05-13 | 2022-11-15 | LIQUIDITY_POLICY | FUNDAMENTAL_REAL | 0,839 | −38,8% | **AMBIGUOUS** *(A≠B)* | +42,4% |

`M2 k=4` = median theo từng mã của `TTM_NP(q0+4)/TTM_NP(q0)`; `ΔROE` = biến động tương đối median
`ROE_Trailing` q0→q0+4. Neo tại **ĐÁY** thay vì ARM (post-hoc, §"Độ bền" dưới) **không đổi nhãn
của bất kỳ episode nào ngoài 2007-04** và không cứu được phép kiểm tách nhóm.

### Bằng chứng A — nguyên nhân vĩ mô (tra tin tức thật, không suy từ đồ thị giá)

- **2007-04 → GFC**: hai lớp chồng nhau. Trong nước 2008: CPI ~28%, SBV nâng lãi suất chính sách
  từ 7,5% (04/2008) lên 13% (05/2008) + nâng dự trữ bắt buộc + phát hành tín phiếu bắt buộc
  (**chính sách**). Đồng thời BĐS đóng băng −40%, doanh nghiệp không bán được sản phẩm, gánh lãi
  vay cao (**thực**) + cú sốc cầu xuất khẩu từ GFC. ⇒ **MIXED**, không ép về một phía.
- **2009-11**: IMF Article IV 2010 — 11/2009 SBV nâng lãi suất chính sách **+100bp**, **phá giá
  VND 5,5%**, **chấm dứt gói cấp bù lãi suất 4pp**. Cú sốc chính sách tiền tệ thuần tuý.
- **2011-05**: Nghị quyết 11/NQ-CP (24/02/2011) — siết tăng trưởng tín dụng <20%, cắt tín dụng
  cho BĐS/chứng khoán; lãi vay 20–25%; bong bóng BĐS vỡ → nợ xấu hệ thống ngân hàng bùng 2012.
  Tới 05/2011 cú sốc **đã vào** doanh thu/biên lợi nhuận/nợ xấu.
- **2012-08**: bắt Nguyễn Đức Kiên 21/08/2012 → rút tiền hàng loạt tại ACB; SBV bơm **17.000 tỷ
  VND** vào liên ngân hàng; HNX −5,24% ngày công bố, thị trường −9,2% trong tuần. **Kích hoạt là
  bank-run**, nhưng bối cảnh nền là khủng hoảng nợ xấu/BĐS đang diễn ra.
- **2018-05**: khối ngoại rút khỏi EM + margin call sau nhịp tăng 48% (2017) và +22% tới đỉnh
  09/04/2018; chiến tranh thương mại Mỹ-Trung; Fed nâng lãi suất. Cú sốc **dòng vốn/định giá**.
- **2020-03**: COVID-19 — cú sốc ngoài hệ thống tài chính đúng theo định nghĩa §1.
- **2022-05**: bắt Trịnh Văn Quyết (03/2022) + huỷ lô trái phiếu Tân Hoàng Minh (04/2022) + bắt
  Trương Mỹ Lan/Vạn Thịnh Phát (10/2022) → **rút tiền hàng loạt tại SCB** (SBV bơm tiền cứu);
  SBV nâng lãi suất **+200bp** T9/T10 chống áp lực tỷ giá (Fed +425bp); **thị trường trái phiếu
  doanh nghiệp đóng băng**; margin call dây chuyền. ⇒ đúng câu chuyện của user, **và nguồn xác
  nhận nó**.

**Nhưng bằng chứng B bác lại chính ca 2022 này**: median TTM lợi nhuận rổ 2022Q1→2023Q1 **−16,1%**,
median ROE **−38,8%** (neo tại đáy 11/2022 còn nặng hơn: **−31,6%** / **−42,6%**), tỷ lệ mã có lãi
92%→79%. Suy giảm thu nhập ở VN 2023 là **thật** (đơn hàng xuất khẩu sụt, BĐS đóng băng), không
chỉ là giá bị ép bán. Cú sốc thanh khoản **và** suy thoái thu nhập thật xảy ra **chồng lên nhau**
— đây chính là lý do §1 phải có nhãn `AMBIGUOUS` và cấm ép nhãn.

---

## Trả lời trực tiếp 2 câu hỏi Mike đặt tên

**(5) Đáy 2010-08-25 (median mã −46,8%/năm) thuộc nhóm nào?**
→ **`LIQUIDITY_POLICY`**, nhãn **sạch**, cả hai nguồn bằng chứng đồng thuận: nguyên nhân là cú
sốc chính sách tiền tệ 11/2009 (nâng lãi suất, phá giá, cắt cấp bù lãi suất), và lợi nhuận rổ
**giữ nguyên** trong 12 tháng sau arm (M2 = 1,180). **NGƯỢC hoàn toàn với kỳ vọng trong dispatch.**
Đây không phải bằng chứng ủng hộ giả thuyết — nó là **phản chứng mạnh nhất chống lại** nó: một
cú sốc thanh khoản/chính sách, lợi nhuận doanh nghiệp không hề sập, mà giá vẫn mất thêm gần một
nửa trong 12 tháng tiếp theo.
*Cơ chế thật khả dĩ hơn:* 08/2010 **chưa phải cuối cú sốc**. Đợt siết tín dụng Nghị quyết 11 và
đóng băng BĐS còn ở phía trước — đo tại 01/2011 (`earnings_gfc_probe.csv`) lợi nhuận rổ đã bắt
đầu quay đầu (M2 k=4 = 0,877), và tới episode 2011-05 thì sập hẳn (0,668). "Lợi nhuận đang giữ"
tại thời điểm mua **không** đồng nghĩa "cú sốc đã qua".

**(6) GFC 2008 có phải `FUNDAMENTAL_REAL` rõ nhất không?**
→ **KHÔNG.** Nó ra **`AMBIGUOUS`**, và thiệt hại thu nhập của rổ niêm yết VN trong GFC lại là
**NHẸ NHẤT** trong ba ứng viên "cơ bản thật". Probe riêng neo giữa đợt sập (`2008-06-02`, tức
2008Q1→2009Q1, `earnings_gfc_probe.csv`): median TTM lợi nhuận **−10,9%**, median ROE
19,7%→13,9% (**−29,6%**, chưa chạm ngưỡng 1/3), tỷ lệ mã có lãi 100%→88,6%. So với 2011-12
(−33%/−50%) và 2022-23 (−32%/−43%) thì GFC nhẹ hơn hẳn — **trong khi drawdown giá lại sâu nhất
lịch sử (−79,9%) và PE median rơi 20,57 → 4,78**. Cùng chiều với tranche T3 lỗ −60,7% mà job
trước tìm ra, nhưng **cơ chế không phải "thu nhập sập"** mà là **de-rating định giá từ nền bong
bóng**. Chiều sâu drawdown ở VN **anti-tương quan** với mức thiệt hại thu nhập trong mẫu này.

---

## Độ bền & những gì có thể bẻ kết luận này

1. **Neo tại ĐÁY thay vì ARM** (post-hoc, khai báo rõ — `earnings_basket_trough.csv`): nhãn đổi ở
   đúng 1 episode (2007-04: từ "không kết luận n<30" thành LIQUIDITY_POLICY, do rổ đủ mã tại
   2009-02). Cả hai episode đi ngược vẫn đi ngược. **Kết luận không đổi.**
2. **Ngưỡng M2**: 2 episode nằm sát biên (2022-05 arm 0,839; 2009-11 trough 0,925). Nhưng cả hai
   episode gây NO-GO (2009-11, 2018-05) đều **không** ở biên (1,180 và 0,987) ⇒ nới/siết ngưỡng
   không cứu được phép kiểm tách nhóm.
3. **Thiên lệch sống sót đẩy kết luận theo hướng NGƯỢC lại**: `tav2_bq.ticker` xoá sạch mã huỷ
   niêm yết (0 dòng FLC) ⇒ số lợi nhuận rổ là **CẬN TRÊN**, và thiên lệch mạnh nhất ở đúng nhóm
   FUNDAMENTAL_REAL. Nghĩa là thực tế giả thuyết còn **yếu hơn** những gì bảng này cho thấy, không
   phải mạnh hơn.
4. **N = 7, và người phân loại đã biết đáp án trước** (PREREG §0/§0b — không giấu được). Đây là
   **bằng chứng cơ chế**, không phải kiểm định. **Không có p-value ở bất kỳ đâu trong file này.**

## Vì sao KHÔNG thể dùng phân loại này làm điều kiện live (kể cả nếu nó đã đúng)

Bằng chứng B nhìn **về phía trước** so với ngày ARM: q0+2, q0+4 chưa tồn tại tại thời điểm ARM và
còn trễ thêm 60–85 ngày công bố (`MAX_FIN_LAG=90`). Một cổng live chỉ được dùng **nguyên nhân vĩ
mô quan sát được ngay** + lợi nhuận **TRAILING** — mà chính nhánh A đơn độc đã sai ở 2/7 ca
(2009-11, 2018-05 đều là "thanh khoản/chính sách" đúng nghĩa và đều thất bại). ⇒ Không có đường
nào biến bảng này thành luật giao dịch.

## Hàm ý cho Phase 1 (`plan_margin_valuation_spread_20260823.md`)

**Không đề xuất thêm biến thể nào.** Cụ thể: **KHÔNG** sửa V8 thành "tăng tranche khi ĐÀO SÂU +
XÁC NHẬN thu nhập rổ còn giữ" như dispatch nêu như một khả năng — chính điều kiện "thu nhập rổ
còn giữ" là thứ đúng ở đáy 2010-08-25 (M2 = 1,180, cao **thứ hai** trong 7 episode) ngay trước
khi median mã mất **−46,8%**. Thêm điều kiện đó vào sẽ **tăng** tỷ trọng đúng vào ca tệ nhất.
`N_trials` giữ nguyên; V8 (tranche `dd52<=-35%`) giữ nguyên như job `_083709` đã chốt, chờ user
duyệt riêng.

## File

| File | Nội dung |
|---|---|
| `PREREG.md` | Prereg — commit `538b4df4` trước mọi truy vấn |
| `q_earnings.sql` → `earnings_basket.csv` | Bằng chứng B **pre-declared**, neo tại ARM |
| `q_earnings_trough.sql` → `earnings_basket_trough.csv` | Cùng phép đo, neo tại ĐÁY (**post-hoc**, độ bền) |
| `q_earnings_gfc.sql` → `earnings_gfc_probe.csv` | Probe **post-hoc**: 2008-06-02 (giữa GFC) + 2011-01-04 (đầu đợt siết) — cần vì arm 2007-04 cách đáy 673 ngày nên cửa sổ pre-declared không thể nhìn thấy GFC |
| `label_and_test.py` → `classification.csv` | Áp luật §3/§4 + phép kiểm tách nhóm §5 |

**Nguồn tin vĩ mô** (bằng chứng A): [APRACA — tác động GFC lên kinh tế VN](https://www.apraca.org/the-impact-of-the-global/) ·
[CFR — Vietnam's Economic Hiccups](https://www.cfr.org/backgrounders/vietnams-economic-hiccups) ·
[IMF Article IV 2010 (CR 10/281)](https://www.imf.org/external/pubs/ft/scr/2010/cr10281.pdf) ·
[Nghị quyết 11/NQ-CP 24/02/2011](https://english.luatvietnam.vn/resolution-no-11-nq-cp-dated-february-24-2011-of-the-government-on-major-solutions-for-controlling-inflation-stabilizing-the-macro-economy-and-ensu-59598-doc1.html) ·
[VietnamNet — bước ngoặt Nghị quyết 11](https://vietnamnet.vn/en/the-turning-point-of-resolution-11-and-the-results-of-steadfastness-2504087.html) ·
[France 24 — ACB sau vụ bắt bầu Kiên](https://www.france24.com/en/20120823-vietnam-bank-turmoil-sotck-arrest-founder-deposits-fraud-acb) ·
[BBC — Nguyen Duc Kien arrest](https://feeds.bbci.co.uk/news/world-asia-19358745) ·
[Business Standard — VN-Index 04/2018](https://www.business-standard.com/amp/article/international/vietnam-asia-s-top-stock-market-of-2018-set-to-be-world-s-worst-in-april-118042700415_1.html) ·
[The Investor — SBV bơm tiền cứu SCB](https://theinvestor.vn/vietnam-central-bank-pumps-cash-to-save-troubled-lender-scb-d9677.html) ·
[VinaCapital — lãi suất & TTCK VN 2022-23](https://vinacapital.com/wp-content/uploads/2023/08/VinaCapital-Insights-Vietnams-Interest-Rate-Cuts-are-Boosting-Stock-Prices.pdf) ·
[VBMA — Bond Market Report 2022](https://vbma.org.vn/storage/reports/April2024/ENGLISH%20VBMA_ANNUAL%20REPORT%202022%20-%20revised%20-%20Copy%202.pdf) ·
[VietnamPlus — TTCK VN nửa đầu 11/2022](https://en.vietnamplus.vn/vietnamese-stock-market-loses-202-billion-usd-in-first-half-of-november/244037.vnp)
