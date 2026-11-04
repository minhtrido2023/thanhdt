# Đề xuất (KHÔNG sửa skill) — macro_snapshot_asof cho skill `due-diligence` và prompt Bobby

## 1. Bước ngắn cho skill `due-diligence` (đặt sau "lấy BCTC gốc", trước "Taylor DD")
> **Bước macro (bắt buộc, 1 lệnh):** `python3 mike/bin/macro_snapshot_asof.py --asof <hôm nay> --format md`
> (sau `source wc_env.sh`). Dán khối vào mục **"Điều thị trường chưa tính"** của dossier: chọn các chỉ báo
> theo bảng ánh xạ ngành→chỉ báo ở cuối khối (bán lẻ→retail/cpi; xây dựng-thép-xi măng→gdp_construction/IIP/FDI;
> KCN→FDI/IIP/PMI; xuất khẩu-logistics→exports/trade_balance/PMI/USDCNY; ngân hàng→policy/interbank/spread/bond_10y Δ;
> tiêu dùng→ô tô/du lịch/lương). Quy tắc: (a) chỉ trích dòng có cờ `ok`; dòng `STALE`/"KHÔNG CÓ DỮ LIỆU" ⇒ ghi
> "chưa có số", không điền số cũ; (b) `vn_bond_10y` chỉ dùng Δ; (c) đây là bối cảnh DISPLAY-ONLY — không đổi
> định giá/biên an toàn chỉ vì một chỉ báo, và không gắn gate/sizing; (d) lỗi script (rc=2) ⇒ nêu thẳng trong báo cáo.

## 2. Dòng nhắc cho prompt Bobby (macro-strategist, đọc MÙ)
> "Bối cảnh vĩ mô bên dưới là snapshot **tại as-of <ngày>**, đã áp độ trễ công bố bảo thủ (không có dữ liệu công bố
> sau as-of) và KHÔNG chứa forward return/diễn biến thị trường sau as-of. Với episode lịch sử, tạo snapshot bằng
> `macro_snapshot_asof.py --asof <ngày trước episode>`; KHÔNG tự tra số liệu sau as-of. Series ghi 'KHÔNG CÓ DỮ LIỆU'
> hoặc STALE = chưa biết, đừng suy diễn."

⚠ **Caveat vintage:** giá trị lịch sử là bản hiệu chỉnh HIỆN HÀNH (bảng không có vintage, backfill 2026-10-30), không phải số công bố lúc đó.
Δ của `vn_gdp_construction` (định nghĩa gãy: luỹ kế YTD tới Q4/2023, theo quý từ Q1/2024) và Δ3T của `vn_fdi` (luỹ kế YTD) bị tắt; `vn_interbank_3m` lag 3 ngày.

Lưu ý khi dùng: as-of lịch sử chỉ đúng PIT khi bảng lag trong code đúng — lag của `vn_fx_reserves` (90d) và `vn_wages` (60d)
không có nguồn lịch (lấy lớn); nguồn dẫn trong docstring script. Bảng `macro_indicator` không có ngày công bố thật; nếu cần PIT chặt
hơn ⇒ quyết định riêng của user (nhờ bq_admin thêm cột), không thuộc đề xuất này.
