# 2026-09-12 — `run_selfchecks.sh` quét cả `mike_paseo/`, một ảnh chụp ĐÓNG BĂNG từ 08-28: 84/248 file (34%) và 3/6 FAIL là bản sao chết

**Status**: fixed
**Phát hiện bởi**: weekly ops audit 2026-09-12, job `Mike_20260911_204825` (mục 8 — triage 6 FAIL)
**Ảnh hưởng**: không chạm tiền thật. Nhưng làm hỏng chính thứ selfcheck sinh ra để giữ: **tín hiệu
đỏ đáng tin**. Mỗi lượt quét (hàng ngày qua `selfcheck_weekly_baseline_check.sh` và hàng tuần qua
`weekly_ops_audit.sh`) trả về một sàn 3 FAIL cố định không ai sửa được — vì code sau chúng không
tồn tại trong production.

## Bằng chứng `mike_paseo/` là cây chết

| Kiểm tra | Kết quả |
|---|---|
| `git -C mike_paseo log -1` | `0e29acb8` **2026-08-28**, KB v2611 — trong khi `mike` ở `a3a17ff0`, KB **v2932** (15 ngày, 321 version) |
| File mới nhất trong cây | 4 file "mới" duy nhất là artifact do **chính bộ quét này** ghi ra lúc 03:30 ICT hôm nay (`logs/wake_thread.log`, 2 `out/selfcheck.json`, 1 `.pyc`) |
| Crontab | `crontab -l \| grep -c mike_paseo` = **0** |
| Repo ngoài | user đã thêm `WorkingClaude/mike_paseo/` vào `.gitignore:131` ngày **2026-09-08**, khi vá gitlink treo làm `fleet_backup` FAIL 11 đêm liền |

## Vì sao 3 FAIL đó là ĐỎ ZOMBIE, không phải bug

- `mike_paseo/bin/daily_retro_wake_metrics_selfcheck.sh` — **`mike/` KHÔNG còn file này**: nó đã bị
  RETIRE có chủ đích ở commit `30648b51`, vì khối nó gác đã được gỡ khỏi `daily_retro.sh`
  (`13f7bd59`). Bản sao đông lạnh vẫn đòi trích khối đó ⇒ FAIL vĩnh viễn khi gác một thứ đã chết.
- `mike_paseo/agents/Winston/freshness_warn_selfcheck.py` — `NameError: _ICT`, tức bản 08-28 nằm
  TRƯỚC fix `e5700fbd` (2026-09-05) trong `mike/`.
- `mike_paseo/bin/job_cancel_guard_selfcheck.py` — trùng lặp thuần với bản `mike/`, cùng một
  assertion đỏ (xem dưới), nên chỉ nhân đôi tiếng ồn chứ không thêm thông tin.

## Root cause

`run_selfchecks.sh` lọc theo tiêu chí đã tuyên bố rõ — "không phải production HEAD" — và đã hai lần
được siết theo đúng tiêu chí đó (08-15 bỏ `wt-*`/`pending_*`, 08-22 bỏ `.claude/worktrees/` + 4
harness). `mike_paseo/` khớp y hệt tiêu chí ấy nhưng chưa bao giờ được thêm vào danh sách. Ngược
lại, bản vá 08-29 còn **cố ý** cấp cho bản sao `mike_paseo/` cùng ngân sách timeout (khớp theo hậu
tố) — quyết định hợp lý **lúc đó**, vì khi ấy cây chưa đông lạnh và chưa bị user gitignore. Điều
kiện thay đổi ngày 09-08; bộ lọc thì không.

## Fix

Thêm đúng một dòng vào pipeline dò file của `bin/run_selfchecks.sh`:

```bash
| grep -vE "^\./mike_paseo/" \
```

**Verify bằng chạy thật** (không chỉ đọc lại): `bash bin/run_selfchecks.sh` in ra
`Tìm thấy 164 selfcheck` — đúng 248 − 84, khớp con số đếm được trước khi sửa, và dòng tóm tắt tự
khai `+ mike_paseo/` trong danh sách loại trừ. `bash -n` sạch.

Bộ dò HÀNG NGÀY (`selfcheck_weekly_baseline_check.sh`) **không bị ảnh hưởng**: nó glob hẹp
(`*_selfcheck.*` ở `WC_ROOT` + `mike/bin/`), chưa bao giờ với tới `mike_paseo/`. Đã kiểm, không
phải giả định.

## Ca đỏ CÒN LẠI sau khi lọc — không phải bug production, nhưng là lỗ hổng coverage thật

`mike/bin/job_cancel_guard_selfcheck.py` 262/263, assertion đỏ duy nhất:
`FAIL systemd-run scope path was actually exercised -- systemd-run --user --scope unavailable here`.

Tái hiện: `systemd-run --user --scope true` → `Failed to connect to bus: $DBUS_SESSION_BUS_ADDRESS
and $XDG_RUNTIME_DIR not defined`. Tức là dưới **mọi** ngữ cảnh cron/headless, nhánh systemd-scope
của `dispatch.sh` KHÔNG BAO GIỜ được selfcheck tự động chạm tới. Selfcheck đang nói thật —
"production path UNTESTED on this host" — nên **không được sửa nó thành PASS**. Nhưng để nó đỏ mỗi
ngày thì cũng chính là cơ chế mục rữa mà file này đang nói tới. Chủ sở hữu: **Wags**. Cần một quyết
định có chủ đích (tách tier "cần D-Bus session", hay chạy có điều kiện), không phải im lặng.

## Bài học

Bộ lọc "cái gì là production" là một **khẳng định về thế giới**, và thế giới đổi. Ba lần siết bộ lọc
này (08-15, 08-22, 09-12) đều là cùng một hình dạng: một cây mã sao chép trở nên không-phải-production
*sau* khi bộ lọc được viết. Tín hiệu rẻ nhất để bắt sớm lần sau đã nằm sẵn trong repo mỗi lần:
`git log -1` của cây đó so với `mike`. Bất kỳ thư mục nào chứa selfcheck mà HEAD tụt lại nhiều ngày
so với `mike` thì hoặc phải được đồng bộ, hoặc phải bị loại — không có lựa chọn thứ ba "cứ để đó
cho chắc", vì "cho chắc" ở đây tạo ra chính xác 0 coverage và 3 đỏ vĩnh viễn.
