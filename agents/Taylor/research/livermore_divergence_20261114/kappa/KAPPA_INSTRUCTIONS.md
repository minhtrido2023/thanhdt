# Gói κ lặp lại — hướng dẫn cho Mike (P0 (i), cổng G0)

Taylor dựng gói, **KHÔNG chạy Livermore**. Mike chạy Livermore (agent native `livermore`, Opus ghim) 3 lần độc lập.

## Nội dung
| File | Ý nghĩa |
|---|---|
| `cases/K01..K20.csv` | 20 case ẩn danh: 250 phiên `open,high,low,close` (÷ close phiên đầu ×100) + `vol_rel` (÷ trung vị cửa sổ). Không mã, không ngày, không nói chuỗi nào là chỉ số. md5 từng file: `cases.md5` |
| `SEALED_truth.json` (+ `.md5`) | Kết cục H20 + mã + ngày. **KHÔNG đưa cho Livermore, KHÔNG trích vào prompt** |
| `build_cases.py` | Tái lập case (seed 20261114, chọn bằng seed từ `universe_pit` U2 + VNINDEX, không chọn tay) |
| `run{1,2,3}_order.txt` | Thứ tự đọc khác nhau cho từng lần (seed 20261115..17) — chống hiệu ứng thứ tự |
| `kappa_score.py` | Chấm: Fleiss κ, Cohen từng cặp, sd của p, tỉ lệ abstain theo luật ensemble (e). `--selftest` đã PASS |
| `runs/` | Mike ghi `run1.csv`, `run2.csv`, `run3.csv` vào đây |

Thành phần: 15 cổ phiếu (U2: `in_universe` ∧ MDV60 thực ≥ 20 tỷ) + 5 mốc VNINDEX, as-of 2014-01 → 2025-09-30, ≤1 case/mã,
không trùng ±60 ngày với 100 case battery 05/11, cửa sổ không có phiên |ret| > 16% và không quá 20% phiên vol = 0.

## Cách chạy (bắt buộc đúng để κ có nghĩa)
1. **Cách ly file**: mỗi lần r, chép CHỈ thư mục case ra chỗ tạm, ví dụ
   `d=$(mktemp -d /tmp/lvr_kappa_r$r.XXXX); cp cases/*.csv "$d"/` — rồi đưa Livermore đường dẫn `$d`. Livermore có
   Bash/Read: nếu trỏ vào thư mục gói thì nó **có thể thấy `SEALED_truth.json`** ⇒ hỏng phép thử. Không trỏ vào repo.
2. **3 lần = 3 lệnh `Agent(subagent_type="livermore")` MỚI**, không `SendMessage` nối tiếp, không nhắc kết quả lần trước,
   không cho biết đây là thử lặp lại (để tránh nó cố "nhất quán" một cách giả tạo).
3. Prompt cố định cả 3 lần (chỉ thay `<DIR>` và `<ORDER>` = nội dung `run{r}_order.txt`):

```text
Bài thử đọc kỹ thuật mù. Thư mục <DIR> có 20 file K01..K20.csv: mỗi file là 250 phiên giao dịch liên tiếp của một
chuỗi giá trên thị trường chứng khoán Việt Nam (cổ phiếu hoặc chỉ số), đã chuẩn hoá: open/high/low/close chia cho close
phiên đầu ×100, vol_rel = khối lượng chia trung vị khối lượng của cửa sổ. Không có mã, không có ngày.
Chỉ đọc các file trong <DIR>; KHÔNG mở bất kỳ file nào khác, KHÔNG tra web về chuỗi.
Đọc theo đúng thứ tự: <ORDER>.
Với MỖI case, dựa trên cấu trúc giá + khối lượng, trả:
- H20_DIR: UP nếu bạn cho rằng close của phiên thứ 20 SAU phiên cuối cùng sẽ CAO hơn close phiên cuối, ngược lại DOWN.
- H20_P_UP: xác suất (0–1, 2 chữ số) close +20 phiên cao hơn close phiên cuối. Phải nhất quán với H20_DIR (>0,5 ⇔ UP).
- RECOGNIZED: true nếu bạn nghĩ đã nhận ra mã hoặc giai đoạn cụ thể, ngược lại false.
Cuối cùng in ĐÚNG một khối CSV, 21 dòng, header: label,H20_DIR,H20_P_UP,RECOGNIZED
```
4. Lưu khối CSV của lần r nguyên văn vào `runs/run{r}.csv` (không sửa tay; nếu thiếu/thừa nhãn ⇒ chạy lại đúng lần đó
   và ghi chú lý do trong `runs/NOTES.md`).
5. Chấm: `cd` vào thư mục này, `/home/trido/thanhdt/wc_venv/bin/python kappa_score.py` (chưa mở truth) → `kappa_result.json`.
   Quyết G0 TRÊN SỐ NÀY. Sau đó mới `--unseal` để có hit/Brier mô tả (N=20 — không kết luận năng lực từ đây).

## Đọc kết quả (cổng G0, kế hoạch §8)
- **Fleiss κ(H20_DIR) < 0,4** (hoặc NaN vì cả 3 lần gọi một phía cho mọi case) ⇒ đầu ra là nhiễu lấy mẫu của LLM:
  P2 BẮT BUỘC dùng ensemble (e) 3 lần đọc/case (user đã duyệt chi phí ×3 cho P2 — tin nhắn duyệt 14/11 13:35), hoặc dừng.
- `ensemble_e_abstain_rate > 0,70` ⇒ cảnh báo trước: vai dự báo không dùng được trong thực hành dù có κ.
- `per_case_sd_p_mean` cho biết độ rung của xác suất giữa các lần (tham chiếu: sd p TOÀN mẫu battery 05/11 = 0,051).
- Sai số lấy mẫu của κ với 20 case × 3 lần là lớn (`ước lượng` SE ~0,15); κ trong [0,3; 0,5] ⇒ coi là "không chắc",
  nghiêng về luật bảo thủ (dùng ensemble).
- Taylor KHÔNG chạy Livermore và KHÔNG mở truth trước khi Mike nộp 3 file run.
