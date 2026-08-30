# Insider CLUSTER BUY scoping — job Taylor_20260830_054316

**Ngày:** 2026-08-30 · **Tác giả:** Taylor · **Trạng thái:** SCOPING xong, kết luận **NO-GO**.

**Bối cảnh:** user duyệt scoping tín hiệu dương đối xứng với `insider_flags.py` (WATCH-only,
nội bộ bán ròng ≥1% CP lưu hành/90d). Ý tưởng: đảo dấu thành "cluster buy" — nội bộ mua ròng
cụm, đặc biệt trong episode `dd52 ≤ -20%` — để hỗ trợ phễu candidate cho sleeve margin đơn mã
discretionary (case DGC/TV1-style: "công ty bị bán tháo nhưng nội bộ tin tưởng mua vào").

## Dữ liệu & phương pháp

Tái dùng panel PIT đã dựng cho gate bán ròng gốc (job `Taylor_20260729_015830`,
`exp_insider/panel2.sql` → `panel2.csv`, 49.059 dòng ticker-tháng, 2015-06→2026-07, universe =
`universe_pit`, cửa sổ 90/180 ngày). Panel đã có sẵn cột phía MUA (`nbuy_90`, `nbuy_90_nb` —
khử ESOP-bulk theo cùng logic `is_bulk` gốc, `buy_sh_90_nb`, `oshares`) — **không chạy BQ mới**.
Tự tính thêm `dd52 = Close / rolling12m_max(Close) - 1` từ chính panel (tháng, ~12 điểm/năm).

**4 định nghĩa cluster-buy, pre-register TRƯỚC khi nhìn IC/spread** (script:
`exp_insider/cluster_buy_scoping.py`):
- **A** `nbuy_90 > nsell_90` — đối xứng thuần với gate bán gốc (`nsell_90 > nbuy_90`)
- **B** `nbuy_90_nb >= 2` — cụm ≥2 người khác nhau (đã khử ESOP-bulk)
- **C** `buy_sh_90_nb / OShares >= 0,5%` — theo tỷ lệ CP lưu hành, mirror ngưỡng 0,5% phía bán
- **D** `B AND (nbuy_90_nb > nsell_90_nb)` — cụm + net-buy đồng thời (mạnh nhất về mặt lọc)

Kiểm 2 chiều: IC rank-corr tháng (ctrl `ey`+`rating8l`, cùng khung `gate_analysis.py` gốc) +
spread demeaned (`xs20`/`xs60`) trên toàn universe VÀ trên subset `dd52 ≤ -20%` (đúng mạch
fear-buy sleeve mà đề xuất nhắm tới).

## Kết quả

**Coverage** (đủ lớn để test, không phải vấn đề): A=12,4%/45,2 mã-tháng, B=5,6%/20,5,
C=8,4%/30,8, D=4,8%/17,5. Quy đổi D ra quý: trung vị **27 mã/quý**, min 14 — coverage KHÔNG
phải lý do loại (đủ dày, ngược lại với lo ngại ban đầu "quá hiếm <1/quý").

**IC toàn universe**: yếu, phần lớn không có ý nghĩa (`|t| < 2`), và **C có dấu NGƯỢC kỳ
vọng** (`t=-1,96` fwd20, `t=-3,22` fwd60 — mua nhiều theo %CP dự báo return THẤP hơn, không
phải cao hơn).

**Spread toàn universe**: không định nghĩa nào có `|t| > 1,2` — không phân biệt được với 0.

**Spread trong subset `dd52 ≤ -20%` (chính là use-case sleeve nhắm tới) — ĐÂY LÀ KẾT QUẢ
QUYẾT ĐỊNH**: cả 4 định nghĩa đều cho spread **ÂM và có ý nghĩa thống kê**, mạnh nhất ở fwd60:

| Định nghĩa | fwd20 t | fwd60 t | fwd60 delta |
|---|---:|---:|---:|
| A (net) | -1,69 | **-3,60** | -1,57pp |
| B (cụm≥2) | -2,82 | **-4,27** | -2,75pp |
| C (%OSH) | -2,07 | -2,63 | -1,62pp |
| D (cụm+net) | -2,49 | **-4,73** | -2,90pp |

Tức là: **mã đang trong episode giảm ≥20% từ đỉnh 52 tuần MÀ nội bộ cụm mua ròng thì return
60 ngày kế tiếp còn TỆ HƠN mã không có cờ này**, không phải tốt hơn — ngược hoàn toàn với giả
thuyết ban đầu (n=884-2229 trong subset, không phải mẫu nhỏ vô nghĩa).

**Ổn định IS/OOS**: B và D flip dấu (IS dương +0,0066/+0,0050 → OOS âm -0,0031/-0,0028) — dấu
hiệu overfit/không bền, cộng thêm với kết quả âm trong subset mục tiêu.

**Overlap với gate bán ròng cũ**: thấp (A/D gần như rời nhau với gate_sell — đúng logic vì
định nghĩa loại trừ lẫn nhau ở numerator nbuy>nsell vs nsell>nbuy), không phải vấn đề trùng lặp.

## Diễn giải (không đoán, bám vào bằng chứng)

Không đủ dữ liệu để khẳng định CƠ CHẾ (không có field chức vụ, không phân biệt được "mua vì
tin tưởng" vs "mua để cứu giá/nghĩa vụ ESOP/ràng buộc call margin cá nhân"), nhưng bằng chứng
tail cho thấy: nội bộ mua ròng trong lúc giá đã giảm sâu ở VN **KHÔNG phải smart-money signal
đáng tin** — hợp lý với giả thuyết thay thế "nội bộ cũng đánh giá sai đáy" hoặc "mua để đỡ giá
trong khi nguyên nhân giảm là thật" — nhưng đây là suy đoán, không phải kết luận đã kiểm chứng
từ dữ liệu này.

## Kết luận: NO-GO

**Không đầu tư xây writer/reader đầy đủ** (`insider_cluster_flags.py` + reader phễu candidate)
cho cluster-buy. Lý do xếp theo trọng số: (1) spread ÂM có ý nghĩa đúng trong subset mục tiêu
`dd52≤-20%` — tín hiệu không chỉ yếu mà **sai chiều** ở chính use-case cần dùng; (2) IS/OOS
không ổn định cho 2/4 định nghĩa; (3) coverage đủ nên không phải lý do loại — false lead ban
đầu (nếu bỏ qua bước IS/OOS + subset test và chỉ nhìn coverage, sẽ kết luận nhầm GO).

Việc kết thúc ở đây — không dispatch quant-skeptic (không có gì để xác nhận, kết luận đã là
NO-GO từ chính dữ liệu pre-register). custom_basket.py/production không đụng, đúng phạm vi
dispatch.
