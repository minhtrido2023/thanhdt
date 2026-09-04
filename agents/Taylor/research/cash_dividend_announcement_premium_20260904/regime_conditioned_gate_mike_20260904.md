# Regime-conditioned dividend pre-ex gate — phân tích tương tác Mike 2026-09-04

> Tiếp nối proxy sprint Taylor_20260904_094347 (NO-GO trên so sánh gộp CASH vs STOCK).
> User hypothesis: hiệu ứng cổ tức tiền mặt chỉ rõ trong bear/crisis/neutral, mất trong bull/mania.
> Phân tích interactive bởi Mike, dữ liệu: cash_events_analyzed.csv + DT5G production states (BQ)
> + deposit_rate_vn.py PIT (26 mốc). CHƯA prereg — mọi con số dưới đây là EXPLORATORY.

## Kết quả chính — gradient regime ĐƠN ĐIỆU (mẫu sạch giá>=10k, yield<=50%, 2014-2026, N=5.237)

AR = pre-ex[−14,−1] − baseline[−28,−15] − VNINDEX, regime đo tại ex−14d (PIT).

| Regime (excess>0 & prior_3y>=3) | N | ticker | median AR | hit | p |
|---|---|---|---|---|---|
| NEUTRAL | 107 | 93 | +2,33% | 64% | 0,0011 |
| BEAR | 332 | 210 | +1,59% | 57% | 0,0032 |
| BULL | 819 | 326 | +0,42% | 53% | 0,114 (ns) |
| EXBULL | 280 | 182 | **−1,80%** | 43% | 0,0087 (ÂM) |

EXBULL đảo dấu: trong mania, cổ phiếu yield cao TỤT so với baseline trước ex-date (value drag).
STOCK_DIV control trong EXBULL lại +1,09% → riêng chiều này CÓ cash-specific (p=0,017).

## Gate đề xuất (exploratory): regime∈{BEAR,NEUTRAL} & excess>0 & prior_3y>=3 & giá>=10k
- N=439, 244 ticker, median +2,05%, hit 58%, p=3,6e-05; cluster-robust +1,75% (p=0,0006)
- Dose-response nội bộ: excess 0-4pp +1,19% → 4-8pp +2,63% → >8pp +2,66%
- Bản chặt (excess>4pp): N=153, median +2,63%, hit 62%, cluster +3,02%
- Tail: p5=−14,5%, p95=+21,5% — phân tán lớn, cần diversification

## 4 caveat PHẢI mang theo
1. **Cash-specificity KHÔNG chứng minh được trong BEAR/NEUTRAL**: STOCK_DIV cùng regime cũng drift
   (+0,68%/+2,00%, MWU p=0,24/0,43). Phần "regime mở → drift trước corp-action" là hiệu ứng CHUNG;
   phần cash-specific chỉ nằm ở dose-response excess yield + chiều âm EXBULL.
2. **Era-concentration**: 2014-2019 ≈ 0 (p=0,66), toàn bộ edge từ 2020+ (+2,55%, p=4e-06);
   riêng 2022 chiếm N=48/153 bản chặt với median +8,4%. LOYO bỏ 2022 → +1,13% (còn dương nhưng nửa).
   Mức lãi suất tuyệt đối KHÔNG giải thích được split này (dương ở mọi bucket rate khi đã gate).
3. Per-year trong gate vẫn có năm âm: 2016 −0,53%, 2018 −3,34%, 2020 −0,69%.
4. Chuỗi deposit rate là CANONICAL-PROXY neo hồi tố (caveat b registry) — backtest mang hindsight nhẹ.

## DGC 2026-09 qua gate?
excess +11,8pp ✓, prior đều ✓, giá 43k ✓ — nhưng DT5G hôm nay = BULL → gate ĐÓNG.
(DGC +8% là announcement-day jump, khác cửa sổ pre-ex mà gate này đo.)

## Trạng thái
EXPLORATORY — chưa prereg, chưa quant-skeptic. Nếu muốn tiến: Taylor formal prereg (freeze đúng
luật trên, không tune thêm) → quant-skeptic → mới bàn wire (dạng lens duyệt plan, không auto-trade).
