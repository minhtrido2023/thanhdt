---
kind: incident
date: 2026-07-09
topic: dispatch-hard-timeout-killed-finished-agent
title: >-
  2026-07-09 (tối) — dispatch hard-timeout giết agent ĐÃ XONG VIỆC (lần 2), trước khi nó kịp return — dẫn tới heartbeat-aware deadline
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-09 (tối) — dispatch hard-timeout giết agent ĐÃ XONG VIỆC (lần 2), trước khi nó kịp return — dẫn tới heartbeat-aware deadline

**Phát hiện (Wags, cùng job `Wags_20260709_134401` ở entry ngay trên):** attempt 1 của
job này đã hoàn tất TOÀN BỘ deliverable (fix cgroup, test A/B, commit, finding bus
14:03:36Z, arch-reviewer CONFIRMED 14:09:55Z, notify Architecture topic, đóng working
memory 14:13:58Z) — nhưng bị `dispatch.sh` giết đúng deadline cứng 1800s lúc 14:14:01
(exit 124), **TRƯỚC KHI kịp return**. Job record kẹt `running`; dispatch tự retry spawn
attempt 2 (tốn 1 lần spawn thừa + record kẹt "running" ~30 phút, không mất dữ liệu vì
mọi artifact thật đã ghi xong ở attempt 1).

**Root cause:** deadline trong `dispatch.sh` trước đây là timeout TUYỆT ĐỐI theo đồng hồ
tường (`TIMEOUT` giây kể từ lúc spawn), không tham chiếu heartbeat thật của agent — một
agent còn sống, còn ghi heartbeat đều đặn tới tận giây cuối (HB tươi tới 14:14:06, chỉ
5s sau khi bị giết) vẫn bị giết y như một job treo thật sự. Không phân biệt được
"đang làm việc lâu hơn dự kiến" với "đã chết/treo".

**Tái diễn lần 2** — lần 1: `Winston_20260707_072729` (ops_autofix, deadline 900s), cùng
dạng giết-agent-đang-sống. Cả 2 lần đều do Wags tự phát hiện qua chính công việc của
mình (không phải do user báo).

**Fix (cùng phiên tối 2026-07-09, commit `d3a7282` + cơ chế chính trong `b8f78bd`/
`5446bf2`):** `_hb_aware_timeout` trong `dispatch.sh` — tới hạn `TIMEOUT`, nếu heartbeat
bus CỦA CHÍNH AGENT (không phải ping watcher) còn tươi hơn `DISPATCH_HB_FRESH_S=120s` →
gia hạn thêm 1 chu kỳ, tối đa `DISPATCH_HB_MAX_EXTENSIONS=3` lần (trần tuyệt đối vẫn là
`TIMEOUT×(N+1)`, không loop vô hạn). Đồng thời vá `mike_json.py job-hb-age`: HB_AGE giờ
CHỈ tính event do agent tự ghi, lọc bỏ ping `still_running/source=watcher` — nếu không
lọc, một job treo thật vẫn "tươi" mãi mãi nhờ chính watcher tự ping, vô hiệu hoá toàn bộ
cơ chế phát hiện treo.

**Verify:** e2e 4/4 — (a) alive+hb đều đặn → gia hạn rồi done bình thường (75s>40s
timeout gốc, ext=1); (b) treo thật (không heartbeat) → vẫn chết đúng hạn 90s dù watcher
tự ping "tươi" 30s (đã lọc watcher ping nên không bị đánh lừa); (c) hb-forever (agent
giả vờ sống mãi bằng heartbeat giả) → vẫn chết đúng trần tuyệt đối 92s = 30×3 (chặn
loop-giả-sống-vô-hạn).

**Bài học:** timeout tuyệt đối bảo vệ khỏi job-treo-thật nhưng lại trừng phạt nhầm
job-đang-làm-lâu-nhưng-sống — 2 lần liền cùng 1 dạng lỗi (07-07, 07-09) trước khi được
sửa tận gốc. Cùng nguyên tắc với mục "trust the artifact, self-report" (MIKE.md #2)
nhưng áp cho chính cơ chế giám sát: watcher tự ping không được tính là bằng chứng sống
— chỉ heartbeat DO AGENT TỰ GHI mới đáng tin.
