---
kind: proposal
status: PROPOSED — chờ Mike duyệt (coding_guidelines §13, KHÔNG tự sửa file kb/ chuẩn tắc)
job: Taylor_20260906_015330 (Phase 0b, việc V3)
target_file: .claude/skills/quant-research/SKILL.md (bước 4 "Declare N honestly") hoặc
             mike/kb/coding_guidelines.md §18 (dẫn tới skill trên) — Mike chọn vị trí phù hợp
---

# Đề xuất: cluster-robust p-value mặc định khi N khai báo là panel (ticker, quý)

## Dòng đề xuất chèn (bước 4 skill quant-research, ngay sau đoạn "N=14 events, sign test...")

> **Panel (ticker, quý) với >1 quý/ticker: báo CẢ HAI p-value, không chỉ row-level.** Nếu N khai
> báo là số dòng ticker-quý (ví dụ 14.884) nhưng số ticker ĐỘC LẬP nhỏ hơn nhiều (ví dụ 733), BH-p
> tính trên dòng có thể phóng đại độ tin cậy vài bậc độ lớn. Bắt buộc thêm **block bootstrap theo
> ticker** (resample N_ticker ticker có hoàn lại, mỗi ticker được rút mang theo TOÀN BỘ dòng quý
> của nó, B≥1000, lấy SE/CI của thống kê từ phân phối bootstrap) làm p-value cluster-robust chính
> thức — báo cạnh p-value row-level, không thay thế. **Không dùng phương án "1 dòng ngẫu nhiên mỗi
> ticker" làm chuẩn cluster-robust** — cách đó không sửa lỗi cluster mà chỉ bỏ ~95% dữ liệu, làm
> mất power một cách giả tạo và có thể cho kết luận "không còn ý nghĩa" trong khi hiệu ứng vẫn thật
> (chỉ là test yếu đi vì thiếu dữ liệu, không phải vì hiệu ứng biến mất).

## Vì sao (bằng chứng cụ thể, Phase 0b T1 accruals, 2026-09-06)

Trục T1 (`accr_q` dự báo `persist_2q`, N=14.884 dòng ticker-quý, 733 ticker độc lập):
- Row-level (như Phase 0 báo cáo gốc): AUC=0.4729, p_BH=1,4e-07.
- Block bootstrap theo ticker (B=2000, giữ nguyên toàn bộ dữ liệu, chỉ sửa cách tính SE):
  AUC=0.4729 (không đổi), boot-SE=0,0058, 95%CI=[0,4616; 0,4845] (không chứa 0,5), p≈3,5e-06 —
  **vẫn có ý nghĩa mạnh**, kết luận không đổi.
- "1 dòng ngẫu nhiên/ticker" (N=733 lặp lại 1000 lần Monte Carlo): AUC trung vị 0,4783, **p trung
  vị=0,31, chỉ 13,5% lần rút có p<0,05** — nếu dùng cách này làm "cluster-robust chuẩn" sẽ kết
  luận SAI là hiệu ứng yếu/không ổn định, trong khi đó chỉ là hệ quả bỏ 95% dữ liệu, không phải
  bằng chứng hiệu ứng không thật.

Hai phương pháp cùng tên "cluster-robust" cho hai câu trả lời đối lập nhau ở cùng 1 bộ dữ liệu —
đây chính là lý do cần khoá PHƯƠNG PHÁP cụ thể (block bootstrap, không phải subsample) làm chuẩn,
không để mỗi sprint tự chọn cách diễn giải "N=733" theo ý mình.

## Phạm vi áp dụng
Mọi Phase-0/backtest tương lai có panel dạng (ticker, thời điểm) với nhiều quan sát lặp lại trên
cùng 1 ticker và N_ticker < N_dòng đáng kể (ví dụ >2× chênh lệch).
