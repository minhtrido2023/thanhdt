# Rà soát kiến trúc vận hành team Mike — 2026-10-08

Phạm vi đo: 14 ngày 2026-09-24 → 10-08, số liệu lấy từ `bus/jobs/`, `kb/recent_delta.jsonl`, crontab, `wc -c` các file nạp mỗi phiên, `wakeup_audit.py`. Không có số token/chi phí per-job vì dispatch.sh không ghi (xem phát hiện 4) — mọi ước lượng tiết kiệm bên dưới là ƯỚC LƯỢNG, không phải đo.

## Kết luận ngắn

Kiến trúc hiện nay **tốt về độ đúng và an toàn** (fail-closed, bot đặt lệnh deterministic không qua LLM, quant-skeptic/arch-review trước khi wire, bus + claim-reply nguyên tử, circuit breaker dispatch). **Yếu về kỷ luật chi phí và tính cân xứng**: mức review và mức context không phân bậc theo rủi ro của thay đổi, luật chỉ tích luỹ không bao giờ nghỉ hưu, và không có telemetry token nên không ai thấy tiền đi đâu.

## 5 phát hiện có số

| # | Phát hiện | Số đo | Hệ quả token |
|---|---|---|---|
| 1 | **Context nạp mỗi phiên Mike ~199KB** (≈55-60K token): `context_pack.md` **78KB** (09-24: 47KB → +65%/14 ngày), `coding_guidelines.md` 41KB, `MIKE.md` 31KB, 2 CLAUDE.md 26KB, memory 24KB | 20 phiên Discord đang sống, mỗi phiên cold-start trả đủ 199KB; phiên này đã ~670K token | `context_pack` vượt ngưỡng OKF 40KB (user mandate 08-19) gần **2×**; `kb_nightly` chỉ WARN ở 45KB, không chặn |
| 2 | **Vòng review lặp cho thay đổi rủi ro thấp**: 66/337 job (20%) là "vòng 2/3/4 / non-blocker / NEEDS_CHANGES". Riêng hôm nay 1 tính năng nhãn cảnh báo (adjfactor AWAITING_TRADE + PRICE_FIELD_MISMATCH, SHADOW, không chạm tiền) tốn **9 dispatch** (r1→r4, rồi r1→r3→chế độ B→NB r1→r2), round-cap bị override 2 lần | 337 job/14 ngày = 24/ngày; Taylor 213 (63%); opus/high 88 (26%) | Mỗi vòng arch-review "hợp lý" (bắt 1-2 gap thật) nhưng tổng vòng không gắn với rủi ro của diff — đúng pattern retro 10-02 đã nêu, chưa giảm |
| 3 | **Cron gọi LLM chạy bất kể có việc hay không**: 16 script; hằng ngày `daily_retro` = **3 job LLM/ngày** (Mike draft → Wags gap → Mike finalize, output 9-17KB/ngày, 27 job Mike trong 14 ngày), `ops_health_check` 2×/ngày + Wags autofix, `kb_nightly` opus/high, `check_report_cadence` effort high | Retro ngày yên tĩnh vẫn đủ 3 bước; người đọc chính của retro là… retro hôm sau | Phí cố định/ngày không phụ thuộc khối lượng sự cố |
| 4 | **Không có telemetry token per-job**: job record có model/effort/turn_cap, KHÔNG có num_turns/cost/cache-hit. Tín hiệu duy nhất là `usage_watch` (% tài khoản) và status `usage_limited` | 17 job usage_limited/14 ngày (13 trong ngày 10-01) ⇒ fleet chạy sát trần, token = công việc bị chặn | Không đo được ⇒ không tối ưu được; audit này cũng phải ước lượng |
| 5 | **`context_pack.md` = `current_ops.md` (37KB) + `canonical.md` (34KB) nối lại**, trong đó ~25KB là tường thuật dự án đã đóng (chuỗi corp-action 09-22→24 ~15KB, lịch sử pin R3 ~8KB, bug screen ~3KB) — thông tin "đã xong", không đổi hành động phiên sau | 466 commit consolidate/14 ngày (33/ngày) rebuild file này | Trả tiền mỗi phiên cho lịch sử đã khép |

Nhỏ, không khẩn: wakeup MISS 8/14 ngày; hook per-turn nhẹ (session_start 8,9KB, prompt_submit 0,1KB) — tốt, giữ.

## Đề xuất — theo thứ tự lợi/chi phí

1. **Cắt `context_pack` về ≤25KB, chặn cứng 40KB** (1 ngày, Wags + arch-review 1 vòng). Giữ: kill-switch, trading status, feature LIVE mỗi feature 1 dòng + con trỏ, holds, luật user chốt (giữ NGUYÊN mọi ngày/ngưỡng/trạng thái cổng). Chuyển tường thuật vào `kb/projects/<file>.md` với 1 dòng pointer. Bắt buộc reviewer thứ 2 đối chiếu bản nén với nguồn (bài học token-saver: lần nén trước từng đưa 2 lỗi sự thật vào file quyết định). Nâng `kb_nightly` 4.6 từ WARN thành pre-commit block cho `context_pack`/`current_ops`.
2. **Phân bậc review theo rủi ro của diff, ghi vào `dispatch-routing`** (0,5 ngày):
   - Bậc 0 — nhãn alert, docs, selfcheck-only, paper/SHADOW: Taylor tự review + selfcheck, **không arch-review**, sonnet/medium.
   - Bậc 1 — số NAV/báo cáo, pipeline dữ liệu: **tối đa 1 vòng** arch-review; non-blocker ghi vào bus, không dispatch vòng sửa.
   - Bậc 2 — đường đặt lệnh, trading_rules, gate tiền: giữ quy trình đầy đủ hiện nay.
   `DISPATCH_ROUND_CAP_OVERRIDE` chỉ hợp lệ cho bậc 2. Ước lượng: 66 job vòng-lặp → ~25.
3. **Retro theo sự kiện, không theo lịch** (0,5 ngày): `daily_retro` chạy đủ 3 bước chỉ khi ngày đó có ≥1 bus `error`/`question` mới/usage_limited/job fail; ngày yên tĩnh ghi 1 dòng "no-retro" bằng shell, không gọi LLM. Giữ `weekly_ops_audit` làm nơi theo dõi pattern. `check_report_cadence` và `kb_nightly` hạ effort high → medium trừ khi có breach.
4. **Thêm telemetry token vào `dispatch.sh`** (0,5 ngày): `claude -p --output-format json` → ghi `num_turns`, `total_cost_usd`, `input/cache_read tokens` vào job record; `weekly_ops_audit` in bảng chi phí theo agent × topic × bậc. Làm việc này TRƯỚC khi đo hiệu quả của 1-3.
5. **Nghỉ hưu luật**: `coding_guidelines` 31 mục + MIKE.md 8 quy chuẩn, mỗi mục sinh từ 1 sự cố, chưa mục nào bị gỡ. Mục đã có gate cơ học (§15 shellcheck, §16 tz_anchor, §29 diag gate, §8c pin gate) chỉ cần 1 dòng "đã cưỡng chế bằng X" — văn xuôi còn lại chuyển sang `_ext.md`. Review quý.
6. **Đóng phiên Discord idle**: 20 phiên sống cùng thư mục; ccdb đóng phiên idle >24h để lần sau cold-start trên context đã cắt (sau mục 1), thay vì resume phiên đã phồng.

## Ước lượng tổng

Không có telemetry nên chỉ ước: mục 1 giảm ~30% chi phí cold-start mỗi phiên; mục 2 giảm ~12% số job; mục 3 bỏ ~2 job LLM/ngày yên tĩnh. Tổng hợp lý **25-35% token fleet** mà không chạm bất kỳ cổng tiền nào. Con số thật chỉ có sau mục 4 chạy 2 tuần.

## Giữ nguyên, đừng "tối ưu"
Fail-closed trên đường tiền · `bot_execute.py` deterministic · quant-skeptic bắt buộc trước wire bậc 2 · claim-reply nguyên tử · circuit breaker dispatch · 3-rail selfcheck · human-in-the-loop plan duyệt. Đây là phần tạo giá trị; chi phí nằm ở chỗ áp cùng mức đó cho mọi thứ khác.
