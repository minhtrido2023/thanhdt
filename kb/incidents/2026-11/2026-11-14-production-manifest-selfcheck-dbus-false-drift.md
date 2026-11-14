# 2026-11-14 — `production_manifest_selfcheck.sh` FAIL giả dưới cron/headless: file chỉ có gốc systemd bị coi "rời production"

**Phát hiện:** weekly ops audit 14/11 (job `Mike_20261114_075225`), mục 8 — selfcheck báo `DRIFT 2 dòng`:
`mike/bin/work_tree_server.py`, `mike/bin/work_tree_tunnel.sh` "(rời production)". Hai unit `mike-work-tree*.service`
vẫn `active`+`enabled` (đọc thật `systemctl --user`).

**Tái hiện:** cùng commit, có `XDG_RUNTIME_DIR` ⇒ `OK manifest khớp (752 file, units=ok)` PASS; `unset XDG_RUNTIME_DIR
DBUS_SESSION_BUS_ADDRESS` ⇒ FAIL. Nguyên nhân (đọc `diff_manifests`): luật "gốc systemd chỉ so khi CẢ HAI bản đọc được
systemd" áp cho `roots` nhưng KHÔNG áp cho `files` ⇒ không D-Bus thì file có gốc duy nhất là unit biến mất khỏi bản mới.

**Sửa (`47430907b`):** khi `units_status` một bên ≠ `ok`, loại khỏi phép so các file mà MỌI gốc đều là `unit …`.
**Verify:** PASS cả 2 môi trường; probe đối kháng: units=ok + xoá `work_tree_server.py` ⇒ vẫn báo `- … (rời production)`;
không D-Bus + xoá `fleet_backup.sh` (gốc cron) ⇒ vẫn báo. Không đụng manifest commit.

**Cùng lượt — 3 selfcheck rc=124 GIẢ (trần offline 60s của `run_selfchecks.sh`):** đo tay annualization_basis 60s PASS,
book_clearing_g3 228s PASS, report_gate_quarterly 142s rc=0 ⇒ thêm budget đo thật (240/480/300) theo đúng mẫu các
ngoại lệ đã có trong runner.
