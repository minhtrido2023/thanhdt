---
kind: group-index
group: research-caches
title: Research caches lớn (KHÔNG production — đừng nhầm là sống)
---

# Research caches lớn (KHÔNG production — đừng nhầm là sống)

| Nguồn (file) | Status |
|---|---|
| [`ba_v11_unified_sig.md`](ba_v11_unified_sig.md) — data/ba_v11_unified_12y_sig.pkl | RESEARCH |
| [`edge_panel_csv.md`](edge_panel_csv.md) — data/edge_panel.csv (panel THÁNG signal+forward, IC/edge-health) | DERIVED — research-only nhưng **refresh DAILY 15:30 ICT** |
| [`static_panels.md`](static_panels.md) — data/fa_ratings_lh.csv (05-15), data/intraday_full.pkl (05-17), data/value_panel_2014.csv (pinned PIT) | RESEARCH |
| [`vnindex_csv.md`](vnindex_csv.md) — data/VNINDEX.csv | RESEARCH |

⚠️ Tiêu đề nhóm ("đừng nhầm là sống") đúng cho 3 nguồn tĩnh, **KHÔNG đúng cho `edge_panel.csv`** —
nguồn này được `papertrade_daily.sh` step [22] ghi lại mỗi phiên T2-T6. Nó nằm ở nhóm này vì
mục đích dùng là nghiên cứu, không phải vì nó đông cứng.

↩ [Về index tổng](../index.md)
