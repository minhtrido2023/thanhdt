# -*- coding: utf-8 -*-
"""Cấu hình bot — đọc/ghi data/trading_bot_config.json (tạo mặc định nếu chưa có)."""

import json
import os

# Isolated worktrees can execute code against the canonical runtime data/secrets only when the
# operator opts in explicitly.  Normal bot/cron processes do not set this and retain the exact
# historical path.  Used by the one-session GDKHQ shadow: code stays isolated, reads the same
# approved plans and broker profiles as production, and still never constructs an Executor.
_CODE_WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKDIR = os.path.abspath(os.environ.get("TRADING_BOT_RUNTIME_ROOT") or _CODE_WORKDIR)
DATA_DIR = os.path.join(WORKDIR, "data")
PLAN_DIR = os.path.join(DATA_DIR, "trade_plans")
EXEC_DIR = os.path.join(DATA_DIR, "execution_logs")
CONFIG_FILE = os.path.join(os.path.dirname(DATA_DIR), "secrets", "trading_bot_config.json")
ACCOUNTS_FILE = os.path.join(os.path.dirname(DATA_DIR), "secrets", "trading_bot_accounts.json")
STOP_FILE = os.path.join(DATA_DIR, "BOT_STOP")          # tạo file này → bot dừng + hủy lệnh treo

DEFAULTS = {
    # --- chung ---
    "mode": "paper",                  # "paper" | "live"
    "broker": "phs",                  # "phs" | "dnse" (per-account override được)
    "strategy": "v23",                # key trong strategies.REGISTRY
    "account_id": None,               # None → tiểu khoản đầu tiên từ PHS
    "etf_symbol": "E1VFVN30",
    "include_etf_park": True,         # mirror cả phần park ETF của paper book

    # --- sizing / mirror ---
    "paper_init_cash": 1_000_000_000, # tiền ảo khởi tạo cho PaperBroker (VND)
    "min_order_value": 5_000_000,     # bỏ qua lệnh < 5M VND (dust)
    "qty_tolerance_pct": 0.05,        # |lệch| < 5% target → không phát lệnh sync

    # --- slicing / execution ---
    "max_child_value": 200_000_000,   # VND tối đa mỗi lệnh con
    "max_participation": 0.10,        # mua/bán ≤ 10% KL khớp lũy kế trong ngày của mã
    "capit_realized_participation_ceiling": 0.30,  # áp cho lệnh ADV20-paced (CAPIT +
                                      #   DISCRETIONARY_SPECIAL, mở rộng job Taylor_20260727_072910;
                                      #   job gốc Taylor_20260721_053659): sau khi đổi cơ sở pacing
                                      #   sang ADV20 causal, trần phụ này chặn fleet vượt 30% KL
                                      #   khớp lũy kế THẬT của phiên → không bao giờ thành đa số
                                      #   một phiên mỏng. Chọn cận trên dải 25-30% mà market-impact
                                      #   test (Taylor_20260721_050720) khuyến nghị: đủ lỏng để KHÔNG
                                      #   tái lập zero-block NCT 2026-07-21 (cần <10% realized mới
                                      #   sập) nhưng vẫn bắt đuôi >30% tape. Non-CAPIT KHÔNG dùng.
    # --- P2: mẫu số pacing = KL KỲ VỌNG tới giờ này (paper-gated, MẶC ĐỊNH TẮT) ---
    # BỆNH: `ceil_allow = 30% × KL ĐÃ khớp trong ngày` lấy làm mẫu số một đại lượng phản ánh
    # thị trường KHÔNG CÓ TA. Lúc 09:15 nó ≈0 ⇒ ta chỉ được HIỆN vài lô; người bán duy nhất
    # của một phiên mỏng xuất hiện lúc 09:40 chỉ nhìn thấy 100cp. Ca thật TV1 2026-08-11:
    # 12.400cp có sẵn ở giá ≤ trần, bot khớp 100cp; lệnh con đi 100→200→300cp — đúng chữ ký
    # "bám 30% KL luỹ kế". Đo trên N=1.840 phiên-mã (job Taylor_20260812_091343): trong
    # 1.538 phiên THỊ TRƯỜNG CÓ ĐỦ HÀNG, cơ chế hiện tại khớp 0,804 còn bỏ trần này khớp
    # 0,910 — **10,6pp là do ta tự bóp**, không do thị trường.
    # SỬA: mẫu số = max(KL đã khớp, ADV20_cp × f(t)). KL HIỂN THỊ không cần neo vào tape đã
    # xảy ra (hiện lệnh KHÔNG tiêu thụ thanh khoản của ai); chỉ KL ĐÃ KHỚP mới cần — và đó
    # là việc của `expected_volume_tape_clamp` bên dưới.
    # BẬT TRÊN PAPER 2026-08-17 (user John chốt qua Mike, job Taylor_20260814_161511) — VẪN LÀ
    # PAPER-ONLY nhờ `expected_volume_pacing_live_gate` ngay dưới. Không account LIVE nào đổi
    # hành vi: cờ này một mình KHÔNG đủ, gate phải TẮT thì P2 mới ăn ở mode≠paper.
    "expected_volume_pacing_enabled": True,    # PAPER 2026-08-17 (was False)
    # Cổng LIVE — cùng cơ chế `fill_timing_live_gate` (executor.py:1207) đã dùng cho HYBRID:
    # True ⇒ P2 chỉ ăn ở account `mode == "paper"`; mọi account live giữ nguyên byte-identical
    # hành vi cũ. Fail-safe: `.get(..., True)` ⇒ cấu hình THIẾU khoá này = gate BẬT (paper-only),
    # không phải mở toang. Flip sang False = đưa P2 lên tiền thật ⇒ cần quant-skeptic CONFIRMED
    # + user sign-off RIÊNG (gate criteria: kb/paper_programs_charter/expvol_pacing.md).
    "expected_volume_pacing_live_gate": True,
    # Đối chứng GHÉP CẶP trên tape THẬT (log-only, KHÔNG đổi hành vi ở bất kỳ mode nào): khi P2
    # đang TẮT/bị gate, executor vẫn tính allowance mà P2 SẼ cho ở cùng lệnh/cùng tape/cùng
    # giây, rồi ghi journal `EXPVOL_SHADOW`. Đây là mẫu ghép cặp DUY NHẤT có thể có: paper
    # không sinh fill thật (PaperBroker khớp đúng giá đặt), còn bật P2 trên live thì đã là thay
    # đổi hành vi — tức thứ ta đang xin phép đo. Tắt = mất nguồn số của paper trial, không mất
    # an toàn.
    "expected_volume_pacing_shadow_log": True,
    # Order-book execution research v1 (user duyệt 2026-08-15): THUẦN TELEMETRY/SHADOW.
    # Không field nào dưới đây được đọc vào `_child_qty`, `_limit_price` hay lịch HYBRID.
    "order_book_shadow_enabled": True,
    "order_book_snapshot_max_age_ms": 5_000,
    "order_book_shadow_policy_version": "spread_depth_v1",
    "order_book_reduce_spread_ticks": 2.0,
    "order_book_defer_spread_ticks": 4.0,
    "order_book_reduce_depth_ratio": 1.0,
    "order_book_defer_depth_ratio": 0.5,
    # Trần đuôi neo vào TAPE THẬT: fill luỹ kế của fleet ≤ 50% KL khớp thật của phiên.
    # Suy ra allowance: đặt F=fleet đã khớp, V=KL phiên (V ĐÃ gồm F). Fill thêm X vẫn giữ
    # F+X ≤ c(V+X) ⇒ X ≤ (cV−F)/(1−c); với c=0,5 ⇒ **X ≤ V − 2F**. KHÔNG dùng dạng lỏng tay
    # `cV−F` (bỏ quên việc chính fill của ta cũng làm V tăng) lẫn dạng chặt tay hơn mức cần.
    # Vì sao cần: bỏ HẲN trần 30% cho ta chiếm >50% tape ở 6,9% số phiên (>80% ở 3,5%) — do
    # floor_allow neo vào ADV20 chứ không vào KL THẬT hôm nay, mà 12,7% số phiên có KL
    # <30% ADV20. Clamp này bịt đúng nhóm đó mà không bóp đầu phiên.
    "expected_volume_tape_clamp": 0.50,
    # f(t) = tỷ trọng KL luỹ kế TRUNG VỊ tới phút t (phút tính từ 00:00 ICT), đo trên rổ 23 mã
    # mỏng × 120 phiên (out/cum_volume_profile.csv, đã ép đơn điệu không giảm). Nội suy tuyến
    # tính giữa 2 mốc; trước mốc đầu = 0 (⇒ P2 KHÔNG ăn, hành vi cũ); sau mốc cuối = 1,0.
    # Lưu ý ngược trực giác đã đo: 14:45+ (ATC) chỉ ~5% KL trung vị — "dồn vào ATC cho chắc
    # khớp" KHÔNG đúng với nhóm mã này.
    "expected_volume_curve": [[555, 0.045], [570, 0.082], [585, 0.145], [600, 0.198],
                              [615, 0.246], [630, 0.318], [645, 0.351], [660, 0.411],
                              [675, 0.444], [690, 0.488], [780, 0.499], [795, 0.568],
                              [810, 0.637], [825, 0.721], [840, 0.784], [855, 0.853],
                              [870, 0.958], [885, 1.000]],
    "slice_interval_min": 8,          # phút giữa 2 lệnh con cùng một parent
    "poll_interval_sec": 20,          # chu kỳ poll sổ lệnh + quote
    "chase_ticks": 1,                 # mua: đặt bid + n tick (passive); 0 = đặt ngay bid
    "buy_cross_spread": True,          # True: mua đặt thẳng giá ask (marketable)
    "cross_mode": "adaptive",         # "adaptive" (default, user+Taylor 2026-06-26): DIP khi
                                      #   order_value/ADV < adaptive_cross_adv_threshold, else
                                      #   TWAP. @1B hầu hết lệnh <0.1% ADV → DIP tự nhiên;
                                      #   khi NAV lớn shift TWAP không cần reconfig.
                                      # "always": TWAP — cross mọi slice (archived; Taylor
                                      #   backtest: fill-rate hơn dip 3.5bps nhưng variance 2×).
                                      # "dip": S2 mean-reversion (archived — beat by adaptive).
    "adaptive_cross_adv_threshold": 0.01,  # 1% ADV: dưới ngưỡng → DIP; trên → TWAP.
                                           # Taylor backtest: DIP fill 0.90→0.38 khi >1% ADV.
    "dip_window_min": 15,             # cửa sổ return quyết định cross/passive
    "px_sample_sec": 60,              # chu kỳ ghi giá vào px_hist (tính r15)
    "max_chase_pct_buy": 0.015,       # trần đuổi giá mua = ref_plan × (1+1.5%)
    "max_chase_pct_sell": 0.03,       # sàn đuổi giá bán = ref_plan × (1−3%)
    # Dung sai cổng đối soát cơ sở giá cho lệnh mua LUẬT A ngay trước khi đặt
    # (Executor._rule_a_ref_guard → no_chase_ceiling.check_ref_vs_live). Vượt ⇒ KHÔNG đặt lệnh
    # đó + bắn event bus RULE_A_REF_PRICE_MISMATCH. 1% chọn từ số đo N=66 mã ngày 2026-08-15 —
    # căn cứ đầy đủ ở `no_chase_ceiling.RULE_A_REF_TOL_DEFAULT`, đừng đổi số này mà không đọc.
    "rule_a_ref_tol_pct": 0.01,
    "atc_remainder_sell": True,       # phần bán còn sót → quét ATC
    "atc_remainder_buy": False,       # phần mua còn sót → mặc định bỏ (mai plan mới tự sync)
    "paper_fee_rate": 0.0015,         # phí mô phỏng paper (0.15% mỗi chiều)

    # --- fill-timing (Layer-3 WHEN-to-fill, đặt trên adaptive cross_mode) ---
    # Taylor backtest 16 names 9670 ticker-days: Open là giờ TỆ nhất mua (+18.7bps),
    # 11:15 là đáy intraday (+1.1bps). SELL: Open là TỐT nhất (+18.7bps morning premium).
    # Lợi ~17.6bps/lệnh mua vs Open, ~5-6bps vs uniform/VWAP (edge trung bình, std cao).
    "fill_timing_enabled": True,      # True: side-aware schedule; False: uniform (tắt hẳn)
    "fill_timing_live_gate": True,    # True: chỉ paper; live cần user tắt thủ công (real money)
    # HYBRID là lịch thực thi khác, có thêm defer/block-cap và đã từng lộ bug tương tác
    # EXTREME trong paper.  Giữ cổng LIVE ĐỘC LẬP: ngày mở fill-timing cơ bản không được
    # vô tình mở luôn HYBRID chỉ vì cả hai cùng là Layer-3.
    "fill_timing_hybrid_live_gate": True,  # True: HYBRID paper-only, kể cả base timing đã live
    "buy_window_start": "10:45",      # BUY: đầu cửa sổ tập trung (ICT)
    "buy_window_end": "11:15",        # BUY: cuối cửa sổ (đáy intraday)
    "sell_window_start": "09:15",     # SELL: tập trung ở Open (đỉnh morning premium)
    "sell_window_end": "09:45",       # SELL: cuối cửa sổ Open
    "fill_timing_outside_mult": 4.0,  # interval × mult ngoài cửa sổ (8min → 32min mặc định)

    # --- fill-timing HYBRID (trải TWAP BÊN TRONG cửa sổ thuận lợi) — PAPER-ONLY ---
    # Taylor 2026-08-10 (job Taylor_20260810_034544), triển khai từ nghiên cứu đã CONFIRMED
    # `mike/agents/Taylor/research/twap_vs_window_execution_20260804.md` §6/§10 — 663 phiên
    # độc lập, nến 15', 33 mã ta thật sự giao dịch, 2023-09-11 → 2026-05-12.
    #   BUY  trải 5 block 11:00-13:45: −6,94 bps vs day-VWAP (t=−6,80), sd 26,3 (gom-1-điểm
    #        @11:15: −7,37 bps, sd 35,5) — giữ 94% edge, cắt 26% độ phân tán.
    #   SELL trải 4 block 09:15-10:15: +8,89 bps (t=4,64), sd 49,4 (gom @09:15: +9,27, sd 59,3).
    #        KHÔNG gom tại mở cửa: "edge" +9,3 bps của gom-mở-cửa là ĐẶT CƯỢC HƯỚNG PHIÊN
    #        (ngày tăng >2% −168 bps / ngày giảm >2% +151 bps), không phải edge thực thi.
    #   Vòng khứ hồi: gom +16,65 bps (sd 62,0) → HYBRID +15,83 bps (sd 53,5), t 6,91 → 7,62.
    # QUY MÔ KINH TẾ NHỎ (~0,1-0,3%/năm ở vòng quay ~3×NAV/năm): đây là VỆ SINH CHI PHÍ,
    # KHÔNG phải đòn bẩy alpha — đừng đánh đổi rủi ro/độ phức tạp để lấy.
    # CAVEAT (§8 báo cáo, mang theo khi trích dẫn): (1) KHÔNG đo được impact của chính lệnh ta;
    # (2) KHÔNG có điều kiện tín hiệu — mẫu là MỌI ngày của 33 mã, không riêng ngày có tín hiệu
    # LAG/BAL; (3) cache `intraday_full.pkl` STALE, hết 2026-05-12 (2026 chỉ 84 phiên);
    # (4) giá thực thi là XẤP XỈ `(H+L+C)/3` của block, KHÔNG phải fill thật; (5) bỏ ATC 14:45.
    # DEFAULT OFF + fill_timing_live_gate ⇒ paper-only; bật LIVE cần user duyệt riêng.
    # BẬT TRÊN PAPER 2026-08-10 (job Taylor_20260810_034544, quant-skeptic CONFIRMED). VẪN LÀ
    # PAPER-ONLY: muốn chạy HYBRID LIVE phải tắt RIÊNG `fill_timing_hybrid_live_gate`; việc
    # tắt `fill_timing_live_gate` chỉ mở lịch fill-timing cơ bản, không kéo HYBRID theo.
    "fill_timing_hybrid_enabled": True,    # PAPER 2026-08-10 (was False) — cần fill_timing_enabled=True
    # Nhãn block = ĐÚNG các nến 15' đã đo (trung bình của chúng tái lập chính xác −6,94/+8,89 bps
    # trong §6 báo cáo) — KHÔNG phải "chia đều N điểm trong khoảng", vì khoảng 11:00-13:45 có
    # nghỉ trưa HOSE 11:30-13:00 (chia đều theo đồng hồ sẽ rơi vào lúc thị trường đóng).
    "hybrid_buy_blocks": ["11:00", "11:15", "13:00", "13:15", "13:30"],
    "hybrid_sell_blocks": ["09:15", "09:30", "09:45", "10:00"],
    "hybrid_block_min": 15,                # bề rộng 1 block (phút) — đúng lưới nến của nghiên cứu

    # --- gap-adaptive fill (Layer-3 extension, PAPER only until user approves LIVE) ---
    "gap_adaptive_enabled": False,    # DEFAULT OFF; set True only for paper. LIVE needs user approval.
    "gap_floor_band": 0.07,           # fallback floor band when broker doesn't expose floor price (HOSE default).

    # --- vol-scaled buy chase-cap (patch#3, Taylor 2026-07-01, backtest CONFIRMED tail-insurance) ---
    # Widen ONLY the buy chase ceiling on high-vol names so a static 1.5% cap doesn't 0-fill a whole
    # basket on correlated gap-up mornings (the go-live failure: 2025-04-10 static missed 12/12 names).
    #   cap_pct = clamp(k * rvol_20d, floor=max_chase_pct_buy, ceil=chase_cap_vol_ceil)
    # Monotone-safe (floor == static cap → only widens, never tightens); fail-safe to the static cap
    # when rvol_20d is missing/<=0. Independent of allocator/selection (touches only _limit_price buy).
    # Backtest (chase_cap_backtest.py, quant-skeptic CONFIRMED): fill 97.5→99.3%, +6.6bps common-case
    # entry cost, tail-catch trades +5.9% fwd20 / win 68%; NET ~0 on avg → INSURANCE, not return-enhancer.
    # LIVE since 2026-08-04 (user sign-off "phương án A"; quant-skeptic CONFIRMED high, job
    # Taylor_20260804_124404). Paper gates 1-3 PASS on 80 real BUY orders / 13 executor sessions;
    # gate 4 (real-fill vs min(open,L) proxy at 50B NAV) was RE-SCOPED, not passed — PaperBroker
    # fills exactly at the placed price by construction, so paper can never yield real-fill data.
    # ACCEPTED OPEN RISK: size-impact at 50B NAV untested; live NAV today (~0.97B/0.91B ≈ 1.9% of
    # that target) is the same order of magnitude as the paper-tested regime. REOPEN gate 4 as NAV
    # grows toward 50B, and re-verify the resolved flag before enabling any new live account.
    "chase_cap_vol_scale_enabled": True,   # LIVE 2026-08-04 (was False = paper-only).
    "chase_cap_vol_k": 2.0,                # k in clamp(k*rvol_20d, static, ceil).
    "chase_cap_vol_ceil": 0.04,            # hard ceiling on the widened buy cap (never chase beyond +4%).

    # --- EXTREME-regime execution gate (Taylor 2026-07-01, backtest-validated tail-insurance) ---
    # Always-on risk gate that only trips in confirmed abnormal DOWN moves. SELL → sell-to-floor
    # (chase down to the daily floor instead of stranding at the −3% cap); BUY → pause (T+1 re-sync).
    # Backtest (data/extreme_regime_backtest.md, quant-skeptic CONFIRMED): compresses the sell tail
    # (worst −13.4%→−6.9%, dispersion 3.8→0.3pp, same-day fill 0→100%) for ~1pp mean cost — insurance,
    # NOT a return-enhancer. DEFAULT OFF; LIVE enable needs explicit user sign-off after paper-trading.
    "extreme_regime_enabled": False,  # DEFAULT OFF — deliberate activation only.
    "extreme_band": 0.03,             # SELL/BUY trip when last within 3% of the daily floor (near limit-down).
    "extreme_move_z": 3.0,            # …or when r15 down-move exceeds z × 20d realised vol.
    "extreme_slice_mult": 0.25,       # shorten cancel/reprice cadence ×0.25 (~2min) to chase the falling book.
    "extreme_cooldown_min": 15,       # once tripped, stay active this long (debounce flicker).
    # Giãn nhịp poll EXTREME khi lệnh đang bị lịch HYBRID HOÃN (chỉ nhánh đó; đường đặt lệnh bình
    # thường không đổi). Cần vì lệnh bị hoãn phải tiếp tục poll để bộ đếm 2-poll-confirm chạy —
    # nếu không sẽ deadlock (không bao giờ arm được ⇒ lệnh bán khẩn kẹt; xem executor.py). Đo
    # thật: không throttle = +359 lời gọi get_quote/lệnh/phiên (PHS cache TTL 3s < poll 20s).
    # 60s ⇒ arm chậm nhất ~2' KỂ TỪ LẦN QUOTE CHẠY ĐƯỢC ĐẦU TIÊN, tải API về đúng bậc cũ.
    # 0 = tắt throttle (poll mỗi chu kỳ). Throttle chỉ tính từ lần poll THÀNH CÔNG: quote lỗi
    # (PHSBroker trả None khi exception) được thử lại ngay chu kỳ sau, không tiêu cửa sổ 60s —
    # nếu không, chuỗi quote lỗi đúng nhịp 60s sẽ khoá EXTREME cả cửa sổ hoãn (REFUTED vòng 4).
    "extreme_defer_poll_sec": 60,

    # --- DC-book NEUTRAL idle-cash WATERFALL (Taylor 2026-07-06, user-approved paper trial) ---
    # When DT5G=NEUTRAL and BAL/LAG have no qualifying deal, fill idle cash in priority:
    #   BAL/LAG (unchanged) → DC book (ConvergePort double-confirm, 8L≤2 ∧ sector-lens BUY,
    #   ex-DHG, cap 0.20/name) → custom30V. Reverse-unwind (custom30V first, DC book second)
    #   when BAL/LAG get a deal back. Research: job Taylor_20260706_125540 (DC-below-BAL/LAG
    #   CONFIRMED, +~1pp/yr full-V2.4, insurance-grade DSR 0.775). This flag ONLY gates the
    #   self-contained PAPER sleeve (dc_book_waterfall_paper.py) — it touches NO production
    #   plan builder / executor. DEFAULT OFF; ON only on paper account `main`.
    "dc_book_waterfall_enabled": False,  # DEFAULT OFF — paper only.

    # --- an toàn ---
    "max_orders_per_day": 60,         # tổng số parent order tối đa trong 1 plan
    "max_daily_gross_value": 20_000_000_000,  # tổng GTGD tối đa 1 ngày (VND)
}


ACCOUNT_DEFAULTS = {
    "label": "main",            # tên định danh — namespace mọi file plan/state/journal
    "enabled": True,
    "mode": None,               # None → dùng mode chung trong trading_bot_config.json
    "broker": None,             # None → broker chung; "phs" | "dnse"
    "credentials_file": None,   # None → creds mặc định theo broker
    "account_id": None,         # None → tiểu khoản đầu tiên của login/key đó
    "note": "",
    "overrides": {},            # override bất kỳ khóa nào của config chung cho riêng account
    "excluded_tickers": [],     # mã KHÔNG BAO GIỜ tự động mua/bán (legacy/special-situation
                                # holding nằm ngoài rebalancing V2.4 — vd DGC trong tài khoản
                                # ZaloPay, đang hạn chế giao dịch HOSE). Enforce cứng ở
                                # bot_execute.py (lọc plan.orders) — không phụ thuộc vào việc
                                # plan generator có nhớ loại trừ đúng hay không. Dùng
                                # `bin/compute_active_nav.py` để tính NAV thực sự khả dụng cho
                                # chiến lược (= account_nav − giá trị thị trường các mã này) khi
                                # lên plan/backtest/báo cáo cho account có field này khác rỗng.
    "manual_offbook_assets_vnd": 0,      # tài sản off-book KHÔNG lộ qua DNSE OpenAPI (KHÔNG bao
                                # gồm "Trứng vàng" — từ 2026-08-18 Trứng vàng tự đọc qua field
                                # egg.totalValue trong balances() API, không cần user báo tay nữa).
                                # Field này CHỈ dùng cho tài sản off-book KHÁC egg (nếu có).
                                # Cộng vào TRUE NAV ở daily_nav_snapshot.py/compute_active_nav.py —
                                # KHÔNG cộng vào 'cash' (sức mua thực sự khả dụng để đặt lệnh).
    "manual_offbook_assets_asof": None,  # ngày user báo số dư này (YYYY-MM-DD)
    "manual_offbook_assets_note": None,  # vd "Trứng vàng DNSE"
}


def load_accounts(cfg, path=ACCOUNTS_FILE):
    """Đọc danh sách account profile; chưa có file → tạo template 1 profile 'main'.

    Trả về list profile đã chuẩn hóa, mỗi profile có thêm khóa "cfg" = config
    hiệu lực (config chung + overrides + mode/account_id của profile).
    """
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            raw = json.load(f).get("accounts", [])
    else:
        raw = [{"label": "main", "mode": cfg["mode"],
                "account_id": cfg.get("account_id"),
                "note": "profile mặc định — thêm account mới vào danh sách này"}]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"accounts": raw}, f, indent=2, ensure_ascii=False)
        print(f"[config] tạo file account profile mặc định: {path}")

    profiles, seen = [], set()
    for r in raw:
        p = dict(ACCOUNT_DEFAULTS)
        p.update(r)
        if p["label"] in seen:
            raise ValueError(f"trùng label account '{p['label']}' trong {path}")
        seen.add(p["label"])
        eff = dict(cfg)
        eff.update(p.get("overrides") or {})
        eff["mode"] = p["mode"] or cfg["mode"]
        eff["account_id"] = p["account_id"]
        p["cfg"] = eff
        profiles.append(p)
    return profiles


def pick_accounts(profiles, labels=None):
    """Lọc profile theo --account labels; mặc định = mọi profile enabled."""
    if labels:
        by = {p["label"]: p for p in profiles}
        missing = [l for l in labels if l not in by]
        if missing:
            raise KeyError(f"không có account {missing} — có: {sorted(by)}")
        return [by[l] for l in labels]
    return [p for p in profiles if p["enabled"]]


def live_dnse_labels(path=ACCOUNTS_FILE):
    """Danh sách label các account THẬT đang chạy tự động hàng ngày (enabled=True,
    mode="live", broker="dnse") — dùng bởi mọi script cron dùng-chung (preflight,
    ops_health_check, send_plan_report, eod_trading_report, bq_freshness_check) để lặp
    qua TẤT CẢ account live thay vì hardcode 1 tên. Thêm account mới vào
    trading_bot_accounts.json với enabled=true/mode=live/broker=dnse là tự động được các
    script này nhận, KHÔNG cần sửa code/cron riêng (xem kb/account_onboarding_runbook.md).
    """
    cfg = load_config()
    profiles = load_accounts(cfg, path=path)
    return [p["label"] for p in profiles
            if p["enabled"] and p["cfg"]["mode"] == "live" and p["broker"] == "dnse"]


def load_config(path=CONFIG_FILE):
    cfg = dict(DEFAULTS)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        unknown = sorted(set(user) - set(DEFAULTS))
        if unknown:
            print(f"[config] ⚠ khóa lạ trong {os.path.basename(path)}: {unknown}")
        cfg.update(user)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULTS, f, indent=2, ensure_ascii=False)
        print(f"[config] tạo file cấu hình mặc định: {path}")
    return cfg
