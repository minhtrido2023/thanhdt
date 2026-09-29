# Bước 1 — Pre-registration: cluster relative-strength (RS) momentum test

Job `Taylor_20260910_152624`. Khoá TRƯỚC khi tính bất kỳ return nào. Không sửa sau khi đã chạy
backtest — nếu phải sửa, ghi rõ AMENDMENT + lý do, không âm thầm đổi.

## 0. Scope (đã duyệt tối 2026-09-10)
Chỉ 2 cụm: **PVN-family** (BSR/GAS/OIL/PLX/PVB/PVC/PVD/PVS/PVT, 9 mã, premise pctl 99,9) và
**Viettel-family** (CTR/VGI/VTP, 3 mã, premise pctl 97-99,5). Masan loại (premise full-sample chỉ
pctl 55,8 ≈ ngẫu nhiên). 2 cụm "financial beta chain" + "KCN real estate" loại (method artifact).

## 1. Tín hiệu — khoá cứng, không grid-search
**Cluster_RS_200(t)** = [mean equal-weight log-return của các mã trong cụm, t−200→t phiên] −
[log-return VNINDEX, cùng 200 phiên]. Tức relative strength của cụm so với thị trường, cửa sổ
200 phiên giao dịch.

**Vì sao 200 phiên, không quét tham số khác:** đây CHÍNH XÁC là lookback `mom_200` đã dùng trong
nghiên cứu AMH cùng ngày (job Taylor_20260910_131906/B, kết luận momentum cá lẻ chết cấu trúc sau
2020). Tái dùng nguyên cửa sổ đã có sẵn — không tự chọn số mới — để đây là phép so sánh ngang hàng
thật: "cùng 1 công thức momentum, áp ở CẤP CỤM thay vì CẤP MÃ ĐƠN, có sống được ở chỗ cấp-mã-đơn
đã chết hay không". Không thử N khác (không 60/100/150) — tránh multiple-testing qua cửa hậu.

**Điều kiện tính**: một `form_dt` (lưới hàng tháng, ngày phiên đầu mỗi tháng — khớp quy ước
`series_by_month` của `fitness2.py`) chỉ hợp lệ khi TẤT CẢ mã trong cụm có đủ 200 phiên Close
liên tục trước `form_dt` (không NaN, không ngoại suy).

## 2. Câu hỏi kiểm định — chọn 1, khoá trước
**Giả thuyết A — cluster momentum/continuation** (ĐƯỢC CHỌN): Cluster_RS_200(t) cao có dự báo
Cluster fwd_3M(t) (lợi nhuận cụm từ t→t+60 phiên, equal-weight log-return, khớp quy ước
`profit_3M`/T+60 toàn fleet) cao hơn không? Tức cụm đang mạnh có tiếp tục mạnh không.

**Giả thuyết B — within-cluster rotation/mean-reversion** (BỊ LOẠI, không test): mã tụt lại trong
cụm có đuổi kịp mã dẫn đầu không. Đây là câu hỏi KHÁC (rotation nội bộ, không phải rotation giữa
cụm mạnh/yếu).

**Lý do chọn A, không test cả 2:**
- Khớp đúng nguyên văn ý user ("rotation giữa nhóm MẠNH/YẾU theo giai đoạn thị trường" = đổi giữa
  CỤM đang mạnh và CỤM đang yếu — đây là momentum/RS liên-cụm theo thời gian, không phải xoay vòng
  NỘI BỘ giữa các mã trong 1 cụm).
- Trả lời đúng câu hỏi Mike đặt ra khi duyệt: cluster-RS có phải MỘT dạng của chính momentum cá lẻ
  vừa chết (test A) hay là cơ chế khác (dòng vốn/sở hữu chung) — test A là phép so sánh trực tiếp
  nhất với kết luận AMH cùng ngày.
- Test cả A và B rồi báo cái thắng = multiple-testing bias đúng loại lỗi vừa cảnh báo ở bước 0.

## 3. Metric đánh giá
N=2 cụm — **không đủ cho cross-sectional IC theo tháng** (N=2 quan sát/tháng vô nghĩa thống kê).
Thay vào đó: với MỖI cụm riêng, tính **time-series correlation** giữa chuỗi Cluster_RS_200(t) và
Cluster_fwd_3M(t) lấy mẫu hàng tháng — bản chất là tự tương quan trạng thái RS của chính cụm đó
qua thời gian (không so cụm này với cụm kia).

Cửa sổ 200d trailing + 60d forward lấy mẫu hàng tháng ⇒ chồng lấn nặng ⇒ dùng **Newey-West t-stat**
(lag ~4 tháng, khớp `fitness2.py` MIN_M_REPORT/MIN_M_CONCLUDE convention) — KHÔNG dùng p-value
thường (N hiệu dụng nhỏ hơn N quan sát rất nhiều do overlap).

Bổ sung bắt buộc theo chỉ đạo dispatch (N quá nhỏ cho p-value đơn thuần): **sign-consistency theo
từng năm dương lịch** (leave-one-year-out) — đếm bao nhiêu năm trong cửa sổ OOS có IC cùng dấu với
IC gộp toàn kỳ.

## 4. IS/OOS — giới hạn dữ liệu phải nói rõ TRƯỚC khi chạy
Kiểm tra ngày niêm yết thật (từ panel Close non-null):
- PVN-family: mã cuối cùng đủ dữ liệu là OIL (bắt đầu 2018-03-07) → Cluster_RS_200 tính được sớm
  nhất ≈ 2019-01 (200 phiên sau đó). IS 2014-2019 theo quy ước chuẩn KHÔNG khả thi — 9 mã PVN-family
  đầy đủ chỉ tồn tại đồng thời từ 2018. IS thực tế chỉ còn ≈ 2019-01→2019-12 (~12 tháng, MỎNG).
- Viettel-family: mã cuối cùng là VTP (bắt đầu 2018-11-23) → Cluster_RS_200 tính được sớm nhất ≈
  2019-09. IS thực tế chỉ còn ≈ 2019-09→2019-12 (**~4 tháng, KHÔNG đủ kết luận**, n<10).
- **OOS 2020-01→2026-09 (~80 tháng) là cửa sổ CÓ ĐỦ LỰC** cho cả 2 cụm — đây là bài test QUYẾT
  ĐỊNH theo đúng rào chắn AMH: "nếu chỉ IS dương, OOS ≈0/âm → NO-GO, dừng ngay, không cần bước 2".
  IS (đặc biệt Viettel) sẽ được BÁO CÁO nhưng gắn nhãn non-conclusion-grade (n<10, theo đúng quy
  ước MIN_M_REPORT của `fitness2.py`), không dùng để quyết định GO/NO-GO.

## 5. Giới hạn ngoại suy — phải nói rõ, không giấu
Thành viên cụm (PVN-family, Viettel-family) được **xác định ở bước 0 bằng tương quan FULL-SAMPLE
2018-2026** — tức đã "nhìn thấy" cả giai đoạn OOS khi chọn thành viên cụm. Đây KHÔNG PHẢI look-
ahead trong bài test RS→fwd-return (RS_200(t) chỉ dùng dữ liệu ≤t, fwd_3M(t) chỉ dùng dữ liệu >t —
walk-forward đúng nghĩa cho CHÍNH tín hiệu này). Nhưng nó có nghĩa: đây KHÔNG phải bài test "liệu
ta có tìm ra đúng cụm này một cách ex-ante năm 2020 không" — cụm được neo bằng lý do kinh tế thật
(sở hữu chung Tập đoàn Dầu khí VN / Viettel, sự thật công khai, không suy diễn thống kê thuần) nên
chấp nhận được, nhưng phải ghi rõ giới hạn này trong kết luận cuối, không trình bày như OOS sạch
100%.

## 6. Quy tắc quyết định — khoá TRƯỚC khi thấy số
**GO (đủ điều kiện qua bước 1, đề xuất bước 2)** chỉ khi CẢ HAI cụm cùng thoả: OOS IC (2020-01→nay)
dương VÀ sign-consistent đa số năm (leave-one-year-out, ≥5/7 năm cùng dấu OOS). Yêu cầu CẢ HAI cụm
đồng thuận (không phải 1/2) — vì N=2 đã quá nhỏ, chỉ 1 cụm dương dễ là nhiễu, đặt thanh cao hơn để
tránh multiple-testing (2 cơ hội, báo cái thắng).
**MIXED (không đủ để GO, cũng không NO-GO dứt khoát)**: 1/2 cụm dương sign-consistent, cụm còn lại
không — báo cáo trung thực, khuyến nghị KHÔNG bước 2 (bằng chứng chưa đủ), không tự diễn giải có
lợi.
**NO-GO**: cả 2 cụm OOS IC ≈0 hoặc âm, hoặc không sign-consistent — dừng ngay, không bước 2, đúng
tiền lệ Rule 3 (20/20 sector sweep) + AMH momentum-death cùng ngày.

## 7. Self-check
Không phải backtest NAV (không có lệnh mua/bán, không vốn) — self-check ở đây là: (a) verify thủ
công Cluster_RS_200/fwd_3M cho 1 form_dt cụ thể bằng recompute tay từ panel.csv (đối chiếu số in
ra bởi script), (b) đối chiếu VNINDEX pull mới với vnindex.csv vừa lấy từ BQ (không dùng
`data/VNINDEX.csv` cục bộ — đã dừng cập nhật từ 2026-05-26, xem
`kb/data_registry/price-volume/vnindex_pe_mirror_col.md`).
