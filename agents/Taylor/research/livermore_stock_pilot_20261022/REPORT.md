# REPORT — Thí điểm Livermore đọc kỹ thuật cổ phiếu BAL/LAG (2026-10-22)

**NHÃN theo tiêu chí khoá: NO-GO** (b thất bại). Nhưng (a) đạt rõ và LR test có ý nghĩa ⇒ đây là NO-GO sát biên, không phải "không có tín hiệu".
PREREG md5 `018bd32318c573a0f4919fb6a2f88991` (kiểm đầu & cuối job: khớp). `reads.csv` md5 `807c670a7ba0693c7f435f296753a1ad`, ghi vào `reads_md5.lock.log` (17:59 ICT) TRƯỚC khi join outcome (`score.py` assert md5 khớp). Số liệu: `score_stdout.txt`.

## Mẫu & vận hành
- N=300 đủ (G_VOL=True 150 / False 150; mỗi tầng 100 LAG + 50 BAL), 227 mã, seed 20261022, 46 quý. Dương tính HIT15 = 83 (True 58, False 25) ⇒ base 27,7% (do phân tầng, không phải base tự nhiên).
- Loại: 41 ứng viên vì nhảy giá >30% (close-close hoặc open/close-trước) / NaN / median volume 0 trong cửa sổ (corp-action chưa chỉnh); 9 vì luật ≤3 sự kiện/mã hoặc giãn cách <40 phiên. 5.377 sự kiện ≥2015-03-01, 5.372 đủ ≥250 phiên trước.
- Nguồn giá: `tav2_bq.ticker` Open/High/Low/Close(adj)/Volume qua cache `data/bq_cache` (cùng nguồn `lag_events.py`). Rò rỉ: 0 chữ cái trong khối dữ liệu; không mã/ngày/book/tầng trong prompt.
- 300 lần gọi `claude -p --model opus --tools "" --setting-sources ""` (cwd /tmp, 6 song song), 0 lỗi kỹ thuật, không chạy lại, không đổi prompt. `system_prompt.txt` = rút từ `livermore.md` (bỏ công cụ/registry/khuôn VNINDEX) + `question.txt`. 
- Độ nhiễm: 0 case khai mã cụ thể (299 NONE; 1 nêu "gợi nhớ cú sốc VN 4/2025" nhưng không xác định mã) ⇒ kết quả loại nhiễm = y hệt.
- Lưu ý dữ liệu: nhiều case thanh khoản rất mỏng (Volume 0 nhiều phiên) — thực tế của sample, không lọc thêm (PREREG không cho).

## Kết quả (CI95 bootstrap cụm theo quý vào lệnh, 5.000 lần)
| Chỉ số | Giá trị | CI95 |
|---|---|---|
| (1) AUC trong-tầng gộp (trọng số = số dương mỗi tầng) | **0,6286** (True 0,6485; False 0,5822) | [0,5497; 0,7063] |
| (1) loại case nhiễm | 0,6286 | [0,5439; 0,7063] |
| (2) B1 cơ học VOL60+RUN20+DIST52, AUC CV 5-fold | 0,6161 | — |
| (2) + logit(P_HIT15), AUC CV | 0,6401 | — |
| (2) **ΔAUC** | **+0,0240** | [−0,0182; +0,0607] |
| (2) LR test (1 bậc tự do) | LR=6,39, p=0,0115 | — |
| (3) B2 cờ G_VOL AUC / Livermore AUC thô | 0,6374 / 0,6887 | — |
| (4) P_POS AUC | 0,5500 | [0,4614; 0,6410] |
| (4) Brier Livermore vs B0 | 0,2534 vs 0,2495 (Livermore tệ hơn 0,004) | Δ [−0,0256; +0,0087] |

Phụ: AUC thô theo book: LAG 0,727, BAL 0,659 (phần lớn là G_VOL: P_HIT15 TB 0,483 ở tầng True vs 0,296 ở False). RISK=HIGH (212/300) có HIT 33,0%, MED 14,8% (81), LOW 14,3% (7) — bucket thô, ít LOW.

## Tiêu chí
- (a) AUC≥0,58 & CI loại trừ 0,5: **ĐẠT** (0,629; CI dưới 0,550).
- (b) ΔAUC>0 & CI loại trừ 0: **HỤT** (CI [−0,018; +0,061] chứa 0), dù LR test p=0,012 (LR dùng toàn mẫu không cụm-quý nên lạc quan hơn bootstrap cụm).
- (c) giữ dấu khi loại nhiễm: đạt (không có case nhiễm để loại).
- ⇒ **NO-GO** theo luật khoá ("(a) hoặc (b) hụt"). Nhánh INCONCLUSIVE của PREREG không thể xảy ra khi (b) hụt nên không dùng được; nhận xét của tôi, ngoài luật: bằng chứng nghiêng về "Livermore có thêm một chút thông tin ngoài VOL60/RUN20/DIST52 nhưng chưa chứng minh được ở N=300" — ΔAUC điểm +0,024 với CI rộng ±0,04. KHÔNG tự mở rộng mẫu (PREREG cấm); nếu user muốn thử tiếp phải là PREREG mới.
- P_POS không có tín hiệu (AUC 0,55 CI chứa 0,5; Brier không tốt hơn base).

## Hành động
Không wire, không cảnh báo hiển thị, không sizing. Không gọi quant-skeptic (NO-GO). Kết quả không suy ra cho VNINDEX.
