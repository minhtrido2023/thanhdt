# Bước 0 — xác nhận tiền đề correlation-cluster xuyên-ICB (2026-09-10)

Job `Taylor_20260910_150633`. Chỉ xác nhận tiền đề — KHÔNG backtest, KHÔNG forward return, KHÔNG
đề xuất wire.

## Dữ liệu / scope
- `tav2_bq.ticker` Close (adjusted), 2018-01-02 → 2026-09-10 (2.167 phiên full-sample) + cửa sổ
  gần nhất 252 phiên (2025-09-05 → 2026-09-10).
- Universe: 352 mã trong `tav2_mike.universe_pit` (snapshot ngày mới nhất, `in_universe=true`).
  **Lưu ý PIT**: dùng membership snapshot HÔM NAY áp ngược lại toàn 2018-2026 — hợp lệ cho
  nghiên cứu mô tả cấu trúc tương quan thuần tuý (không phải backtest sinh tín hiệu), nhưng KHÔNG
  phải universe PIT-đúng nếu bước 1-2 tiến tới backtest thật.
- ICB: `tav2_bq.corporate_action.icb_code_lv1` (mode/ticker) — mức 1 rất thô (Banks/Financial
  Services đã tách 2 code khác nhau dù cùng "Financials"; một số mã dầu khí lưu code "1" thay vì
  "0001" — cùng ý nghĩa, khác chuỗi).
- Market-cap proxy: Close mới nhất × `OShares` mới nhất (`ticker_financial`).
- threads=1, self-check thủ công (tái chạy dry-run trước mỗi query, BQ cost <120MB/query).

## 1. Case đã biết (Vingroup, Masan) vs baseline
So tương quan trung bình pairwise (log return) với 2 baseline: (a) cùng ICB lv1 sector, (b) pair
ngẫu nhiên cùng vốn hoá (|Δlog mktcap|≤0.5, N=2.000 draw/cửa sổ).

| Nhóm | Full-sample (2018-2026) | percentile/z vs control | Last 252d | percentile/z vs control |
|---|---|---|---|---|
| **Vingroup** VIC/VHM/VRE | 0.561 | p99.5 (z=+2.80) | 0.656 | p99.2 (z=+2.87) |
| **Masan** MSN/MCH/MML/MSR | 0.226 | **p55.8 (z=+0.08)** | 0.401 | p87.8 (z=+1.15) |
| Baseline-a same-ICB (RE 8600) | 0.261 (sd 0.129, n=1653 pairs) | — | 0.290 | — |
| Baseline-a same-ICB (Consumer 3000) | 0.198 (sd 0.115, n=990) | — | 0.201 | — |
| Baseline-b cap-matched random | 0.217 (sd 0.123, n=2000) | — | 0.230 (sd 0.148) | — |

**Kết luận bước 1**: Vingroup XÁC NHẬN mạnh, ổn định cả 2 cửa sổ (cao hơn CẢ baseline sector lẫn
control ~2.5-3 sd). **Masan KHÔNG xác nhận ở full-sample** (gần như bằng random, p55.8) — chỉ
xuất hiện ở cửa sổ gần đây (p87.8, z+1.15, chưa mạnh). Đọc: Masan family correlation có thể là
hiện tượng ĐANG NỔI GẦN ĐÂY / theo giai đoạn, không phải cấu trúc bền suốt 8 năm — khác Vingroup.
Cảnh báo n nhỏ: Masan chỉ 6 cặp, Vingroup chỉ 3 cặp — percentile dùng control N=2000 nên đáng tin
hơn so sánh naive, nhưng biến động từng cặp đơn lẻ vẫn có thể nhiễu.

## 2. Quét toàn universe (data-driven, ngưỡng |corr|>0.6, cluster = connected components ≥3 mã)
Chạy cả 2 cửa sổ. **2 cụm xuyên-ICB sạch nhất, không đoán trước tên**:

- **Viettel-family**: CTR(Industrials)/VGI(Telecom)/VTP(Industrials) — avg corr full=0.483 (p97.4,
  z+2.16), recent=0.715 (p99.5, z+3.27). 3 mã, cả 2 cửa sổ đều mạnh, ổn định.
- **PVN-family**: BSR/GAS/OIL/PLX/PVB/PVC/PVD/PVS/PVT (9 mã, sở hữu chung Tập đoàn Dầu khí VN —
  sự thật công khai, không suy diễn) — avg corr full=0.615 (p99.9, z+3.23, N=36 cặp), recent=0.666
  (p99.2, z+2.94). Mạnh nhất + robust nhất (N cặp lớn nhất, bền cả 8 năm lẫn 252d gần đây). Đa số
  thành viên cùng share ICB "1" (dầu khí, chỉ khác cách lưu "1" vs "0001"); 2 mã thật sự KHÁC
  ngành chính thức là GAS (Utilities 7000) và PVT (Industrials/logistics 2000) — vẫn tương quan
  cao với lõi, đây mới là phần "xuyên-ICB thật".

**2 cụm KHÔNG đáng tin — nghi artifact phương pháp, không phải phát hiện mới**:
- Cụm 81-mã (recent) / 32-mã (full): chủ yếu Banks(8301)+Financial Services(8700), lẫn thêm vài
  mã BĐS/thép. avg_internal_corr chỉ 0.49-0.51 — THẤP HƠN ngưỡng 0.6 dùng để nối cạnh → đây là
  **chaining bắc cầu** của thuật toán connected-components (A-B>0.6, B-C>0.6 nhưng A-C thấp), KHÔNG
  phải 1 clique thực sự cùng di chuyển. Về bản chất đây cũng chỉ là "Financials" supersector đã
  biết (bank+broker cùng beta lãi suất/margin), bị tách thành 2 ICB-code khác nhau trong dữ liệu.
- IDC/KBC/SIP/SZC/VGC (KCN/khu công nghiệp): 4/5 đã cùng ICB 8600 (BĐS); VGC (2000) khác nhãn
  nhưng mảng KCN của VGC thực chất CÙNG ngành kinh tế (nhãn ICB lv1 của VGC bị gán "Industrials"
  dù có mảng BĐS KCN lớn) — đây là lỗi phân loại ICB, không phải bằng chứng sở hữu chéo mới.

## 3. Đối chiếu sweep #20 "Holding company/conglomerate SOTP" (đã đóng, `kb/KNOWLEDGE.md` §7)
**KHÔNG trùng lặp — khác cả câu hỏi lẫn universe:**
- #20 là lens ĐỊNH GIÁ (coverage ratio = Parent MC / Σ stake×sub MC) cho 4 cặp: VIC→VHM,
  MSN→MCH+TCB, GEX→VGC+GEE, GVR→PHR+DPR+TRC. Không hề chạy correlation clustering, không quét
  toàn universe, không đụng Viettel-family hay PVN-family.
- Vingroup/Masan trong bước 0 này TRÙNG TÊN công ty với #20 nhưng khác trục hoàn toàn (correlation
  giá pairwise, không phải valuation discount/premium).
- **Nhưng #20 đã để lại 1 tiền lệ bắt buộc phải tôn trọng**: kết luận của #20 là *"discount does
  NOT mean-revert — deep discount is a TRAP"* và *"LENS NOT BOOK, DO NOT WIRE"* cho ĐÚNG các cặp
  Vingroup/Masan/GEX/GVR bằng phương pháp khác. Cộng với Rule 3 giữ vững 20/20 sector sweep (mọi
  cách gộp nhóm trong hệ thống này chỉ có giá trị LENS, chưa từng thành BOOK sinh lời độc lập) —
  đây là prior mạnh nhất chống lại kỳ vọng correlation-cluster rotation sẽ khác biệt.

## Trả lời 2 câu hỏi của dispatch
1. **Tiền đề tương quan-xuyên-ngành có THẬT không?** CÓ, nhưng KHÔNG ĐỒNG ĐỀU: Vingroup + Viettel-
   family + PVN-family xác nhận mạnh, ổn định cả 2 cửa sổ thời gian (p97-99.9, z+2.2 đến +3.3).
   Masan CHỈ xác nhận yếu và GẦN ĐÂY (không có ở full-sample) — không nên coi ngang hàng 3 case
   kia. 2 cụm lớn tìm được qua quét toàn universe là artifact phương pháp (sector beta chaining),
   không phải phát hiện mới.
2. **Có phải hiện tượng MỚI (chưa bị #20 phủ hết) không?** CÓ — góc nhìn correlation-cluster và 2
   family cụ thể (Viettel, PVN) là mới, KHÔNG bị #20 phủ. Nhưng #20 đã cảnh báo trước bằng phương
   pháp khác đúng NHÓM TÊN GẦN NHẤT (Vingroup/Masan/GEX) rằng grouping-based edge ở đây LỊCH SỬ
   chưa từng vượt qua LENS-not-BOOK — đây là base rate cần neo vào trước khi pre-register bước 1.

## Khuyến nghị cho bước 1 (chưa làm, chờ duyệt)
Nếu tiến tới bước 1 — pre-register hypothesis nên tách RIÊNG theo độ mạnh tiền đề vừa đo, KHÔNG
gộp chung "correlation-cluster" thành 1 giả thuyết: (a) PVN-family/Viettel-family (tiền đề mạnh,
ổn định) mới đáng ưu tiên test cluster-RS; (b) Masan loại khỏi test chính hoặc tách case riêng vì
premise yếu/mới nổi; (c) 2 cụm tài chính lớn KHÔNG đưa vào — đã xác định là artifact, không phải
cluster thật. Thanh chắn bắt buộc từ bối cảnh AMH cùng ngày vẫn giữ nguyên: cluster-RS phải sinh
alpha OOS hậu-2020, nơi momentum cá lẻ (SIGNAL_V11) đã chết cấu trúc 8/8 ô test.
