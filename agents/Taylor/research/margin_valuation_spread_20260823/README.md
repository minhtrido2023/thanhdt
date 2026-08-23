# margin_valuation_spread_20260823 — Phase 0 artifacts

Job `Taylor_20260823_075808`. Bằng chứng MÔ TẢ cho mandate "margin theo khoảng cách định giá".
**Không có backtest chiến lược nào ở đây** — chỉ chuỗi point-in-time + forward return VNINDEX.
Plan Phase 1 pre-registered: `../../plan_margin_valuation_spread_20260823.md`.

| File | Nội dung |
|---|---|
| `q_monthly.sql` / `_raw_monthly.csv` | 244 tháng (2006-2026): EY/DY của universe_pit (median, cap-weighted, payers-only), n_uni, top1 weight |
| `q_breadth.sql` / `_breadth_monthly.csv` | đếm số mã vượt từng ngưỡng DY/EY theo tháng (dựng breadth) |
| `_vnindex_daily.csv`, `_dt5g_daily.csv` | VNINDEX daily (dd52 + forward return), DT5G state daily (`vnindex_5state_dt5g_live`) |
| **`monthly_spread_series.csv`** | **chuỗi chính A1**: EY/DY + deposit + margin(giả định) + 6 định nghĩa spread + dd52 + DT5G state + fwd 6/12/24m + breadth |
| `episodes.csv` | A2 — episode theo 5 luật thô ban đầu |
| `episodes_absolute_sp0.csv` | 4 episode `DY(median payer) >= deposit` (trả lời trực tiếp câu hỏi user) |
| `episodes_absolute_ey_margin.csv` | 9 episode `EY(median) >= margin_rate` |
| `episodes_pit_top_quintile.csv` vs `episodes_fullsample_top_quintile.csv` | bằng chứng ngưỡng PERCENTILE thất bại khi ép point-in-time (net12 median −6,9pp / 38% dương) vs đẹp giả khi dùng full-sample |
| `analyze_spread{,2,3,4}.py` | script tái lập (chạy bằng `$DNA_PYEXE`, theo thứ tự 1→4) |

## 3 caveat phải mang theo khi trích bất kỳ số nào ở đây
1. `deposit_rate_vn.py` gồm 26 mốc **neo hồi tố cùng 1 lần 2026-06-19** ⇒ không point-in-time thật.
2. `margin_rate = deposit + 5,0pp` là **GIẢ ĐỊNH** (neo vào 12,5% thật của SpaceX vs deposit 6,8%);
   không tìm được chuỗi lãi margin CTCK lịch sử.
3. 2008-01→2010-12 deposit là **proxy** = SBV refi + 0,50pp (cột `deposit_src`).
