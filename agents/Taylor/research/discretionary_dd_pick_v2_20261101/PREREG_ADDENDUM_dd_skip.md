# PREREG_ADDENDUM — loại mã đã DD cho tới BCTC quý mới (job Taylor_20261101_140717)

Chỉ đạo user 2026-11-01 21:06 ICT: "DD do chính tôi chỉ định đã làm DD sau khi có báo cáo quý mới nhất rồi
thì không cần đề xuất làm lại. Chỉ làm lại dạng DD thiên về rủi ro ngành nghề, pháp luật để quyết định có
nên cut-loss không."

PREREG gốc (md5 12d35014) KHÔNG đổi; trọng số W_V/W_E/W_R, TOP_K, MoS, FRESH_DAYS không đổi. Chỉ đổi QUY TẮC LOẠI TRỪ (§3):
1. Mã có DD (thư mục `dd_<MÃ>_<ngày>*` kể cả blind/reweight · `kb/projects/<mã>-dd-*-<ngày>.md` · claim trong
   sổ) với ngày DD >= ngày công bố BCTC quý MỚI NHẤT (`known` PIT, như lane C) ⇒ loại.
   Trở lại pool khi có BCTC quý mới công bố SAU ngày DD. DD cùng ngày công bố tính là SAU BCTC.
2. Không có ngày công bố ⇒ fallback `DD_FALLBACK_DAYS = 120`.
3. `DD_COOLDOWN_DAYS = 90` chỉ còn cho mã mới được ĐỀ XUẤT (picked) mà chưa có DD.
4. Sổ claim thêm `source` (picker mặc định | user). `--claim ... --source user` ghi sổ nhưng KHÔNG trừ suất;
   trần chỉ áp cho source=picker. Bản ghi cũ không có `source` coi là picker.
5. Mã đang giữ vẫn loại như cũ. DD rủi ro ngành/pháp lý phục vụ cut-loss là luồng KHÁC (cutloss_crisis_dd),
   không đi qua bộ chọn này.
Hạn chế đã biết: `known` lấy từ `fin` tại asof (quý biết < asof); BCTC công bố giữa asof và ngày chạy không thấy.
