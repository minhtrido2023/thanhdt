# Khung ngành — NGÂN HÀNG (26/10/2026)

> Khung bối cảnh cấp ngành, KHÔNG phải tín hiệu mua/bán, không nói lợi suất kỳ vọng cổ phiếu. Đọc vĩ mô
> (phân loại khủng hoảng, tín dụng/GDP) thuộc Bobby và `kb/projects/vn-realestate-structural-risk-20260826.md`.
> Nhãn nguồn: **[BQ]** = `tav2_bq.ticker_financial`, file `bq_fin_funnel_sectors_2025Q1_2026Q3.csv` ·
> **[DEP]** = `data/deposit_rate_vn_events.csv` / `data/cctg_rate_vn_events.csv` (CANONICAL-PROXY) ·
> **[W]** = báo chí qua WebSearch 26/10, CHƯA mở bản gốc NHNN/BCTC (URL ở cuối).

**Mã funnel thuộc ngành (10)**: ABB, CTG, HDB, MBB, NAB, SHB, TPB, VBB, VCB, VPB — 121 lượt (79 làn C tăng trưởng LN, 42 làn B hạn ngạch).

## Pha chu kỳ: **mở rộng muộn — lợi nhuận đỉnh tăng tốc, chi phí vốn và chất lượng tài sản bắt đầu ngược chiều**
| Bằng chứng | Số | Nguồn |
|---|---|---|
| LNST gộp 10 NH funnel YoY | Q1/26 **+26,4%** → Q2/26 **+41,9%** (56,9 nghìn tỷ vs 40,1) | [BQ] |
| Q3/26 đã công bố trong BQ | VPB +18,8% (8.644 vs 7.276 tỷ) · ABB +101% (1.028 vs 511) | [BQ] |
| Tín dụng toàn hệ thống 30/9/26 | +11,59% YTD, +16,69% YoY; NHNN nói "đang chậm lại" | [W] NHNN họp báo 7/10 |
| LS huy động bình quân giao dịch mới | 6,38% (20/9), **+1,15 điểm %** so với cuối 2025 | [W] |
| Big-4 12T online | 6,8% không đổi 20/07→26/10 · CCTG 12T Big-4 cao nhất 7,4% | [DEP] |
| Chỉ đạo hạ LS | CV 9608/NHNN-CSTT 18/10: giảm LS niêm yết ≥0,5đ% kỳ hạn ≥6T; 19–20/10 ≥14 NH cắt | [W] |
| Liên ngân hàng qua đêm | 6,95% (30/9) → 0,72% (7/10) → ~4,8% (12/10) — biến động mạnh | [W] |
| Chất lượng tài sản (27 NH niêm yết, Q2/26) | NPL 2,01% đi ngang · nhóm 2 +14bp lên 1,38% · **bao phủ 79%, thấp nhất từ Q2/2018**, giảm 2 quý liền | [W] Yuanta |
Diễn giải: LN tăng nhờ tín dụng +16–17% YoY và (ở một số NH) trích lập thấp — bao phủ giảm là nguồn LN
"mượn" từ tương lai. Chi phí vốn đã lên ~1đ% trong năm; chỉ đạo 18/10 kéo ngược lại nhưng LS cho vay cũng bị yêu cầu giảm 1,5–2đ% cho nhóm ưu tiên [W] ⇒ NIM bị ép 2 đầu.

## Động lực 2–3 quý tới
1. **NIM**: huy động giảm 0,5đ% (lag theo kỳ hạn 6–12T) vs cho vay ưu tiên giảm 1,5–2đ% ⇒ ước lượng NIM ngành đi ngang/giảm nhẹ (MBS cùng hướng [W]). Phân hoá: NH huy động sỉ/LDR cao chịu nặng hơn.
2. **Trích lập**: bao phủ 79% + nhóm 2 tăng ⇒ áp lực phải trích lại; là biến số lớn nhất của LN 2027.
3. **Thông tư 25/2026** (hiệu lực 1/7): trần vốn ngắn hạn cho vay trung dài hạn 30%→40%, KBNN vào mẫu LDR ⇒ nới dư địa cho vay [W].
4. Luật sửa đổi Luật NHNN/TCTD hiệu lực **1/12/2026** — chưa kiểm nội dung [W].

## Rủi ro cấu trúc / chính sách
- Tập trung BĐS (xem tài liệu vĩ mô; tỷ trọng BĐS/tổng dư nợ 25,5% theo Bobby 26/08). NHNN nới: KCN/NOXH (29/5) và du lịch–nghỉ dưỡng (CV 8509, 16/9) không tính vào tín dụng BĐS.
- TPDN BĐS đáo hạn Q4/26 ~77 nghìn tỷ, Q2/27 ~84 nghìn tỷ (VIS Rating) [W] — rollover qua NH.
- Áp lực tỷ giá Q4 (Yuanta [W]) giới hạn dư địa hạ LS.
- Can thiệp hành chính lên giá vốn/giá cho vay (CV 9608) — biên lợi nhuận ngành bị chính sách quyết định, không chỉ cung cầu.

## Chỉ báo dẫn dắt (nguồn cụ thể)
| # | Chỉ báo | Nguồn | Tần suất |
|---|---|---|---|
| 1 | Big-4 12T online + CCTG 12T | `deposit_rate_vn.py` / `cctg_rate_vn.py` (registry `macro/`, CANONICAL-PROXY, refresh tuần) | tuần |
| 2 | Tín dụng/huy động YTD toàn hệ thống | NHNN họp báo; `data/fiinprox_money_credit_monthly_*.csv` (DERIVED, snapshot trial — không tự tươi) | tháng |
| 3 | LNST quý 10 NH funnel YoY | `tav2_bq.ticker_financial` NP_P0 vs NP_P4 (CANONICAL `fundamentals/`) | quý |
| 4 | NPL + nhóm 2 + bao phủ gộp 27 NH | BCTC quý / tổng hợp Yuanta-TCBS (chưa có feed — thủ công) | quý |
| 5 | Liên ngân hàng qua đêm | NHNN; `fiinprox_rates_snapshot_20260927` chỉ là snapshot một lần — **không có feed sống** | ngày |

## DỰ BÁO CÓ THỂ BÁC BỎ — kiểm chứng **2027-05-20** (sau mùa BCTC Q1/2027)
**F-BANK-1**: Tăng trưởng LNST gộp 10 NH funnel **giảm tốc**: YoY của Q1/2027 nằm trong **[0%, +25%]**, tức thấp hơn
rõ mức +26,4% của Q1/2026 và +41,9% của Q2/2026.
- Chấm: `SUM(NP_P0)/SUM(NP_P4) − 1` trên `ticker_financial`, `quarter="2027Q1"`, đúng 10 mã trên. Cần ≥9/10 mã có số.
  Trong khoảng ⇒ ĐÚNG; > +25% ⇒ SAI (chu kỳ mạnh hơn tôi nghĩ); < 0% ⇒ SAI phía xấu (trích lập/NIM sập nhanh hơn).
- Cơ chế đặt cược: NIM bị ép 2 đầu + phải trích lập lại khi bao phủ ở đáy 8 năm, trong khi tín dụng đã "đang chậm lại".
**F-BANK-2 (phụ)**: Bao phủ nợ xấu gộp 27 NH niêm yết Q4/2026 hoặc Q1/2027 **≤ 85%** (không hồi lại vùng ≥ 90%).
Chấm từ tổng hợp ngành công bố (Yuanta/TCBS), ghi rõ nguồn khi chấm.

## Thiếu dữ liệu (nói thẳng)
Chưa có số Q3/26 công bố của VCB/CTG/MBB/TPB/HDB, NIM ngành Q3, NPL Q3. Số [W] là tóm tắt kết quả tìm kiếm,
chưa đối chiếu văn bản gốc. Cột `GPM_P0` của BQ cho NH không phải NIM — không dùng.

URL chính: tapchicongthuong.vn …556187 (tín dụng 30/9) · thanhtra.com.vn …98015f8ce (LS, liên NH) · tapchikinhtetaichinh.vn …169892 (CV 9608) ·
cafef.vn …188261021150259725 · tapchikinhtetaichinh.vn …166834 (NPL/bao phủ Q2, Yuanta) · thoibaotaichinhvietnam.vn …199482 (TT25) ·
vnba.org.vn …23282 (luật sửa đổi) · tienphong.vn …post1881328 (TPDN đáo hạn). Đầy đủ: `sources_web_20261026.md`.
