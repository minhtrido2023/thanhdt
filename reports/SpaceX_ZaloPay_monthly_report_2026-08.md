# BÁO CÁO THÁNG — TÀI KHOẢN SPACEX & ZALOPAY
## Kỳ báo cáo: THÁNG 08/2026 (01/08 – 31/08/2026)
### *Tháng thứ hai vận hành — Signal HOLD toàn bộ từ 21/08 do VPI, capit_margin_lever LIVE từ 24/08*

**Tài khoản 1:** SpaceX · DNSE, số hiệu 0002023347 · V2.4 live (có margin) · vốn cơ sở theo R3 pin
**Tài khoản 2:** ZaloPay · DNSE, số hiệu 0001743768 · V2.4 live (cash-only) · DGC excluded
**Chiến lược:** V2.4 — BAL momentum + LAG hậu-công-bố-lợi-nhuận, parking custom30V NEUTRAL, rổ CAPIT khi bear-washout
**Ngày lập báo cáo:** 01/09/2026 · **Người lập:** Taylor (Quant, §2-3-6-8-11) · Mike (§1-7-9-10) · Bobby (§5) · Spyros (§4)
**Đối tượng:** Báo cáo hiệu suất & vận hành tháng — chuẩn mực quản lý tài sản

---

> **Ghi chú phiên bản:** Template này tạo ngày 25/08/2026 với §5 (Vĩ mô) đã điền đầy đủ bởi Bobby.
> Các mục hiệu suất (§1-4, §6-11) điền ngay sau khi đóng tháng (01/09/2026).

---

## MỤC LỤC — PHÂN CÔNG THEO PHẦN

| # | Mục | Người phụ trách | Nguồn dữ liệu |
|---|---|---|---|
| 1 | Tóm tắt điều hành | **Mike** | Tổng hợp toàn bộ |
| 2 | Hiệu suất MTD/QTD/YTD vs chỉ số | **Taylor** | nav_history + BQ + DNSE API |
| 3 | Phân rã nguồn lãi/lỗ (attribution) | **Taylor** | verify_account_snapshot.py + dividend_adjusted_return.py |
| 4 | Chỉ số rủi ro | **Spyros** (risk-auditor) | nav_history + positions |
| **5** | **Diễn biến vĩ mô tháng 8 & đánh giá rủi ro khủng hoảng** | **Bobby** (macro-strategist) | GSO/TCTK + SBV + Fed + nguồn công khai |
| 6 | Phí & chi phí | **Taylor** | execution logs + DNSE API |
| 7 | Nhật ký sự kiện tháng | **Mike** | bus events + KB |
| 8 | Danh mục cuối tháng | **Taylor** | positions DNSE 31/08 |
| 9 | Công bố sự cố & khoảng trống số liệu | **Mike** | bus incidents + kb/incidents/ |
| 10 | Triển vọng & việc cần làm | **Mike + DollarBill** | current_ops + plan pipeline |
| 11 | Phụ lục phương pháp | **Taylor** | pipeline spec + coding_guidelines |

---

## 1. TÓM TẮT ĐIỀU HÀNH
> **Người phụ trách: Mike** · Hoàn thành sau 01/09/2026

| Chỉ tiêu | SpaceX | ZaloPay |
|---|---:|---:|
| NAV đầu kỳ (01/08) | *[TBD từ nav_history 31/07]* | *[TBD]* |
| NAV cuối tháng (31/08) | *[TBD]* | *[TBD]* |
| Lãi/lỗ trong kỳ (VND) | *[TBD]* | *[TBD]* |
| Tỷ suất MTD | *[TBD]* | *[TBD]* |
| VN-Index cùng khung | *[TBD]* | *[TBD]* |
| Chênh so với chỉ số | *[TBD]* | *[TBD]* |
| Biến động năm hoá | *[TBD]* | *[TBD]* |
| Sụt giảm tối đa | *[TBD]* | *[TBD]* |
| Số lệnh khớp | *[TBD]* | *[TBD]* |
| Tổng phí + thuế ước tính | *[TBD]* | *[TBD]* |

*[Điền sau 01/09 — lấy từ daily_nav_snapshot.py + reconcile_equity.py]*

---

## 2. HIỆU SUẤT MTD / QTD / YTD SO VỚI CHỈ SỐ
> **Người phụ trách: Taylor** · Nguồn: nav_history_{SpaceX,ZaloPay}.csv + DNSE API + BQ ticker

*[TBD — điền sau 01/09]*

Ghi nhớ khi điền:
- YTD 2026 = tổng kể từ ngày go-live (SpaceX 01/07, ZaloPay 06/07), không phải từ 01/01
- Cần bảng diễn biến theo tuần (4 tuần August)
- Dùng `dividend_adjusted_return.py` cho tỷ suất per-position

---

## 3. PHÂN RÃ NGUỒN LÃI/LỖ (ATTRIBUTION)
> **Người phụ trách: Taylor** · Bắt buộc dùng `bin/dividend_adjusted_return.py` (§21 coding_guidelines)

### 3.1 SpaceX — phân rã theo cấu phần kế toán
*[TBD]*

### 3.2 SpaceX — phân rã theo nhóm (đã cộng cổ tức ròng sau thuế 5%)
*[TBD]*

### 3.3 SpaceX — 5 vị thế tốt nhất & 5 tệ nhất
*[TBD]*

### 3.4 ZaloPay — phân rã theo nguồn
*[TBD — nhớ tách DGC excluded ra riêng]*

### 3.5 ZaloPay — lãi/lỗ chưa thực hiện phần bot (đã xác minh)
*[TBD]*

---

## 4. CHỈ SỐ RỦI RO
> **Người phụ trách: Spyros** (risk-auditor) · Nguồn: nav_history ngày, positions DNSE

| Chỉ số | SpaceX | ZaloPay | VN-Index |
|---|---:|---:|---:|
| Biến động ngày | *[TBD]* | *[TBD]* | *[TBD]* |
| Biến động năm hoá | *[TBD]* | *[TBD]* | *[TBD]* |
| Sụt giảm tối đa | *[TBD]* | *[TBD]* | *[TBD]* |
| Tỷ trọng cổ phiếu cuối tháng | *[TBD]* | *[TBD]* | — |

*[TBD — Spyros dispatch sau 31/08]*

---

## 5. DIỄN BIẾN VĨ MÔ THÁNG 8/2026 & ĐÁNH GIÁ RỦI RO KHỦNG HOẢNG
> **Người phụ trách: Bobby** (macro-strategist) · Đọc BLIND với forward-return và backtest outcome
> Dữ liệu: GSO/Tổng cục Thống kê, SBV, Fed, NBS Trung Quốc, EIA · Chốt ngày: 25/08/2026

> **Lưu ý dữ liệu:** CPI tháng 8/2026 chưa được Tổng cục Thống kê công bố (lịch mới: ngày 6/9/2026).
> Mọi số liệu CPI dưới đây là tháng 7/2026 hoặc lũy kế 7 tháng — ghi rõ tường minh.

---

### 5.1 Số liệu kinh tế trong nước

**Tăng trưởng GDP:** Kinh tế Việt Nam tiếp tục đà tăng tốc mạnh. GDP Q2/2026 đạt **+8,39% YoY**
(Q1: +7,94%), nâng lũy kế H1/2026 lên **+8,18%** — thuộc nhóm cao nhất khu vực ASEAN. Chính phủ
đặt mục tiêu tăng trưởng cả năm 2026 ở mức 8% hoặc có thể hướng tới 2 con số.

**Lạm phát — CPI tháng 7/2026 (số liệu TCTK mới nhất):**
- MoM: **−0,12%** (giảm nhẹ theo mùa vụ)
- YoY: **+4,45%** (giảm nhẹ so với tháng 6: +4,69%)
- Lũy kế 7 tháng 2026: **+4,39% YoY** · Lạm phát cơ bản: **+4,19%**

CPI đang tiệm cận nhưng *chưa vượt* trần mục tiêu Quốc hội (~4,5%). Bloomberg survey dự báo bình
quân năm 2026 ở mức 4,8% — hàm ý CPI có thể nhích lên trong các tháng cuối năm.

**Sản xuất công nghiệp (tháng 7/2026):** IIP tăng **+14,5% YoY**; lũy kế 7 tháng **+11,4% YoY** —
mức cao nhất trong nhiều năm. Manufacturing đóng góp 33,07% tổng giá trị gia tăng toàn nền kinh tế Q2.

**Bán lẻ (tháng 7/2026):** Tổng mức bán lẻ đạt 669,1 nghìn tỷ VND, tăng **+14,5% YoY**
(7 tháng: +13,1% theo giá hiện hành, +7,5% loại trừ yếu tố giá). Cầu nội địa duy trì mạnh.

**Xuất nhập khẩu (tháng 7/2026 và lũy kế 7 tháng):**

| Chỉ tiêu | Tháng 7/2026 | Lũy kế 7T/2026 | So sánh 7T/2025 |
|---|---|---|---|
| Xuất khẩu | 53,08 tỷ USD (+25,0% YoY) | 319,53 tỷ USD (+21,7%) | — |
| Nhập khẩu | 56,67 tỷ USD (+41,4% YoY) | 340,05 tỷ USD (+34,8%) | — |
| Cán cân | −3,59 tỷ USD | **−20,52 tỷ USD** | Đảo chiều từ **+10,35 tỷ USD** |

Nhập khẩu tăng vọt do máy móc thiết bị FDI và đầu tư hạ tầng — phản ánh chu kỳ mở rộng đầu tư,
chưa phải mất cân đối tiêu dùng. Cần theo dõi dự trữ ngoại hối nếu thâm hụt kéo dài.

---

### 5.2 Chính sách tiền tệ

**Lãi suất điều hành NHNN:** Lãi suất tái cấp vốn giữ nguyên **4,5%** (từ tháng 8/2023 đến nay).
Chính sách tiền tệ tiếp tục nới lỏng hỗ trợ tăng trưởng.

**Tăng trưởng tín dụng:** Mục tiêu toàn năm 2026: **~15%**. Đến 31/7/2026: +8,98% YTD (~20,3 triệu tỷ VND),
bám sát kế hoạch. NHNN triển khai gói tín dụng ưu đãi 200.000 tỷ đồng (~8,4 tỷ USD) cho SME.
Chính phủ giao NHNN siết tín dụng vào lĩnh vực rủi ro (BĐS) và đẩy nhanh xử lý nợ xấu.

**Tỷ giá VND/USD:** Ổn định trong tháng 8, dao động **26.013–26.345** (bình quân ~26.224). Tỷ giá
trung tâm SBV ngày 24/8: 25.600; thị trường ~26.280. DXY dưới 99 điểm là yếu tố thuận lợi.

**Chất lượng ngân hàng:** NPL toàn hệ thống **2,01%** cuối Q2 (từ 1,99% Q1) — vẫn kiểm soát được.
Lãi suất huy động có áp lực tăng nhẹ (dự báo +0,5–1 điểm % cả năm) nhưng chưa đến mức đáng lo.

---

### 5.3 Bối cảnh quốc tế

**Fed:** Họp FOMC 29/7/2026 giữ nguyên **3,50–3,75%** với 3 thành viên bất đồng (muốn tăng).
Không có forward guidance cho tháng 9. Fed Chair Kevin Warsh (nhậm chức 5/2026) thận trọng.
Rủi ro tăng lãi suất thêm vẫn hiện hữu — đặc biệt nếu CPI Mỹ tiếp tục cứng.

**Trung Quốc:** PMI sản xuất NBS tháng 7: **49,2** (tháng 6: 50,3) — tháng thứ 5 dưới ngưỡng 50.
PMI phi sản xuất: 49,0. Trung Quốc là đối tác thương mại lớn nhất của VN; suy yếu kéo dài ảnh
hưởng chuỗi cung ứng nguyên vật liệu và cầu nhập khẩu hàng VN.

**Giá dầu Brent:** Biến động mạnh tháng 7–8: đáy 69 USD (đầu T7, sau MOU Mỹ-Iran) → đỉnh 105 USD
(23/7, căng thẳng Hormuz) → **~85 USD** (24/8/2026). J.P. Morgan dự báo bình quân Q3: 86 USD.
Biên độ ±35% trong 2 tháng phản ánh rủi ro địa chính trị cao, ảnh hưởng chi phí sản xuất và lạm phát nhập khẩu VN.

**VIX/Biến động toàn cầu:** Bất định Fed, địa chính trị Trung Đông, PMI Trung Quốc suy yếu — môi
trường rủi ro toàn cầu đang ở mức cao hơn bình thường trong tháng 8/2026.

---

### 5.4 Đánh giá rủi ro khủng hoảng

**Verdict: KHÔNG CÓ CRISIS SIGNAL**

Đối chiếu với framework Bobby (Loại 1 / Loại 2):

| Chỉ báo cảnh báo sớm | Ngưỡng nguy hiểm | Mức tháng 8/2026 | Kết quả |
|---|---|---|---|
| CPI YoY | ≥6% (PIT filter) / ≥8% (STRUCTURAL) | **4,45%** (T7) | ✅ Dưới ngưỡng |
| Lãi tiết kiệm 12M | ≥9% (PIT filter block) | ~6,5–7% (ước tính) | ✅ Dưới ngưỡng |
| Tăng trưởng tín dụng | ≥30% | **~15%/năm** (trong target) | ✅ Bình thường |
| NPL hệ thống ngân hàng | ≥5% | **2,01%** | ✅ Bình thường |
| Cán cân vãng lai | Xu hướng xấu nhiều quý | Đang xấu đi (FDI-driven) | ⚠️ WATCH |

**Kết luận:** Không có chỉ báo cốt lõi nào của Loại 1 (excess-credit/inflation structural) bị kích
hoạt. Macro VN đang trong **pha tăng trưởng lành mạnh** — GDP +8,18% H1, sản xuất +11,4%, tiêu dùng
+13%. Rủi ro chủ yếu đến từ bên ngoài (Fed/Trung Quốc/giá dầu), chưa yêu cầu hành động phòng thủ.

**Danh sách WATCH (theo dõi, chưa hành động):**
1. CPI tiệm cận trần 4,5%; Bloomberg dự báo 4,8% cuối năm — theo dõi xem có vượt 5%+ không
2. Thâm hụt thương mại đảo chiều lớn (-20,52 tỷ USD 7T) — theo dõi dự trữ ngoại hối
3. PMI Trung Quốc dưới 50 tháng thứ 5 liên tiếp — rủi ro chuỗi cung ứng
4. Fed bất định tháng 9 — nếu tăng lãi có thể tái áp lực tỷ giá như Q4/2022

*Ngưỡng kích hoạt PIT filter sản phẩm (tham chiếu): CPI≥6% OR lãi tiết kiệm≥9% → block capit_margin_lever. Cả hai đang còn đệm an toàn đáng kể tháng 8/2026.*

---

## 6. PHÍ & CHI PHÍ
> **Người phụ trách: Taylor** · Nguồn: execution_logs/dnse_raw_{date}.jsonl (filter by account_no) + §6 coding_guidelines

| Khoản mục | SpaceX | ZaloPay |
|---|---:|---:|
| Giá trị mua trong tháng | *[TBD]* | *[TBD]* |
| Giá trị bán trong tháng | *[TBD]* | *[TBD]* |
| Tổng giá trị giao dịch | *[TBD]* | *[TBD]* |
| Phí giao dịch (0,075%/lượt) | *[TBD]* | *[TBD]* |
| Thuế bán (0,1%) | *[TBD]* | *[TBD]* |
| Lãi vay margin | *[TBD] (nếu có)* | 0 (cash-only) |
| Phí quản lý / hiệu suất | **0** | **0** |

*[TBD — Taylor điền sau 01/09, dùng `reconcile_equity.py` filter account_no tường minh]*

---

## 7. NHẬT KÝ SỰ KIỆN THÁNG
> **Người phụ trách: Mike** · Nguồn: bus events (inbox/Taylor.jsonl + inbox/SpaceX.jsonl), KB, Discord topic Trading Daily

### 7.1 Signal HOLD toàn bộ từ 21/08 (VPI)
HOLD_ALL áp dụng cho cả 2 tài khoản đến 2026-09-16 (quyết định user 19/08).
Tín hiệu BAL mới phát sinh → escalate hỏi, không tự mua.

### 7.2 capit_margin_lever LIVE từ 24/08
`enabled=True`, `f=1.3`, `gate=dd52≤−20%`, `loan_package_id=1840 (RocketX)`.
Mỗi ngày có CAPIT margin phải chạy `approve_margin_day.py` trước bot.

### 7.3-7.X Sự kiện khác
*[TBD — Mike điền sau 31/08 từ bus events]*

---

## 8. DANH MỤC CUỐI THÁNG (31/08/2026)
> **Người phụ trách: Taylor** · Nguồn: DNSE API positions 31/08 (same-day = DNSE API, không dùng BQ §6 coding_guidelines)

### 8.1 SpaceX — *[TBD]* mã
*[TBD — lấy positions từ DNSE API sau khi phiên 31/08 đóng cửa]*

### 8.2 ZaloPay — *[TBD]* mã
*[TBD — nhớ tách DGC excluded, tính % active_nav]*

### 8.3 Ghi chú rủi ro tập trung
*[TBD — Spyros audit cuối tháng]*

---

## 9. CÔNG BỐ SỰ CỐ & KHOẢNG TRỐNG SỐ LIỆU
> **Người phụ trách: Mike** · Nguồn: kb/incidents/retro/, bus events, ops_health_check

*[TBD — điền sau 01/09. Nguyên tắc: công bố MỌI sự cố ảnh hưởng NAV/giao dịch/số liệu, kể cả đã tự khắc phục]*

Hạng mục đã biết cần theo dõi:
- CAPIT episode 2026-07-20 (NCT/PVT/SAB/SIP/VNM): còn ~36 phiên đến 60-phiên lock (~đầu 10/2026)
- Khoảng trống số liệu tồn tại từ tháng 7 (Mục 8.3 report T7 #4-7): cập nhật trạng thái

---

## 10. TRIỂN VỌNG & VIỆC CẦN LÀM
> **Người phụ trách: Mike + DollarBill** · Nguồn: current_ops.md + macro §5 + kết quả tháng

### 10.1 Bối cảnh hệ thống bước sang tháng 9
*[TBD — điền sau 31/08, tham chiếu §5 Vĩ mô Bobby]*

### 10.2 Rủi ro chính tháng 9
*[TBD]*

### 10.3 Việc cần làm — có người phụ trách và hạn nghiệm thu

| # | Việc | Người phụ trách | Hạn |
|---|---|---|---|
| 1 | Cập nhật CPI thực tế tháng 8 vào §5 khi TCTK công bố (06/09) | **Bobby** | 07/09/2026 |
| 2 | Verify fill thật capit_margin_lever lần đầu (sau khi CAPIT signal kích hoạt) | **Spyros** | Khi có fill |
| *[TBD]* | | | |

---

## 11. PHỤ LỤC — PHƯƠNG PHÁP & LƯU Ý
> **Người phụ trách: Taylor** · Cập nhật nếu có thay đổi pipeline so với tháng 7

### 11.1 Pipeline xác minh số liệu (bắt buộc, không có ngoại lệ)
*(Giống §10.1 report T7 — Taylor xác nhận sau 01/09 có thay đổi gì không)*

### 11.2 Cạm bẫy số liệu đặc thù tháng 8
*[TBD — Taylor điền nếu phát hiện trap mới]*

### 11.3 Quy ước
- Giá mark-to-market = giá đóng cửa phiên cuối kỳ
- Số liệu cùng ngày (định giá lệnh, sức mua) = DNSE API trực tiếp, KHÔNG dùng BQ
- Cổ tức tiền mặt = bắt buộc dùng `dividend_adjusted_return.py` (§21 coding_guidelines), hiển thị cả gộp lẫn ròng (−5% thuế TNCN)
- Phí: giao dịch 0,075%/lượt; thuế bán 0,1%; lãi margin ~12,5%/năm (chưa xác minh với DNSE)
- KHÔNG báo cáo Sharpe/Sortino/Calmar — cần tối thiểu 6 tháng NAV ngày (milestone: 01/01/2027)

### 11.4 Công bố tuân thủ
- Đây không phải khuyến nghị đầu tư. Kết quả quá khứ không đảm bảo kết quả tương lai.
- Mọi số liệu trace được về nguồn broker; số chưa trace được ghi rõ là thiếu/ước tính.

---

*Báo cáo tháng 08/2026 · Tổng hợp từ hệ thống giám sát vận hành nội bộ, đối soát với dữ liệu DNSE API và BigQuery.*
*Template tạo 25/08/2026; điền đầy đủ sau 01/09/2026.*
*Báo cáo tuần chi tiết: SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md · ..._08-10_to_08-14.md · ..._08-17_to_08-21.md · ..._08-24_to_08-28.md (TBD)*
