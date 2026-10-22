# Patch quyền mua X1, X2, X3, N2, N3 — job Taylor_20261022_022942

User duyệt 22/10/2026 09:27 ICT (thread 1559443521747026040, "Duyệt việc 1, việc 2"). Nguồn thiết kế:
`agents/Taylor/research/lag_rights_audit_20261022/` (REPORT.md, B2_nav_chain.md, B2b_B3_park_exit.md).
**N1 và N4 KHÔNG làm** (N1 chờ user chọn luật entry_date lô quyền; N4 chờ legal-vn).

- Nhánh `feat/lag-rights-patches-20261022` (repo mike), worktree
  `/home/trido/thanhdt/WorkingClaude/wt-lag-rights-patches-20261022`, gốc `27f844f16`. **CHƯA merge.**
- Mỗi patch = 1 commit (hoàn nguyên từng cái bằng `git revert <hash>`; thứ tự revert ngược nếu revert nhiều):

| Patch | Commit | Tệp | Selfcheck mới (×3 TZ: `env -u TZ`, Pacific/Kiritimati, America/New_York) | Mutant |
|---|---|---|---|---|
| X1 | `5ef72c1f7` | `bin/lag_rights_exit_hold.py` (mới), `bin/auto_exit_inject.py`, `bin/auto_exit_inject_selfcheck.py` (stub) | `lag_rights_exit_hold_selfcheck.py` 47/47 | 17/17 killed |
| X3 | `d201f6bc7` | `bin/corp_actions.py` | `corp_actions_skip_unsupported_selfcheck.py` 16/16 | 6/6 |
| X2 | `3698d8d44` | `bin/portfolio_status.py`, `bin/auto_exit_inject.py` | `orphan_lot_blocked_selfcheck.py` 9/9 | 3/3 |
| N3 | `3dce22cf4` | `bin/daily_nav_snapshot.py`, `bin/exdate_frame.py`, `bin/corp_action_broker_detect_selfcheck.py` (stub) | `rights_subscription_qty_selfcheck.py` 36/36 | 12/12 |
| N2 | `6840c070c` | `bin/daily_nav_snapshot.py` | `rights_terp_price_gate_selfcheck.py` 35/35 | 10/10 |

Số dòng (ĐO, `git diff --numstat 27f844f16 HEAD`): 13 tệp, +1797/−8.

## Từng patch — hành vi, ĐO vs SUY LUẬN, rủi ro còn lại

### X1 — auto-exit HOLD lệnh thoát LAG có quyền mua chưa tới GDKHQ
- Nguồn sự kiện: `tav2_bq.corporate_action` (ISS, `issue_method_code="Rights"`, tỉ lệ>0, không huỷ, `public_date ≤ signal_date`).
- Có GDKHQ và `plan_date < GDKHQ` ⇒ không chèn SELL, mã vào `blocked` + alert dedup (lý do cố định). `plan_date ≥ GDKHQ` ⇒ bán bình thường.
- Chưa có ngày (như SCL): HOLD + lý do mang ngày ⇒ **alert mỗi ngày đòi user quyết**. User giải phóng/giữ bằng
  `bin/lag_rights_exit_hold.py --record ... --decision HOLD|SELL --decided-by user --at <ISO có TZ> --source <link>`
  vào `data/lag_rights/exit_ack.json` (validate decided_by=user, at có múi giờ, source khác rỗng, event_hash phải khớp sự kiện HIỆN TẠI trên BQ; ghi atomic + flock). Hash gồm `exright_date` ⇒ vendor điền ngày thì ack cũ tự hết hiệu lực, chuyển sang luật có ngày.
- Lỗi BQ / sổ ack hỏng ⇒ fail-closed HOLD + lỗi thật (§29).
- SELL đã có sẵn trong plan + mã HOLD ⇒ chỉ cảnh báo người duyệt gỡ, KHÔNG tự xoá lệnh.
- **ĐO** (22/10, BQ chỉ đọc, `--check SCL --plan-date 2026-10-23`): SCL ⇒ `HOLD`, "quyền mua 15.38% CHƯA có GDKHQ (công bố 2026-09-08) — CẦN USER QUYẾT", kèm lệnh `--record` có sẵn id `6a0516165b1fb4c98c3ab2a2` hash `b15c13b7b4b9`. `data/lag_rights/` chưa tồn tại (chưa có ack nào).
- Rủi ro còn lại: (a) sự kiện công bố chưa có ngày quá 365 ngày bị coi là bản ghi treo của vendor và bỏ qua (ĐO trong commit X1: 25 dòng P không ngày từ 2022) — nếu một sự kiện thật treo >1 năm sẽ không chặn (SUY LUẬN: hiếm). (b) Chỉ áp cho candidate LAG; BAL không đổi (ngoài phạm vi luật 21/10). (c) Auto-exit gọi BQ thêm 1 query cho candidate LAG; BQ sập ⇒ HOLD mọi candidate LAG có liên quan (chủ ý fail-closed, có cờ).

### X3 — `corp_actions.load_all` không còn sập toàn cục vì record RIGHTS
- Loại chưa hỗ trợ (mọi trạng thái) hoặc record chưa CONFIRMED mà hỏng ⇒ BỎ QUA + stderr nêu id/ticker/lý do + list `skipped`. CONFIRMED loại hỗ trợ mà hỏng ⇒ raise như cũ.
- `data/corp_actions.json` thật KHÔNG bị sửa (không thêm record RIGHTS).
- Rủi ro còn lại: một record RIGHTS ai đó lỡ ghi CONFIRMED sẽ bị bỏ qua có cảnh báo chứ không chặn — đúng thiết kế (loại chưa hỗ trợ không thể dùng để quy KL), nhưng cảnh báo chỉ ở stderr của caller.

### X2 — mã mồ côi (broker qty>0, sổ lô 0 ở mọi book)
- `book_lot_snapshot` trả `blocked` "MỒ CÔI: ..." cho mọi book_label; `auto_exit_inject` ghi MỘT lần (book "*") vào notes + alert dedup.
- **ĐO** (21/10, park_holdings thật, chỉ đọc, trong commit X2): SpaceX/ZaloPay 0 mã mồ côi ⇒ không phát sinh alert mới.
- Rủi ro còn lại: chỉ BÁO, không tự gán lô — lô quyền về sau (N1) vẫn hiện "mồ côi" cho tới khi N1 làm.

### N3 — quyền mua không phải "sự kiện cổ phiếu"; ngày nộp tiền phân loại đúng
- `classify_qty_residual`: loại Rights khỏi `is_share_event` (tỉ lệ quyền mua không "giải thích" cú tăng KL tối cum).
- `classify_rights_subscription` (PURE) + `rights_subscription_check` (I/O): phần dư KL dương = user nộp tiền mua quyền (lệnh tay hợp lệ, luật 21/10 như DRI) CHỈ khi ĐỦ: lệnh khớp=0 trong cửa sổ; Rights chưa huỷ, GDKHQ ≤ asof ≤ GDKHQ+120 ngày; biết giá phát hành; phần dư ≤ floor(KL×tỉ lệ)+1; bước Σ(openQuantity×costPrice) broker = phần dư × giá phát hành (±max(0,5%, 1.000đ)). Lọc account_no (§12). Thiếu 1 bit ⇒ vẫn rc=5 (daily_nav_snapshot) / blocked ⇒ rc=6 (exdate_frame → compute_active_nav), thông điệp nêu vì sao không nhận.
- Bổ sung lần này: `corp_action_broker_detect_selfcheck.py` stub module `daily_nav_snapshot` giả thiếu hàm mới ⇒ **N3 bản lần 1 làm selfcheck này sập AttributeError** (lần 1 chưa chạy nó). Đã thêm stub trả "không phải quyền mua" (squash vào commit N3). Số ca 788/788 = gốc `27f844f16` (ĐO).
- Rủi ro còn lại: (a) ngày nộp tiền mà user CÙNG lúc mua/bán chính mã đó ⇒ không tách được bước giá vốn ⇒ vẫn chặn (cần người). (b) Giả định bước giá vốn ở giá PHÁT HÀNH dựa trên 1 ca đo (MBB 08-28); nếu DNSE ghi giá vốn khác cho đợt khác ⇒ chặn (fail-closed, không sai NAV). (c) Sổ lô/giá vốn verify_account_snapshot chưa có lô quyền (N1).

### N2 — cổng giá tối cum chấp nhận marketPrice ≈ TERP
- `classify_rights_ref_gap` (PURE) + `rights_ref_check` (I/O): khi một mã lệch giá >5% (`mismatched`), tra BQ Rights: chưa huỷ, GDKHQ = phiên giao dịch KẾ TIẾP, tỉ lệ r>0, BIẾT giá phát hành S, và |marketPrice − (P + r·S)/(1+r)| ≤ max(200đ, 0,5%) ⇒ không chặn, **mark giá CUM** (quyền còn gắn với CP hôm nay). Cả đường live và `--from-raw`. Artifact `nav_snapshot_*` ghi `corp_action_gate_v2.rights_ref_confirmed`.
- Thiếu giá phát hành / TERP không khớp / tỉ lệ hỏng / lỗi BQ ⇒ VẪN rc=4, thông điệp thêm "[quyền mua: <lý do>]" (§29). Không có quyền mua ⇒ thông điệp như cũ (ca E5 khẳng định).
- BQ chỉ được gọi khi mã đã lệch >5% (ca E7 khẳng định: không lệch ⇒ không gọi, fetch ném lỗi vẫn rc=0).
- Dung sai **ĐO**: SCL 2025 Close/Price 0,88674 vs TERP lý thuyết 0,88501 (lệch 0,2%, audit B2). Fixture: P=22.200, S=1e11/8e6=12.500, r=0,35714286 ⇒ TERP 19.647, marketPrice 19.650 ⇒ confirm.
- **SUY LUẬN** (chưa đo trên ca quyền mua thật): broker hạ marketPrice về TERP ngay tối cum (audit chỉ đo cho cổ tức tiền DRI/ISS VPB/MBB, 19:07–19:32). Nếu broker KHÔNG hạ ⇒ không lệch ⇒ nhánh này không chạy, hành vi cũ đúng.
- Rủi ro còn lại: (a) snapshot `corp_action_daily` 07:30 KHÔNG mang giá phát hành ⇒ N2 dựa vào BQ `corporate_action` lúc 19:10; BQ sập ⇒ rc=4 như cũ (`nav_sync_retry.sh` retry tới 21:15). (b) Cùng tối có CẢ quyền mua lẫn cổ tức tiền cho một mã ⇒ TERP không tính chân tiền ⇒ rc=4 (fail-closed, cần người). (c) Hằng số `exercise_ratio` vendor là CP mới/CP cũ (0,357 cho 14:5) — cùng cách hiểu với N3 và `rights_issue_alert`; nếu vendor đổi quy ước, cả ba cùng sai chiều fail-closed (TERP không khớp ⇒ chặn).

## Không đổi hành vi LIVE cổ tức tiền / cổ phiếu / thưởng / tách (ĐO — selfcheck cũ giữ nguyên số ca, chạy trên HEAD `6840c070c`, ×3 TZ trừ chỗ ghi)
| Selfcheck | Kết quả |
|---|---|
| `daily_nav_snapshot_from_raw_selfcheck.py` | 83 PASS / 0 FAIL ×3 TZ (gốc N3 HEAD cũng 83) — giữa chừng bắt `except (TypeError, ValueError)` mới của N2 (luật 13y), đã sửa |
| `daily_nav_snapshot_corpaction_error_selfcheck.py` | 7/7 ×3 TZ |
| `exrights_price_basis_selfcheck.py` | 38/38 ×3 TZ |
| `corp_action_broker_detect_selfcheck.py` | 788/788 ×3 TZ (= gốc `27f844f16`) |
| `cash_identity_selfcheck.py` | 348 assertion ×3 TZ |
| `compute_active_nav_broker_fills_selfcheck.py` | ALL PASS ×3 TZ |
| `discretionary_margin_gate_selfcheck.py` | PASS ×3 TZ |
| `nav_scripts_2account_selfcheck.py` | PASS ×3 TZ (SpaceX ≠ ZaloPay, §12) |
| `nav_snapshot_daily_selfcheck.sh` | 51/51 (tự ép `env -u TZ`) |
| `nav_sync_retry_rc_selfcheck.sh` | 8/8 |
| `auto_exit_inject_selfcheck.py` | 113/113 (Test6 tự chạy 3 TZ) |
| Từ commit trước (lần 1, không chạy lại lần này): `dividend_adjusted_return` 347/347, `portfolio_status` PASS, corp_action/exdate/auto_confirm cũ giữ số ca (ghi trong message commit X3/N3) |

Phạm vi §23: `daily_nav_snapshot.py` / `exdate_frame.py` / `corp_actions.py` là lõi dùng chung của chuỗi NAV + corp-action ⇒ quét rộng mọi selfcheck import chúng (`grep -rln daily_nav_snapshot bin/*selfcheck*`). KHÔNG đụng `trading_bot/` (executor/plan/config/brokers), `trading_rules.json`, sizing, trần giá, cron. Selfcheck chạy sandbox `mkdtemp`, `MIKE_BOT_TEST_MODE=1`, không BQ/broker/bus/Discord; kiểm `find -newer` trên `data/`, `mike/state`, `mike/bus` sau khi chạy N2: 0 file bị ghi. Pre-commit xanh, không SKIP.

## N1 sẽ cắm vào thế nào (không bị chặn đường)
- X1 quyết định theo (mã, ngày, sự kiện) — không đọc/sửa sổ lô ⇒ lô quyền thêm vào book LAG đi qua cùng cổng.
- X2: khi N1 ghi lô quyền vào sổ (book LAG, entry_date theo luật user chọn), mã hết "mồ côi" tự nhiên — không cần sửa X2.
- N3: `rights_subscription_check` trả `event_id`, `issue_price`, `subscribed_qty`, `exright_date` — đủ để N1 tạo lô (qty, giá vốn = giá phát hành, entry_date = ngày nộp tiền hoặc kế thừa lô gốc). Điểm cắm: nhánh `rs_ok` trong `exdate_frame.classify_positions` / `daily_nav_snapshot.main`.
- N2 chỉ chạm cổng GIÁ tối cum, độc lập sổ lô.

## Việc cho Mike
1. arch-review mức cao (đường tiền: auto-exit + NAV gate) theo từng commit.
2. Sau merge: chưa cần chạy gì thêm; X1 sẽ đưa SCL vào `blocked` + alert hằng ngày tới khi user ghi ack (HOLD/SELL) hoặc vendor điền GDKHQ.
