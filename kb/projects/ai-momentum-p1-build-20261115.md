# AI momentum — P1 BUILD (2026-11-15, Taylor, job `Taylor_20261115_154607`)
Nhánh `research/ai-momentum-p1-20261115` (worktree `agents/Taylor/wt-ai-momentum-p1`), KHÔNG merge main. Chưa cài cron, chưa chạy forward, không tiền/lệnh/plan.
Bổ sung `ai-momentum-p0-result-20261115.md`. Artifact: `agents/Taylor/research/ai_momentum_20261115/`; md5 trong `PREREG_v2.md5`.

## 1. Power với view có hướng (việc 1) — `power_sim_directional.py/.out`
Killer objection quant-skeptic xác nhận ĐÚNG hướng: N phải đếm sự kiện CÓ view có hướng. Với p_dir=0,4 (M1 dry-run: NO_VIEW 5/10 @20s; **mẫu 10, thô**):
- Power T1/ex20 (nhóm A=CONT vs phần còn lại; p hoán vị khối tháng; α=0,05/3): N_dir=80 → 0,75 (Δ8pp) / 0,98 (Δ12pp); N_dir=150 → 0,99 / 1,00; N_dir=40 → 0,35 / 0,60.
- **Thời gian tới N_dir** (÷ nhịp×0,4): 80 → 15,2 th (nhịp TB 13,2/th) hoặc 31,7 th (6 th gần: 6,3/th); 150 → 28,4 hoặc 59,5 th; nới ngưỡng ×2: 150 → 17,4 th (21,5/th) hoặc 30,5 th (12,3/th).
- **Kết luận thẳng**: ở ngưỡng v1 + nhịp gần đây, trần 24 tháng kết thúc ở N_scored≈150, N_dir≈60 — chưa tới L1 ⇒ **gần chắc chắn "không kết luận"**. Mô hình lạc quan (view độc lập outcome, CONT 50%).
- ⚠️ Retro P1 (2 sự kiện HII, VNZ, gói đã lọc ingested_at): cả 2 NO_VIEW@20s (P0, gói có tin, HII là CONT) ⇒ p_dir có thể **thấp hơn 40%** khi tin thưa. Chưa đo trên mẫu lớn.

## 2. Canary (việc 2) — `canary/canary_raw.jsonl`
Raw P0 **không còn** ⇒ 0/10 của P0 không kiểm toán lại được (nói thẳng). Chạy LẠI ở P1 (khác raw P0): **0/10 rò**, nhưng 10/10 UNKNOWN (model không dám đoán ⇒ canary yếu). README trong thư mục.

## 3. Prompt/schema/packet (việc 3) — PREREG_v2.md
Khoá `claim/source/date`, `additionalProperties:false`, `event_id` tuỳ chọn; gói thêm `sector_context`; tin lọc `DATE(ingested_at,'Asia/Ho_Chi_Minh') ≤ T` + log `public_date`/`ingested_date`. 
**Hệ quả đo**: 98,8% stock_news nạp 2026-09-13 (backfill) ⇒ gói retro T<09-13 gần như không có tin (`n_news=0` cả 2 sự kiện thử) — retro chỉ gỡ quy trình, không đại diện live. Chạy thật 2 sự kiện retro với prompt v2: 0 lỗi schema (trước khi bỏ `event_id` khỏi required: 2/2 lỗi lần đầu).

## 4. `ai_momentum_daily.py` (việc 4)
PIT (SQL chỉ ≤T, `universe_pit` rv1, rating as-of ≤T ghi `rating_read_at`), cooldown greedy (sổ + `events.csv` R4), hàng đợi 10/tuần ISO nhân quả (ghi `skipped_capacity`), JSONL append-only md5/dòng + flock + idempotent (chạy lại không gọi lại M1), live chỉ T==hôm nay ICT (ngày bù → ledger retro), `--dry-run`, `--date`, `--score`. Scorer giữa look chỉ in N/N_dir/G-proc.
- **Đối chiếu SQL sự kiện với `events.csv` P0** (dry-run thật trên BQ, T=2026-11-13/10-12/09-21/08-05): khớp 4/4 (CTD; DXP; APH; HII+VNZ).
- **Chi phí/token M1 phiên trần (đo thật, 2 sự kiện)**: 1 lần gọi/sự kiện, in 2.419 / 2.423 token (tạo cache 2.417 / 1.295 + đọc 0/1.126), out 802 / 734, **$0,0177 / $0,0126** ⇒ ~3,2k token/sự kiện so với 75,8–76,9k của agent P0 (**−96%**). Chưa đo: vòng phản biện, live có WebSearch. Ước lượng (nhãn): ≤1,4 sự kiện/ngày × ~$0,03 ⇒ <$0,5/ngày ≪ trần $15.
- Cách cắt token: `claude -p --model sonnet --effort medium --setting-sources "" --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --system-prompt <prompt> --tools "" --no-session-persistence`, cwd tmp rỗng. (`--bare` thử và loại: "Not logged in" — cần API key.)
- **Selfcheck** `selfcheck_ai_momentum.py`: 24 test + 22 mutant trên chính source (fake BQ/M1/M2, không mạng) — **24/24 PASS, 22/22 mutant bị bắt, dưới 3 TZ** (`env -u TZ` / `TZ=UTC` / `TZ=America/New_York`; output `selfcheck_output_*.txt`). Máy host mặc định UTC nên `-u TZ` ≡ UTC; NY mới phân biệt. Phủ: không double-append (ledger + run_day + song song 6 tiến trình), sửa tay → md5 báo, không lộ outcome (khoá cấm + SQL không LEAD/profit_/ticker_prune), tin nạp sau T bị loại, M2 raise/FAIL ⇒ `m2_status=FAIL` fail-open, schema sai tên khoá ⇒ `m1_status=FAIL`, hàng đợi/cooldown/reset tuần, live-guard, dry-run không ghi, scorer không peek, neo ICT.
  Mutant từng SỐNG sót ban đầu (lộ test yếu: idempotent bị che bởi guard thứ 2; flock không bắt được race; cooldown 90→0 vì quy tắc quý che) → thêm test trực tiếp; nay bắt hết.

## 5. M2 (việc 5)
`m2_adapter()` fail-open (`adapter_not_enabled`), KHÔNG đụng `second_opinion.sh`. Bật bằng thân hàm khi Wags xong. Chưa kiểm chứng M2 thật ⇒ **chưa có flip_rate/κ/T3**.

## 6. PREREG v2 (việc 6)
`PREREG_v2.md`: 7 thay đổi + lý do, không đổi ngưỡng sự kiện. **Đề xuất cho USER (không tự làm)**: nới ngưỡng ×2 là điều kiện thực tế để FINAL khả thi (~12–20 tháng thay vì không bao giờ); phải quyết trước khi chạy forward (sẽ thành v3).

## Cảnh báo còn tồn
1. Quyết định nới ngưỡng ×2 hay chấp nhận "không kết luận" — chưa có.
2. M2 chưa sống (chờ Wags); forward chạy trước đó sẽ không có T3.
3. `--score` chưa chạy trên dữ liệu thật (ledger rỗng); `fetch_outcomes` SQL chưa test BQ (chỉ unit-test phần thuần).
4. Cron/ngày nghỉ: script thoát rc≠0 khi BQ chưa tới T (cuối tuần/lễ, trước sync 23:45) — wrapper cron phải coi đó là "không có phiên", không alert.
5. Ledger mặc định `mike/data/ai_momentum/` (chưa tạo, chưa gitignore) — Mike quyết nơi lưu/backup khi merge.
6. `ai_momentum_daily.py` md5 trong `PREREG_v2.md5` là bản lúc commit; sửa code sau đó phải ghi chú (prompt/schema mới là phần khoá).
7. fa_ratings_8l republish định kỳ (as-of hồi tố có thể lệch) — live ghi rating đọc tại T (PIT thật).
quant-skeptic chưa gọi trên bản P1.
