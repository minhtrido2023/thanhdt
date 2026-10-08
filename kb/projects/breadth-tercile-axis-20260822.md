# Trục 2 mặc định = breadth-tercile PIT — bằng chứng + định nghĩa tính chuẩn
> Chuyển nguyên văn từ `kb/canonical.md` (trim context_pack 2026-10-08). Quy ước + ranh giới vẫn ở file gốc.

## Chuyển từ kb/canonical.md L257-262 (trim 2026-10-08, Wags_20261008_133659) — Bằng chứng 0/27 ô, job E 0/4
- **KHÔNG có bằng chứng trục này tách tín hiệu.** 08-22: **0/27 ô** qua BH FDR 10% (radar: 0/24 —
  hai trục HOÀ). Chính báo cáo gốc §7 viết **"KHÔNG wire"** và §6.3 "tốt hơn để **MÔ TẢ**, không
  phải để wire". Job E 2026-09-27 đo lại bằng thước khác (IC cross-sectional momentum/value) trên
  **12,6 năm** (IS 72 tháng / OOS 80 tháng): **0/4** — `ic_mom` đảo dấu IS +0,057 → OOS −0,038;
  `ic_ey` từ −0,082 (p_BH 0,0030, CI loại 0, đơn điệu) về +0,003 (p 0,886) = **artifact IS**.
  Không phải lỗi cửa sổ ngắn: hỏng y hệt trên cửa sổ dài gấp 1,6×.

## Chuyển từ kb/canonical.md L266-289 (trim 2026-10-08, Wags_20261008_133659) — Trục khác 0/12, lý do 08-22, cách tính breadth chuẩn
- **Không trục nào khác qua được cùng chuẩn**: job E so 3 trục cùng khuôn (breadth / retail_net_share
  / DT5G state) = **0/12**. `retail_net_share` giữ được cùng dấu IS&OOS nhưng IS chỉ 9/7/5 tháng và
  **nguồn chết 28/09/2026** ⇒ không phải ứng viên thay thế.

Lý do (nguyên văn 08-22, vẫn đúng — tái lập CHÍNH XÁC 2026-09-27):
- Value Radar zone ≈ kỷ nguyên: 54% số năm bị 1 nhãn chiếm ≥90% phiên → n_effective ~2-3 chu kỳ, không bao giờ đủ sức thống kê
- Breadth-tercile PIT: **0%** năm bị 1 nhãn chiếm ≥90%; **2,0×** số episode so với radar (262 vs 131)

Cách tính breadth chuẩn — **định nghĩa đầy đủ, 3 chi tiết dưới đây từng làm tái lập lệch**:
- Nguồn: `tav2_mike.universe_pit` (CANONICAL)
- breadth_t = COUNT(Close_t > MA200_t | in_universe=True) / COUNT(in_universe=True)
  **Mẫu số chỉ đếm mã có `MA200` KHÔNG NULL.** Tính từ `data/bq_cache/ticker` mà không lọc
  `MA200 IS NOT NULL` → breadth 2016 ra **0,243 thay vì 0,730** (`bq-cache` registry, bẫy MA200 NULL
  2015-2017). Lọc đúng: corr 0,999954 với chuỗi gốc.
- Phân loại phiên t: dùng breadth_{t-1} (PIT, không look-ahead cùng phiên).
  ⚠️ **Đây KHÔNG phải biến thể sinh ra bảng §4 của báo cáo gốc** — bảng đó dùng breadth CÙNG PHIÊN
  (look-ahead corr **+0,109**, báo cáo tự thừa nhận) và §5a của chính nó cho thấy **trễ 1 phiên là
  mất tính đơn điệu**. Hai chuỗi cho số khác nhau đáng kể (ô HIGH excess **+5,5pp vs +16,6pp**, thứ
  tự tercile ĐẢO). Trích số 08-22 thì phải nói rõ biến thể nào.
- Tercile: phân vị rolling **252 phiên trước** (không phân vị toàn mẫu). Quy ước tie của bản gốc:
  `(# trong 252 phiên trước < breadth_t) / 253` — 4 quy ước hợp lý khác cho LOW 1.224-1.226 thay vì
  **1.232**. Và `pd.cut([0,1/3,2/3,1])` **ném mất `pct==0,0`** (63 phiên breadth thấp nhất lịch sử,
  tức các phiên VNI xấu nhất) ⇒ excess ô LOW tụt +27,4pp → +14,7pp. Dùng ngưỡng tường minh.


## Chuyển từ kb/canonical.md L292-294 (trim 2026-10-08, Wags_20261008_133659) — Nguồn quyết định + tái kiểm
Kết quả dẫn tới quyết định: breadth-vs-radar-matrix-20260822 (Taylor, B2) + user confirm 2026-08-22.
Tái kiểm + ranh giới hiệu lực: `agents/Taylor/research/breadth_tercile_recheck_20260927/report.md`
(bus `finding:breadth-tercile-08-22-recheck`, verdict **A — quy ước ĐỨNG, không đổi trục**).

