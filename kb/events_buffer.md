# events_buffer — episodic buffer (consolidator-managed, do not edit)
# Archive: kb_nightly.sh moves entries older than KEEP_DAYS to kb/archive/


## Consolidation 2026-07-01T02:05:02Z
- [2026-07-01T02:05:01Z] Mafee/status — bot-start: {"account": "SpaceX", "plan_date": "2026-07-01", "auto_otp": true}
- [2026-07-01T02:05:02Z] Mafee/error — bot-fail: {"account": "SpaceX", "plan_date": "2026-07-01", "elapsed_s": 0, "rc": 127, "log": "/home/trido/thanhdt/WorkingClaude/mike/logs/run_bot_SpaceX_2026-07-01.log"}
- [2026-07-01T01:45:07Z] Mike/status — preflight-2026-07-01: {"result": "GREEN", "checks": ["✅ BOT_STOP: CLEAR", "✅ Plan 2026-07-01: 23 lệnh, ~0.938B VND, state=NEUTRAL (DT5G_macro), approved=user", "✅ macro_health: HEALTHY (DT5G_macro, file 9.4h tuổi)", "✅ Gmail OAuth: có refresh_token (tự refresh khi cần)", "✅ BQ ticker_prune: lag=1d ✓"]}

## Consolidation 2026-07-01T02:28:51Z
- [2026-07-01T02:28:51Z] Mafee/status — bot-start: {"account": "SpaceX", "plan_date": "2026-07-01", "auto_otp": true}
- [2026-07-01T02:28:51Z] Mafee/error — bot-fail: {"account": "SpaceX", "plan_date": "2026-07-01", "elapsed_s": 1, "rc": 1, "log": "/home/trido/thanhdt/WorkingClaude/mike/logs/run_bot_SpaceX_2026-07-01.log"}

## Consolidation 2026-07-01T02:53:10Z
- [2026-07-01T02:30:11Z] Mafee/status — bot-start: {"account": "SpaceX", "plan_date": "2026-07-01", "auto_otp": true}
- [2026-07-01T02:36:20Z] Mafee/status — bot-start: {"account": "SpaceX", "plan_date": "2026-07-01", "auto_otp": true}
- [2026-07-01T02:53:10Z] Mafee/error — bot-fail: {"account": "SpaceX", "plan_date": "2026-07-01", "elapsed_s": 1011, "rc": 143, "log": "/home/trido/thanhdt/WorkingClaude/mike/logs/run_bot_SpaceX_2026-07-01.log"}

## Consolidation 2026-07-01T04:41:27Z
- [2026-07-01T04:39:44Z] Taylor/heartbeat — Taylor_20260701_043909: {"status": "in_progress", "note": "đọc executor._limit_price + config + plan"}
- [2026-07-01T04:40:09Z] Taylor/heartbeat — Taylor_20260701_043909: {"status": "still_running", "elapsed_min": 1, "job_id": "Taylor_20260701_043909"}
- [2026-07-01T04:41:03Z] Taylor/finding — buy-limit-price-chase-ceiling: {"job": "Taylor_20260701_043909", "question": "Vì sao rổ lệnh MUA đặt thấp hơn khá xa so với best bid?", "verdict": "BY DESIGN — không phải bug", "mechanism": "executor._limit_price (trading_bot/executor.py:243-270): px_mua = min(desired, cap), cap = ref_price*(1+max_chase_pct_buy). SpaceX live: max_chase_pct_buy=0.015 (1.5%), ref_price=close ngày signal (2026-06-30). Khi giá thị trường đã chạy >1.5% trên close hôm trước → px bị kẹp tại ref*1.015, NẰM DƯỚI bid/ask hiện tại (docstring L14-15, journal note L489 nằm chờ tại trần đuổi). Cơ chế 2: cross_mode=adaptive @1B hầu hết lệnh <1% ADV → nhánh DIP mean-reversion (_decide_cross_adaptive L209-241): nếu r15 cho thấy giá đã tăng thì cross=False → đặt bid+1tick chờ nhịp dip, KHÔNG đuổi.", "implication": "2026-07-01 go-live NEUTRAL, 23 BUY urgency=normal. Nếu phiên sáng gap-up, phần lớn lệnh mua bị cap 1.5% trên close 30/06 → treo dưới thị trường. Đây là kỷ luật anti-overpay/patience: đổi fill-rate lấy giá vào tốt hơn. Cost: ngày trending-up có thể KHÔNG khớp (atc_remainder_buy=false → phần dư bị bỏ, mai plan sync lại), KHÔNG đuổi vào ATC.", "not_a_bug": true, "citations": ["executor.py:243-270 _limit_price", "executor.py:249 cap", "executor.py:252-254 desired", "config.py:47 max_chase_pct_buy=0.015", "executor.py:209-241 adaptive DIP"]}
- [2026-07-01T04:41:09Z] Taylor/heartbeat — Taylor_20260701_043909: {"status": "still_running", "elapsed_min": 2, "job_id": "Taylor_20260701_043909"}

## Consolidation 2026-07-01T04:48:05Z
- [2026-07-01T04:45:59Z] Taylor/heartbeat — Taylor_20260701_044508: {"status": "in_progress", "note": "đọc xong executor logic — dựng scenario số"}
- [2026-07-01T04:46:08Z] Taylor/heartbeat — Taylor_20260701_044508: {"status": "still_running", "elapsed_min": 1, "job_id": "Taylor_20260701_044508"}
- [2026-07-01T04:47:09Z] Taylor/heartbeat — Taylor_20260701_044508: {"status": "still_running", "elapsed_min": 2, "job_id": "Taylor_20260701_044508"}
- [2026-07-01T04:47:53Z] Taylor/finding — abnormal-volatility-scenarios-static-caps: {"job": "Taylor_20260701_044508", "question": "Executor hành xử thế nào khi thị trường tăng/giảm bất thường? Có adaptive theo volatility không?", "verdict": "LIVE KHÔNG adaptive theo volatility — chỉ cap tĩnh 1.5%buy/3%sell + clamp trần/sàn ±7%", "live_config": {"gap_adaptive_enabled": "False (executor.py:66, LIVE cần user duyệt)", "fill_timing_live_gate": "True → mode!=paper trả 1.0 (executor.py:415)", "note": "2 layer phản ứng-biến-động đều OFF ở live; cross_mode adaptive chỉ theo %ADV size KHÔNG theo volatility"}, "case_UP": {"buy": "cap +1.5%=30450 < ask → park dưới ask, KHÔNG khớp → miss entry; DIP còn passive hơn", "sell": "khớp tại bid, ăn nhịp tăng OK"}, "case_DOWN": {"buy": "khớp ngay tại ask rẻ (sàn 27900 chặn cuối); DIP bắt dao rơi vào đà giảm — live không còn guard limit-down", "sell": "⚠ floor_cap −3%=29100 TREO TRÊN bid → KHÔNG khớp kể cả urgency=high (cap vô điều kiện) → chặn stop-loss trong crash"}, "weaknesses": ["(a) live không có phản ứng biến động cực đoan, chỉ cap tĩnh", "(b) sell floor-cap −3% chặn stop-loss thật trong sập nhanh — không có đường bán-bằng-mọi-giá", "(c) DIP bắt dao rơi ở live mất guard limit-down (guard nằm trong gap_adaptive đang tắt)"], "refs": ["executor.py:243-270 _limit_price", "executor.py:209-242 adaptive cross size-based", "executor.py:382-431 gap_adaptive (OFF live)", "config.py:47-48 caps"], "scope": "risk-probe only, KHÔNG yêu cầu sửa code"}
