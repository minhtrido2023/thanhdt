# MANIFEST — 8L update package (since 2026-06-02)

Sinh ngày 2026-06-11. Chỉ gồm phần thay đổi kể từ bản 02/06. Không chứa secret (telegram_config.json).

## code/ — đặt vào thư mục gốc 8L (WORKDIR_8L), ghi đè bản cũ
```
oil_transmission.py        MỚI  — L7 chuỗi dầu khí (cần data/oil_transmission_map.csv)
freight_map.py             MỚI  — cước vận tải biển (cần data/freight_*.csv, bdi_daily_real.csv)
vn30_8l.py                 MỚI  — rổ 8L-VN30 (liq≥10B top-30 EW) → data/vn30_8l.csv
bot_8l_commands.py         MỚI  — lệnh bot top-N / new / vn30 (lớp render)
moat_5f.py                 SỬA  — moat 5F gate (cần data/moat_tags.csv)
rank_8l.py                 SỬA  — tích hợp moat 5F
dna_card.py                SỬA  — tích hợp moat 5F + map dầu/cước
cyclical_structural.py     SỬA  — neo Brent (cần data/brent_monthly.csv)
rating_8l.py               SỬA  — rating 1–5
power_lens.py              SỬA  — lăng kính POWER
unified_screener.py        SỬA  — hợp nhất map mới + merge rating
```

## data/ — đặt vào WORKDIR_8L/data/ (input cấu trúc/tag tay, code mới cần)
```
oil_transmission_map.csv         map ngành→kênh truyền dẫn dầu
freight_map.csv                  map mã→nhóm cước
freight_rates_quarterly.csv      chuỗi cước theo quý
bdi_daily_real.csv               Baltic Dry Index ngày
brent_monthly.csv                neo giá Brent tháng
moat_tags.csv                    registry moat 5F (tag tay)
```
> Các CSV/MD OUTPUT (rank_8l.csv, unified_screener.csv, dna_cards.csv, vn30_8l.csv, rating_8l*.csv...) KHÔNG kèm — pipeline tự sinh mỗi phiên.

## reference/
```
pt_8l_daily.bat            orchestrator Windows (tham khảo thứ tự + 2 bước mới); server Linux tự viết runner
```

Xem CHANGELOG.md để biết mô tả thay đổi + phụ thuộc ngoài gói (BQ, DT5G, env, Telegram glue).
