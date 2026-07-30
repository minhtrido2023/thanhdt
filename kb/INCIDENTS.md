# Incidents — ĐÃ CHUYỂN SANG CẤU TRÚC OKF

> **File này giờ là STUB REDIRECT.** (2026-07-30, job Winston_20260730_144031)

Sổ postmortem của fleet (trước đây 1 file 408KB, 69 entry) đã được migrate sang cấu trúc chuẩn
mở **OKF** (Open Knowledge Format: markdown + YAML frontmatter tối giản, 1 sự cố = 1 file) tại:

## 👉 [`kb/incidents/`](incidents/) — bắt đầu ở [`incidents/index.md`](incidents/index.md)

- 1 sự cố = **1 file `.md`**, tên `YYYY-MM-DD-<topic>.md`, nhóm theo tháng:
  [`incidents/2026-07/`](incidents/2026-07/), [`incidents/2026-06/`](incidents/2026-06/).
- Entry **RETRO** hằng ngày (digest tổng hợp cả ngày) tách riêng:
  [`incidents/retro/retro-YYYY-MM-DD.md`](incidents/retro/).
- Mục "Open / not-yet-hardened" (việc còn hở, không gắn 1 sự cố cụ thể):
  [`incidents/_open-not-yet-hardened.md`](incidents/_open-not-yet-hardened.md).
- Quy tắc "khi nào ghi entry" + format entry giữ NGUYÊN VĂN trong `incidents/index.md`.

**Grep vẫn hoạt động** (thay 1 file bằng 1 thư mục, thêm `-r`):

```bash
grep -rn "loanPackageId" mike/kb/incidents/     # theo từ khoá
ls mike/kb/incidents/2026-07/ | grep 2026-07-06 # theo ngày
python3 mike/bin/incident_lookup.py "<label>" "<details>"   # tra tự động theo từ khoá
```

**Ghi entry mới:** tạo file mới trong `incidents/<YYYY-MM>/` (hoặc `incidents/retro/` với RETRO)
rồi thêm 1 dòng vào bảng trong `incidents/index.md` — **đừng append vào file STUB này**.

File STUB giữ lại (KHÔNG xoá) để mọi trích dẫn cũ `kb/INCIDENTS.md` rải rác trong code comment,
báo cáo nghiên cứu và KB lịch sử vẫn có nơi để đi tới.
