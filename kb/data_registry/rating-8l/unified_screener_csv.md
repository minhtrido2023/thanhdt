---
kind: script-output
status: CANONICAL
source: data/unified_screener.csv
group: rating-8l
note: OUTPUT tự sinh, KHÔNG phải nguồn dữ liệu ngoài
writer: unified_screener.py (dòng 433)
---

# data/unified_screener.csv

**Status: CANONICAL (self-generated output, not an external input)**

## Là gì
Screener hợp nhất — router gán mỗi ticker vào đúng khung định giá (BANK → NPL/coverage/CAR gate
+ PB-vs-ROE; CYCLICAL → commodity-trough + dislocation; COMPOUNDER → PEG/pe_z/pb_z + value-trap
guard) rồi trả về verdict + action chuẩn hoá. Output của `unified_screener.py`.

## Ai ghi / cadence
`unified_screener.py`. Input reuse: `data/bank_lens_v3.csv` (banks), `data/{rubber,iron_ore,
urea,dap,caustic_soda}_monthly.csv` (commodity regime), BQ `ticker` (compounder/cyclical
valuation), `fa_ratings_lh` (quality gate). Cadence theo pipeline 8L, không cron riêng.

## Ai đọc
`rank_8l.py` (input chính, cùng `engine_class.csv`), `bot_8l_commands.py`, `telegram_8l_bot.py`,
`dna_report.py`, `dna_card.py`, `rank_8l_daily_alert.py`.

## Bẫy
Route BANK phụ thuộc `bank_lens_v3.csv` — nếu bank lens đang BLOCKED-STALE/PARTIAL (xem
`bank_lens_v3.md`), route BANK trong file này thiếu differentiator NPL/CAR/coverage, không phải
lỗi của `unified_screener.py` — kiểm nguồn trước khi nghi ngờ script này.
