# PENDING — flip `chase_cap_vol_scale_enabled` sang LIVE (patch#3 vol-scale buy chase-cap)

- **Job**: `Taylor_20260804_124404` · **Ngày**: 2026-08-04 · **Owner**: Taylor
- **Trạng thái**: ĐÃ ĐỦ ĐIỀU KIỆN, **CHƯA ÁP DỤNG** — thao tác sửa `trading_bot/config.py`
  bị **auto-mode classifier CHẶN** trong phiên headless này (đúng thiết kế: LLM headless không
  được tự chạm cấu hình tiền thật — xem `kb/context_pack.md` § Kiến trúc fleet).
  **KHÔNG bypass.** Cần 1 phiên interactive (Mike/user) áp patch dưới đây.

## Điều kiện đã đủ

| Cổng | Kết quả |
|---|---|
| User sign-off | ✅ John 2026-08-04: *"Vol-scale vì là bước bảo hiểm rẻ tiền, tôi đồng ý chọn A cho go-live."* |
| Gate 1-3 (paper) | ✅ PASS — 80 lệnh BUY thật / 13 phiên executor paper main |
| Gate 4 | 🔄 RE-SCOPED (không phải PASS) — paper không sinh được fill thật |
| quant-skeptic | ✅ **CONFIRMED / confidence high** — log `mike/logs/verify_20260804_124744.log` |

## Rủi ro còn treo (được chấp nhận tường minh)

Size-impact ở NAV 50 tỷ **chưa từng kiểm** và **không kiểm được trên paper** (PaperBroker khớp
đúng bằng giá limit đã đặt — quant-skeptic verify lại trong `brokers.py::_try_fill`).
Giảm nhẹ: NAV live 2026-08-04 = SpaceX 965.416.271đ, ZaloPay 906.684.413đ ≈ **1,9% NAV target
50 tỷ**, cùng bậc với quy mô paper đã đo (`paper_init_cash` 1 tỷ).
**Điều kiện mở lại gate 4**: NAV live tiến gần 50 tỷ (mốc theo dõi: gross lệnh/phiên vượt ~343tr).

## Cách áp (chạy trong phiên interactive)

```bash
cd /home/trido/thanhdt/WorkingClaude
git apply --check mike/agents/Taylor/pending_live_flip_chase_cap_20260804/flip_live.patch   # đã verify: sạch
git apply         mike/agents/Taylor/pending_live_flip_chase_cap_20260804/flip_live.patch
# self-check BẮT BUỘC sau khi áp (cả 3 ĐÃ chạy PASS ở bản mô phỏng, xem §Đã verify):
/home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/stress_vol_scale_chase_cap.py   # kỳ vọng RESULT: PASS
/home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/chase_cap_selfcheck.py          # kỳ vọng ALL PASS
/home/trido/thanhdt/wc_venv/bin/python dc_book_waterfall_selfcheck.py                     # kỳ vọng ALL PASS
# repo NGOÀI (WorkingClaude):
git add trading_bot/config.py dc_book_waterfall_selfcheck.py
git commit -m "chase-cap patch#3: flip chase_cap_vol_scale_enabled -> LIVE (user sign-off + quant-skeptic CONFIRMED, job Taylor_20260804_124404)"
# repo NESTED (mike/) — 2 file selfcheck của Taylor nằm trong repo con:
cd mike && git add agents/Taylor/stress_vol_scale_chase_cap.py agents/Taylor/chase_cap_selfcheck.py && \
  git commit -m "chase-cap patch#3 selfchecks: expect LIVE default (job Taylor_20260804_124404)"
```

## Đã verify TRƯỚC khi giao patch (không phải đọc-thấy-hợp-lý)

Mô phỏng flip **trong bộ nhớ** (`DEFAULTS["chase_cap_vol_scale_enabled"]=True` rồi `runpy` file
đã vá) — KHÔNG chạm file thật:

| Selfcheck (bản đã vá) | Kết quả dưới flip mô phỏng |
|---|---|
| `stress_vol_scale_chase_cap.py` | **RESULT: PASS** (14 assert, gồm NEG-control mới) |
| `chase_cap_selfcheck.py` | **ALL PASS** |
| `dc_book_waterfall_selfcheck.py` | **61 passed, 0 failed — ALL PASS** |
| `dcf_check_selfcheck.py` (không cần vá, fixture tường minh) | OK 20/20 |

⚠️ Chính bước mô phỏng này **bắt được file thứ 4** (`chase_cap_selfcheck.py:32`, assert
"shipped default OFF") mà bản patch đầu bỏ sót — nếu chỉ đọc diff thì đã ship thiếu.

## Cơ chế bật — đã đọc code, KHÔNG đoán

`trading_bot/config.py::load_accounts()`: `eff = dict(cfg); eff.update(profile["overrides"])`
⇒ thứ tự ưu tiên **DEFAULTS → `secrets/trading_bot_config.json` → per-account `overrides`**.

- `secrets/` bị `.gitignore` (chỉ `README.md` tracked) ⇒ bật bằng per-account override là thay
  đổi **không auditable qua git** → **loại**.
- `secrets/trading_bot_config.json` hiện **không có** khoá này ⇒ giá trị DEFAULTS có hiệu lực.
- SpaceX `overrides=None`, ZaloPay `overrides={"cross_mode":"always"}` ⇒ flip global default
  **có tới được cả 2 account live**. Paper `main` đã override `true` (không đổi).

⚠️ **RocketX** (`enabled=false`, mode=live, không override) — flip global sẽ **bật sẵn** cờ này
nếu ai đó enable RocketX sau này. Đây là `recommended_reruns[2]` của quant-skeptic: phải
verify lại cờ hiệu lực của RocketX **trước khi** cho nó giao dịch.

## 4 file thay đổi

1. `trading_bot/config.py:87` — `False` → `True` + chú thích go-live.
2. `dc_book_waterfall_selfcheck.py:224-226` — assert D1 tách ra: `extreme_regime_enabled` vẫn
   phải False, `chase_cap_vol_scale_enabled` nay phải True (LIVE).
3. `mike/agents/Taylor/stress_vol_scale_chase_cap.py` — cổng 0 đổi kỳ vọng (paper/live/global đều
   True); NEG-control §5 giữ nguyên **mục đích** (chứng minh việc nới trần đến TỪ CỜ) nhưng đổi
   nguồn: dùng bản copy `live_cfg` ép cờ `False` thay vì trông vào việc live vốn tắt.
4. `mike/agents/Taylor/chase_cap_selfcheck.py:31-34` — assert `0) shipped default OFF` →
   `0) shipped default ON (LIVE 2026-08-04)`.
