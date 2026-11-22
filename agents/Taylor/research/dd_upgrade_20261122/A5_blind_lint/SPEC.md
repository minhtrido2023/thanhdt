# A5 — `bin/dd_blind_lint.py` (Taylor sonnet/medium dựng đúng đặc tả; user đã duyệt kế hoạch 22/11 19:07, mục A5 của `kb/projects/dd-upgrade-final-action-20261122.md`)

Việc: script lint kiểm brief/fact-pack giao cho agent đọc ngành / định giá MÙ không chứa token rò giá/mã. CHỈ chế độ cảnh báo + rc, CHƯA nối vào dispatch.sh (nối sau khi có số báo giả — Mike làm).

LÀM TRONG WORKTREE RIÊNG `/home/trido/thanhdt/wt-dd-a5` (nhánh session/1574033826936660078-a5, từ master). Commit ở đó, KHÔNG merge master. Không đụng `kb/dd_price_zones.json`, dispatch.sh, ~/.claude/**.

## CLI
`python3 bin/dd_blind_lint.py <file> [<file>...] [--ticker MÃ --ticker MÃ2] [--mode sector|valuation|skeptic] [--json]`
- rc=0 sạch; rc=1 có vi phạm (in từng dòng `file:dòng: LOẠI: đoạn trích`); rc=2 lỗi dùng/không đọc được file.
- `--ticker`: mã cụ thể phải không xuất hiện (khớp ranh giới từ, không phân biệt hoa/thường). Không truyền ⇒ chỉ kiểm theo loại dưới đây, cộng danh sách mã trong `kb/dd_price_zones.json` (36 mã) ở chế độ `sector` (đọc ngành phải không nhắc BẤT KỲ mã nào của sổ — trừ khi mã đó là từ thường tiếng Việt: nêu & xử lý ca "VIC/HAG/..."? dùng ranh giới từ + chữ HOA bắt buộc để giảm báo giả).
## Loại vi phạm (mỗi loại một mã lỗi chuỗi)
1. `PRICE_TOKEN` — giá cổ phiếu dạng "giá 71.000", "71.000đ", "71k", "55,0–66,7k" gắn ngữ cảnh giá/vùng/tâm/target/mục tiêu (regex có ngữ cảnh, KHÔNG báo mọi số).
2. `MULTIPLE` — P/E, PE, P/B, PB, EV/EBITDA kèm số ("PE 14,2", "P/E 12x") hoặc cột bảng tên P/E|P/B có giá trị.
3. `MARKET_CAP` — "vốn hoá", "market cap" kèm số; "tỷ đồng vốn hoá".
4. `TICKER` — theo `--ticker` hoặc 36 mã sổ ở mode sector (chữ HOA 3–4 ký tự, ranh giới từ).
5. `PATH_LEAK` — đường dẫn chứa mã: `dd_<MÃ>_...`, `<MÃ>_DD_`, `dd_blind_<MÃ>` (đúng ca F7: sector read 22/11 trích `…/dd_VLB_20261122/macro_snapshot…` trong khi khai không biết mã).
6. `FORWARD_RETURN` — "forward return", "lợi suất kỳ vọng", "profit_2W/1M", "kỳ vọng +x%".
7. `VERDICT_LEAK` (chỉ mode sector/valuation) — "rẻ", "đắt", "QUALIFY", "CONFIRMED", "REFUTED", "khuyến nghị mua/bán", nhãn vùng giá.
- Mỗi vi phạm có cờ ngoại lệ dòng: dòng chứa `<!-- blind-ok: lý do -->` được bỏ qua và liệt kê ở cuối ("miễn: n").
- Dùng `kb/dd_price_zones.json` chỉ để lấy danh sách mã (đọc, không ghi).
## Test (bin/dd_blind_lint_selfcheck.py, rc 0 = PASS; dưới `env -u TZ` và TZ lạ)
- Bộ ca dương + âm tự dựng; mutation: tắt từng loại phải làm ít nhất 1 ca fail.
- THỬ TRÊN 10 BRIEF CŨ thật (liệt kê đường dẫn): brief PAT lượt 1–2 (`agents/Taylor/research/dd_PAT_20261114/brief.md`, `brief_r2.md`) PHẢI bị bắt (có giá/cột PE); ít nhất 6 brief/sector-read/fact-pack khác (`agents/Taylor/research/dd_*/brief*.md`, `kb/data_registry/market-state/sector_read_*_*.md` — sector_read VLB 22/11 phải bị bắt PATH_LEAK) và báo: số brief sạch bị báo giả. Mục tiêu: 0 báo giả trên brief sạch; nếu có, liệt kê từng ca + chỉnh regex hoặc giải thích. Ghi bảng vào `agents/Taylor/research/dd_upgrade_20261122/A5_blind_lint/TRIAL_REPORT.md` (mỗi file: bị bắt gì / sạch / có đáng báo không, đánh giá thủ công 1 dòng).
## Nghiệm thu: output thô selfcheck rc ×2 TZ, TRIAL_REPORT.md, hash commit. Hằng tắt: `MIKE_BLIND_LINT=off` ⇒ rc=0 + in cảnh báo (cho wiring sau). pre-commit có ruff ratchet/tz gate: chmod +x, không import thừa, không `datetime.now()` trần. Ghi bus finding khi xong. KHÔNG gửi email.
