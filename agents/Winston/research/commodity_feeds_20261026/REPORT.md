# REPORT — Dữ liệu cước (job Winston_20261025_085247, 2026-10-25) — tiếp job 062823

## (a) Mendeley DOI 10.17632/t76ckh2ygg.1 — TẢI ĐƯỢC
- Đường qua: `https://data.mendeley.com/public-api/datasets/t76ckh2ygg` (JSON công khai, không anti-bot) → `download_url` trực tiếp. Không đăng ký, không trả phí.
- File: `bdi_mendeley.xls` (272.896 B), sha256 `0689b716f21a10d9510bb6f1739a18c296c1efb8a8c5e4450788e480a15791d4` — **khớp** hash công bố của API.
- Giấy phép **CC BY 4.0** (phải ghi công: Totakura, B.R., Mendeley Data, DOI trên). `published_date` = 2020-11-09; v1 duy nhất; tác giả sửa file 2019-10-03.
- ⚠️ **KHÔNG có cột BDI headline.** Cột thật: `Date, HSI, SI, PI, CI, DTI, CTI` = Handysize, Supramax, Panamax, Capesize, **DTI/CTI (tanker dirty/clean — chưa xác minh đúng là BDTI/BCTI, đừng gọi vậy)**. Sheet 2 "tanker index" chỉ có cột ngày (rỗng dữ liệu).
- CSV chuẩn hoá: `freight_subindices_mendeley_2012_2019.csv` (sha256 `0886f6caaf0d76ff9061ba9f48344e00566d8ff93765a10270301ec0196ce4b3`). 1.749 ngày, 2012-08-01→2019-07-31, 0 trùng ngày, 0 ô trống ở 4 chỉ số dry; chỉ có khoảng trống Giáng sinh/Tết (9–11 ngày/năm, bình thường). CTI trống 846 dòng (2012-08-01→2015-12-15).
- **Trùng khớp với `data/bdi_daily_real.csv`: KHÔNG kiểm được** — file local chỉ 115 dòng, 2026-05-05→2026-10-22; không giao nhau với 2012–2019. Cũng không có BDI headline để so. Chưa kiểm chéo độc lập tính đúng của số liệu (chỉ sanity: Cape 3.657 / Panamax 1.891 ngày 31/07/2019 hợp lý theo trí nhớ, KHÔNG phải xác minh).
- **Khoảng trống chưa có nguồn: 2019-08-01 → 2026-05-04** (~6,8 năm), gồm toàn bộ đỉnh cước 2021. Dùng được làm backtest 2012–2019 cho 4 sub-index, không đủ cho giai đoạn gần.

## (b) Freightos FBX — KHÔNG có CSV lịch sử miễn phí không cần đăng ký
- `fbx.freightos.com` → 301 → `www.freightos.com/enterprise/terminal/freightos-baltic-index-global-container-pricing-index/`.
- "View Data for Free" dẫn tới **trang sign-up** (cần tài khoản — ngoài phạm vi được phép). Trang nói xuất CSV/PNG và dữ liệu chi tiết thuộc **gói trả phí**; bậc free: tra cứu cho biết ~30 ngày lịch sử (từ kết quả tìm kiếm, không xác nhận trên trang). Baltic Exchange giữ lịch sử từ 2016 cho hội viên.
- Trang nói nhà báo/nhà phân tích có thể **xin CSV qua email** (địa chỉ bị che). → Đã soạn nháp `fbx_email_draft.md`. **KHÔNG gửi.** Điều khoản sử dụng/tái phân phối chưa đọc được (trang T&C không lấy).
- API `apidocs.freightos.com` (Terminal API) — chưa rõ có phủ FBX; không thử vì cần khoá.
