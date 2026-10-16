# FTSE upgrade (hiệu lực 2026-09-21) — re-validate 3 tầng, job Taylor_20261013_114456
Kết luận: KHÔNG ĐỔI GÌ (0/24 đại lượng ngoài dải p5-p95 của 198 mốc giả; N=1 sự kiện, 16 phiên). Chi tiết + bảng:
`mike/kb/projects/ftse-upgrade-structural-break-20260921.md.proposed` § Kết luận.
Tái lập: `source wc_env.sh; cd <thư mục này>; $DNA_PYEXE pull.py` (BQ + curl VNDirect cho khối ngoại — urllib bị 403,
xem lệnh curl trong lịch sử job) → `measure.py` (→ results_table.csv, out_measure.txt, t3_capit_names.csv) →
`measure_fgn27.py` (→ out_fgn27.txt). Cắt dữ liệu tại 2026-10-12 (universe_pit max lúc đo).
Kiểm chéo: breadth trước/sau tính lại độc lập bằng SQL BQ = 0,2540 / 0,2548, khớp script.
Không dùng: ticker_prune cho universe (chỉ đọc cho CAPIT vì production còn ghim CAPIT_POOL_SOURCE="prune"), cột profit_*, forward return.
