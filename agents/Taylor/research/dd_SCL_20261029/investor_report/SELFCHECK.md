# Tự kiểm — SCL_DD_investor_report_20261029 (job Taylor_20261029_055834, 29/10/2026)

(i) Số liệu: mọi số tính (TERP, giá trị quyền, FV 25.495, %/TERP, bear/bull, vốn hoá, định giá ngược, P/E/P/B/EV-EBITDA,
nợ ròng/EBITDA, pha loãng 2,595×, VinCons 58,5%, AR +40,9% QoQ, biên H1 39,4%, EPS ~565/+76%, ESOP 11,78 tỷ, P/E chuẩn hoá 20,2,
football field) tính lại bằng python trong phiên — khớp REPORT.md/BCTC (tr.1–5 đọc lại từ PDF scan). Sửa trong lúc tự kiểm:
vốn hoá PF 1.282,9→1.282,8; biên về 36% ≈ −39 (không phải −38) tỷ; câu "KL cao nhất ~2 tháng" → "cao nhất kể từ 21/08/2026" (đo trên price_raw.csv).
Đính chính so với REPORT.md (không do skeptic nêu): (a) ESOP 14–17 tỷ (giá giả định 25–28k) → ~11,8 tỷ theo đóng cửa 30/07/2026 = 22.800 [BQ];
(b) "AR +41% khi DT +8,6% QoQ" trộn DT thuần Q3 với DT gộp Q2 → so cùng cơ sở DT gộp: +14,6%; (c) sàn = UPCoM (DNSE secdef marketId=UPX).
(ii) Điểm skeptic đã đính chính — grep 0 hit: "bán trước GDKHQ", "lô lẻ/mồ côi", "≈ pha loãng/−8%" (TERP −8,0% chỉ là phép tính TERP),
"Long Thành", "QUALIFY ≤21.700", base mô tả đúng = ước LNST 2026.
(iii) 0 hit: SpaceX/ZaloPay/LAG/NAV/giá vốn/số CP nắm giữ/tên agent nội bộ.
(iv) Không có nhãn mua/bán cá nhân hoá; chỉ NON/AMBIGUOUS/QUALIFY + điều kiện.
Render: HTML qua bin/render_report_html.py (10 ảnh nhúng, 0 "Ảnh thiếu"); PDF 14 trang A4 pymupdf.Story, kiểm bằng mắt từng trang
(dấu tiếng Việt OK, bảng không tràn, không tách bảng qua trang — tránh lỗi Story vẽ lặp nền hàng bảng).
Giá 29/10: DNSE latest_trade 29.500 lúc 11:29:49 ICT (trong phiên).
