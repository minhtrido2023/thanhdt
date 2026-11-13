# Brief A6 (job Taylor_20261113_075112, dispatch từ Mike) — ⚠️ PAPER
Nối A5 + recommended_reruns của skeptic A5 (`mike/logs/verify_20261113_073356_1145932.log`). KHÔNG đổi production / trading_rules.json / neo; KHÔNG merge.
1. Đưa `IDLE_CARRY_TIER` lên 1 nhánh từ main; pin0% (mặc định off) trùng byte 80f509ec, pin1M trùng e2de0ac4; selfcheck quét rộng 3 TZ.
2. Small-NAV: NAV_TOTAL_B=1,2 · L1 (LIQ off) vs L3P (lag+pit) · park 0 · pin0% — chênh DD5 ~4pp còn không khi trần ADV không ràng buộc.
3. DD5 theo dải: L∈{10,21,42} × ≥5 seed cho 4707bcbe, 80f509ec, dc8910f8.
4. ADV thấp giả sau tách/thưởng: theo từng (mã, ngày) mua LAG.
