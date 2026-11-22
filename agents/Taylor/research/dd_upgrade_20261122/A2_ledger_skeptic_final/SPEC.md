# A2 — Sổ giá DD: thêm skeptic_final + skeptic_verdict_path + audited_fy_missing (đặc tả; Taylor sonnet/medium dựng, KHÔNG thiết kế lại)

Nguồn kế hoạch (user đã duyệt, decided_by user 22/11 19:07): `kb/projects/dd-upgrade-final-action-20261122.md` mục A2. Số nền: `kb/projects/dd-baseline-20261122.json`.

LÀM VIỆC TRONG WORKTREE `/home/trido/thanhdt/wt-1574033826936660078` (nhánh session/1574033826936660078; chạy `git merge --ff-only master` hoặc `git merge master` trước tiên). KHÔNG sửa trực tiếp `/home/trido/thanhdt/WorkingClaude/mike` (master). Commit trong worktree, KHÔNG merge vào master (Mike sẽ merge sau arch-review). Chạy selfcheck bằng đường dẫn tuyệt đối tới script TRONG worktree với `--ledger <worktree>/kb/dd_price_zones.json`; nguồn research (untracked) nằm ở canonical nên giữ `MIKE_SRC_ROOT` mặc định. Chạy mọi selfcheck dưới `env -u TZ` VÀ `TZ=Pacific/Kiritimati`.

## Trường mới (mỗi entry của `entries[]`)
- `skeptic_final`: enum 4 giá trị, KHÁC nhau theo nghĩa:
  - `CONFIRMED` — vòng skeptic CUỐI ghi CONFIRMED (không REFUTED/INCONCLUSIVE) VÀ sau đó không có đính chính số/vùng nào.
  - `FIXED_UNVERIFIED` — đã có REFUTED/INCONCLUSIVE (hoặc đính chính sau CONFIRMED) và bản sửa đã áp, nhưng chưa có vòng skeptic nào chạy lại trên bản sửa.
  - `REFUTED_OPEN` — REFUTED/INCONCLUSIVE mà bản sửa CHƯA áp (hoặc văn bản nói rõ còn mở).
  - `NONE` — chưa qua skeptic ("CHƯA qua skeptic", "CHƯA chạy fundamental-skeptic").
- `skeptic_verdict_path`: đường dẫn (tương đối repo mike) tới file verdict của vòng cuối, hoặc `null` (cho phép null với entry cũ — chỉ 19/58 thư mục dd_* có file tên skeptic/verdict). Nếu entry có file `SKEPTIC*.md`/`skeptic/` trong thư mục nguồn của nó thì điền đường dẫn thật (kiểm file tồn tại), không đoán.
- `audited_fy_missing`: bool; `true` khi thiếu BCTC năm GẦN NHẤT đã kiểm toán (hiện biết: VLB; tra `skeptic_status`/`notes` từng entry tìm "thiếu BCTC 2025 KT" hoặc tương tự; không chắc ⇒ để false và liệt kê vào danh sách mơ hồ).

## Backfill (script chỉ-thêm-trường, idempotent, chạy lại ra y kết quả): `bin/dd_ledger_backfill_skeptic_final.py`
- Chỉ ghi các trường mới vào MỌI entry hiện có (95 entry). Với entry KHÔNG phải rev cuối của mã: suy theo cùng luật từ `skeptic_status` của chính nó. KHÔNG sửa bất kỳ trường cũ nào; sổ append-only ⇒ diff phải chỉ là dòng thêm.
- Luật cố định đọc `skeptic_status` (+ `notes`, `correction_reason`) theo thứ tự: NONE nếu chứa "CHƯA qua skeptic"/"CHƯA chạy fundamental-skeptic"; nếu text nói bản sửa/đính chính đã áp (vd "REFUTED-đã-áp", "đã áp", "đính chính") ⇒ FIXED_UNVERIFIED trừ khi có vòng sau ghi rõ CONFIRMED trên bản đã sửa ("lần cuối CONFIRMED", "r3/r4 ... CONFIRMED" mà không có đính chính số sau đó) ⇒ CONFIRMED; REFUTED/INCONCLUSIVE không nói đã áp ⇒ REFUTED_OPEN; chỉ có "CONFIRMED" ⇒ CONFIRMED; không match gì ⇒ KHÔNG gán — ghi vào danh sách MƠ HỒ.
- TUYỆT ĐỐI không tự gán CONFIRMED cho ca mơ hồ. Ghi `skeptic_final` = null cho ca mơ hồ?? KHÔNG — selfcheck sẽ đòi enum; thay vào đó gán `FIXED_UNVERIFIED` (an toàn) cho ca mơ hồ và đánh dấu `skeptic_final_basis: "ambiguous_backfill"` trên entry đó; Mike xác nhận tay sau. Mọi entry khác ghi `skeptic_final_basis: "rule_backfill_20261122"`.
- In ra: bảng đếm (rev-cuối-mỗi-mã: CONFIRMED / FIXED_UNVERIFIED / REFUTED_OPEN / NONE) và danh sách từng mã mơ hồ kèm trích dẫn nguyên văn `skeptic_status`. Mong đợi tham chiếu (baseline): rev cuối CONFIRMED-nhãn 19, REFUTED-nhãn 16, khác 1; review ghi 20/16. LỆCH ⇒ liệt kê TỪNG mã lệch, không ép khớp. Đặc biệt phải nêu rõ PNJ, PAT, QTP, SZL.

## Cưỡng chế (`bin/dd_price_zones_selfcheck.py`)
- Hằng `SKEPTIC_FINAL_REQUIRED_FROM = "2026-11-23"` (mẫu `LOCK_REQUIRED_FROM`, dòng ~30): entry có `recorded_at` ≥ ngày đó BẮT BUỘC có `skeptic_final` ∈ enum + `audited_fy_missing` kiểu bool; `skeptic_verdict_path` cho phép null (A4 sẽ đóng sau). Entry cũ chỉ bị kiểm nếu CÓ trường (giá trị phải ∈ enum).
- Thêm test đột biến (theo mẫu các dòng "PASS … bị bắt" hiện có): (1) entry mới thiếu skeptic_final bị bắt; (2) enum sai bị bắt; (3) entry cũ thiếu trường được miễn; (4) `audited_fy_missing` không phải bool bị bắt; (5) `skeptic_verdict_path` trỏ file không tồn tại (khác null) bị bắt.
- Chưa nối vào cổng LAG/tiền; hiển thị thôi.

## Hiển thị
- `bin/dd_price_zone_watch.py`: nơi in từng mã ứng viên/dòng mã, thêm nhãn `skeptic_final` + số `rev` (chỉ in thêm, không đổi logic lọc/ngưỡng −15%/xếp hạng). Thêm 1 ca vào `bin/dd_price_zone_watch_selfcheck.py`. Chạy lại watch cho ngày 20/11 (chế độ không gửi tin) và xác nhận danh sách mã không đổi so với trước.

## Nghiệm thu (nộp output THÔ)
1. `env -u TZ python3 bin/dd_price_zones_selfcheck.py --ledger <worktree ledger>` rc=0 + bản chạy `TZ=Pacific/Kiritimati`; số PASS/lỗi 0.
2. `env -u TZ python3 bin/dd_price_zone_watch_selfcheck.py` rc=0.
3. `git diff --stat` + kiểm "chỉ dòng thêm" trên kb/dd_price_zones.json: `git diff -U0 master -- kb/dd_price_zones.json | grep '^-' | grep -v '^---'` phải rỗng (hoặc chỉ dòng dấu phẩy cuối đối tượng — nêu rõ).
4. Bảng đếm backfill + danh sách mơ hồ đầy đủ (PNJ/PAT/QTP/SZL bắt buộc có mặt dù mơ hồ hay không) vào `agents/Taylor/research/dd_upgrade_20261122/A2_ledger_skeptic_final/BACKFILL_REPORT.md`.
5. Commit trong worktree (kèm dòng Co-Authored-By theo quy ước repo), in hash. Ghi bus finding.
Lưu ý repo: pre-commit có cổng `dd-price-zones-gate` (selfcheck), ruff ratchet (script mới cần chmod +x và không import thừa), tz-anchor. Cấm `--no-verify`.
