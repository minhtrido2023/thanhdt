# A3 — Replay luật D1 "LAG đòi skeptic_final = CONFIRMED" (chỉ đọc)

**Kết luận: luật D1 chặn THÊM 0 lệnh / 0 mã trong toàn bộ lịch sử plan.** Cổng hiện tại đã chặn cả 33/33 lệnh MUA LAG còn lại khi replay (0 lệnh qua cổng (a)) ⇒ hệ quả tiền thật lịch sử của D1 = 0 đ (counterfactual; chưa tính `deferred_orders`, xem ghi chú).

> ⚠️ CAVEAT: nhãn `skeptic_final` của entry mới nhất trong sổ là **BACKFILL 22/11** (`rule_backfill_20261122` / `ambiguous_backfill`), xấp xỉ, KHÔNG phải verdict gốc. Với kết quả 0 chặn-thêm, caveat này không đổi kết luận (không lệnh nào qua cổng (a) để mà nhãn quyết định).

## 1. Cổng hiện tại (tóm tắt)
- `trading_bot/plan.py:1190` `filter_lag_dd_zone_orders`, gọi ở `bot_execute.py:611` (sau `filter_dd_flag_orders`, trước `net_offsetting_orders`). Chỉ lệnh `buy` book `LAG`; FAIL-CLOSED.
- Giữ lệnh CHỈ KHI: có entry sổ DD với `dd_date ≤ plan_date` (bản mới nhất thắng); khoá `assumptions_md5` khớp; chưa hết hạn (`expiry_of`/`expires_on`); không có sự kiện quyền điều chỉnh giá sau `dd_date` (`frame_check`) / kiểm được corp-action; tâm > 0; và `min(ref_price, hard_no_chase_ceiling) ≤ min(center, zone_high)`. Lệnh được giữ bị ép trần cứng = tâm.
- Luật lặp ở prompt: `mike/bin/bq_freshness_check.sh:970` (`LAG_ZONE_NOTE`, kèm "chưa quá expires_on"). Cổng tắt bằng `LAG_DD_ZONE_GATE_ENABLED`. Không có điều kiện `skeptic_final` nào ở cổng hiện tại.
- (a) trong replay = bản sao đúng các điều kiện trên (dùng `latest_entries/lock_mismatch/expiry_of/corp_events/frame_check` của `dd_price_zone_watch.py`); `PACK_STALE` không thuộc hàm này nên không mô phỏng.

## 2. Bảng lệnh MUA LAG (orders + cancelled_orders), 33 dòng / 33 cặp (plan_date, account, ticker)
Cả hai tài khoản; `cancelled_orders` không tồn tại trong plan nào (0 dòng). Chi tiết từng dòng: `out_unsetTZ.txt`.

| Nhóm | Dòng | Plan có approved_by | (a) cổng nay | (b) CONFIRMED | Chặn THÊM |
|---|---|---|---|---|---|
| 27/07–10/08 (trước luật 09/11, chưa có DD) | 12 | Y | chặn (chưa có DD) | chặn (NO_DD) | 0 |
| 26–29/10 (chưa có DD) | 13 | Y | chặn (chưa có DD) | chặn | 0 |
| 09/11 BSR/CSV/GAS/MSB × 2 acct (plan CHƯA duyệt: `approved_by` trống) | 8 | N | chặn (giá > tâm) | chặn (FIXED_UNVERIFIED) | 0 |
| Từ 10/11 tới nay | **0** | – | – | – | 0 |
| **Tổng** | **33** | | **qua 0** | **qua 0** | **0** |

Số nền (kiểm lại): ngày plan có lệnh MUA LAG từ 10/2026 = 26, 27, 28, 29/10 và 09/11; **0 dòng** với plan_date ≥ 10/11 ⇒ khớp kế hoạch. Có thêm lệnh tháng 7–8/2026 (12 dòng) mà kế hoạch không nhắc.
Danh sách chặn-thêm từng lệnh: **trống**.

Ghi chú: 09/11 là ngày luật ra; DD các mã này ghi cùng ngày, giá > tâm nên (a) đã chặn. 12 dòng tháng 7–8 + 13 dòng tháng 10 bị (a) chặn chỉ vì replay áp cổng ngược thời gian (cổng chưa tồn tại lúc đó); đó là counterfactual, không phải lệnh thật bị chặn. `deferred_orders` (27 dòng buy LAG) KHÔNG nằm trong phạm vi spec nên không replay.

## 3. Sổ hôm nay (36 mã, bản master)
- skeptic_final rev cuối: **CONFIRMED 15 · FIXED_UNVERIFIED 21 · REFUTED_OPEN 0 · NONE 0**.
- Mã CONFIRMED mà basis = `ambiguous_backfill`: **không có**. Mã mang `ambiguous_backfill`: HHS, MSB, PAT, PNJ, QTP, SCL, SZL (cả 7 đều FIXED_UNVERIFIED).
- Bảng đầy đủ mã × rev × path × cờ: `out_unsetTZ.txt` mục 2. Hàm ý: nếu D1 bật hôm nay, 21/36 mã (58%) không được mua LAG kể cả khi giá ≤ tâm (số đếm, chưa phải ước lượng).

## 4. Tái lập
`python3 mike/bin/dd_lag_confirmed_replay.py` (worktree `/home/trido/thanhdt/wt-dd-a3`, sổ = bản master). `ruff check` sạch. Chạy `env -u TZ` và `TZ=Pacific/Kiritimati` → output giống hệt (trừ dòng giờ chạy), rc=0 cả hai. Output thô: `out_unsetTZ.txt`, `out_kiri.txt`.
