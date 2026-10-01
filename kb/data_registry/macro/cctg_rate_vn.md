---
kind: config
status: CANONICAL-PROXY (single-anchor, bootstrapped 2026-10-01)
source: cctg_rate_vn.py (CCTG_EVENTS + data/cctg_rate_vn_events.csv append-only)
group: macro
role: DISPLAY-ONLY input (combined via deposit_rate_vn.effective_deposit_rate()); NOT wired into
  any LIVE production selector/gate output as of 2026-10-01
writer: 1 mốc frozen 2026-10-01 (job Taylor_20261001_032954) + CSV append-only cho mốc tương lai
verified_by: Taylor, job Taylor_20261001_032954
---

# `cctg_rate_vn.py` — Big-4 CHỨNG CHỈ TIỀN GỬI (CCTG), kỳ hạn 6 tháng

**Status: CANONICAL-PROXY, single anchor.** Series MỚI, tách biệt hoàn toàn khỏi
`deposit_rate_vn.py` (Big-4 12M term-deposit, [[deposit_rate_vn]]) — không ghi đè, không gộp,
không restate lịch sử.

## Là gì
Lãi suất CCTG nhóm Big-4 (VCB/BIDV/CTG/Agribank), kỳ hạn **6 tháng** — KHÁC kỳ hạn với chuỗi
12M đang dùng, một dấu hiệu cần giữ nguyên khi hiển thị (đường cong đảo khi 6M > 12M là tín hiệu
thị trường thật, không phải lỗi).

## Dữ liệu
Mốc duy nhất: `2026-09-30, 7.5%` — nguồn VietnamNet 30/09/2026 (nhóm Big-4; một số NH cổ phần tới
9,4% nhưng NGOÀI phạm vi chuỗi này, giữ nhất quán Big-4-only với `deposit_rate_vn.py`).

## Pháp lý (nguồn thứ cấp, CHƯA re-verify độc lập bởi legal-vn session riêng)
CCTG ≈ tiết kiệm về bảo hiểm tiền gửi (Luật 111/2025, hạn mức 350 triệu VND), lãi miễn thuế TNCN,
lãi suất kỳ hạn ≥6 tháng do thị trường quyết định (không trần SBV). Đây là tóm tắt do user relay
2026-10-01, CHƯA được legal-vn agent độc lập xác nhận trong phiên này — re-verify trước khi trích
dẫn trong tài liệu gửi khách hàng.

## Cơ chế kết hợp
`deposit_rate_vn.effective_deposit_rate(asof)` = max(Big-4 12M, CCTG 6M) **CHỈ KHI** CCTG fresh
(cùng ngưỡng 45 ngày) và trong khoảng hợp lệ [0.5%, 30%] — không bao giờ lấy trung bình, không
bao giờ để CCTG lấn Big-4 khi CCTG đang stale/thiếu. Trước 2026-09-30, `current_cctg_rate()` trả
`None` cho mọi asof ⇒ mọi backtest pin trước ngày này **byte-identical** với thế giới chưa có
module này.

`macro_killswitch_a_status()` (`deposit_rate_vn.py`) đã wire overlay này — hôm nay (2026-10-01,
asof production với CSV thật) effective=7,5% (CCTG đang là driver), trigger `>` 7,5% strict ⇒
**CLEAR đúng ngưỡng** (không armed). Lưu ý: trong worktree R&D (`wt-depgate75-1001`) CSV Big-4 thật
bị `.gitignore` ẩn nên gọi không-asof trả stale=True — đây là giới hạn môi trường worktree, KHÔNG
phải bug; production đọc đúng CSV thật (`data/deposit_rate_vn_events.csv`, mốc 2026-09-04) sẽ
không stale.

## Kiểm kê consumer `current_deposit_rate()`/`merge_deposit()` + quyết định wiring (2026-10-01)

| Consumer | File | Loại | Quyết định |
|---|---|---|---|
| Kill-switch A (`macro_kill_switches.A_sbv_rate_suspend`) | `deposit_rate_vn.py::macro_killswitch_a_status` | DISPLAY + kill-switch, KHÔNG sizing/order (sleeve nó gate là PROPOSED/paper) | **WIRED** 2026-10-01 |
| Value Radar | `value_radar.py` | DISPLAY-ONLY (CLAUDE.md §6b — không phải tín hiệu mua/bán) | **WIRED** 2026-10-01 |
| `rating_8l.py` NEUTRAL-only deposit tilt | `rating_8l.py:881-882` | **LIVE daily** (±0.03 trên `value_score_v3`, chạy `pt_8l_daily.sh` 17:45 ICT, validated 2026-06-19) | **KHÔNG WIRE** — đổi output rating sống mỗi ngày. User directive (2026-10-01): consumer đổi output live thì phải nộp bảng diff, không tự quyết |
| `trading_bot/due_diligence.py` YIELD_FLOOR (`_yield_floor()`) | fear-buy backstop sleeve, live QUALIFY/NON cho BUY order bị flag | **LIVE** | **KHÔNG WIRE** |
| `custom30_yield_labels.py` | batch-equivalent của `_yield_floor()` (đã verify khớp 120/120, job Taylor_20260818_131745) | Phải đi CÙNG với due_diligence.py để giữ bất biến khớp-số — wire 1 mình sẽ làm 2 bản lệch nhau | **KHÔNG WIRE** (ràng buộc theo due_diligence.py) |
| `dcf_valuation.py` (discount rate r = Big-4 + ERP) | feeds `due_diligence.py` fear-buy DCF leg + research | **LIVE** (qua due_diligence chain) | **KHÔNG WIRE** |
| `dcf_refresh_gate.py`, `dcf_rate_robustness.py` | giám sát/độ nhạy cho chain DCF ở trên | Cùng chain DCF | **KHÔNG WIRE** (giữ nhất quán với leg DCF) |
| `macro_confidence_regime.py` | RESEARCH/DISPLAY-ONLY, chạy một lần, "writes nothing to production paths" (tự khai trong docstring) | Không phải consumer sống lặp lại | Ngoài phạm vi — không cần quyết |
| `append_deposit_rate.py`, các `pt_v23_*`/`probe_*`/`backtest_*`/`engine_*` research & `deploy_golive_dt5g_v4/golive_recommend_v23.py` | công cụ ghi chuỗi Big-4 / backtest lịch sử / go-live engine điểm-trong-thời-gian | Không phải consumer sống lặp lại | Ngoài phạm vi — không cần quyết |

### Diff cụ thể cho 2 consumer bị chặn (để user cân nhắc)
- **`rating_8l.py` tilt, hôm nay**: Big-4-only `_dep=6.8%` (như hiện hành) vs effective=7,5% nếu
  wire ⇒ `_spread = earn_yield*100 - _dep` dịch **−0,7pp** cho MỌI mã ở cả 2 ngưỡng (`>=3` và
  `<0`) ⇒ một số mã nằm sát biên sẽ đổi tilt từ 0 → −0,03 hoặc +0,03 → 0. Không đo được số mã cụ
  thể bị đổi trong phiên này (cần chạy `rating_8l.py` live để liệt kê) — đây chính là lý do không
  tự wire.
- **`due_diligence.py`/DCF chain**: dùng `current_deposit_rate()` làm risk-free/hurdle rate —
  effective cao hơn 0,7pp sẽ hạ fair-value DCF (discount rate cao hơn), có thể đổi QUALIFY→NON cho
  mã nằm sát ngưỡng margin-of-safety. Cùng lý do không tự wire.

## Bẫy
1. **Tenor mismatch 6M vs 12M** — max() là CỐ Ý (đường cong đảo là tín hiệu thật), nhưng MỌI báo
   cáo trích effective rate phải nói rõ driver (`rate_source` field) — đừng gộp mù thành "lãi suất
   tiền gửi" chung chung.
2. **Chỉ 1 mốc dữ liệu (2026-09-30)** — chưa có lịch sử CCTG, không dùng cho backtest trước ngày
   này (sẽ luôn trả `None`/fallback Big-4, đúng thiết kế, không phải thiếu sót cần "làm giàu thêm
   lịch sử" một cách hồi tố).
3. **Pháp lý chưa re-verify độc lập** — xem mục Pháp lý ở trên.
