#!/usr/bin/env python3
"""kb_hot_size_gate.py — pre-commit gate: kb/current_ops.md + kb/canonical.md không được phình.

VÌ SAO: hai file này được publish_context.sh dán NGUYÊN vào kb/context_pack.md, nạp vào MỌI
phiên Mike (~20 phiên Discord) qua @-import. 2026-10-08 context_pack đã 78KB (current_ops 37KB +
canonical 34KB) — tường thuật dự án đã đóng/đã LIVE tích dần vì không có gì chặn lúc commit
(kb_nightly chỉ cảnh báo sau sự việc). Job Wags_20261008_133659, user duyệt 08/10.

LUẬT (đo trên nội dung ĐANG STAGE, không phải working tree):
  tổng byte 2 file > LIMIT (30000)  VÀ  tổng > tổng ở HEAD  ⇒ BLOCK.
Vế "> HEAD" là RATCHET có chủ đích: ngày bật gate, sàn thật sau khi chỉ DI CHUYỂN (không viết lại
sự thật, giữ mọi trạng thái/cổng/mục CÒN MỞ) là ~39KB > 30000. Một ngưỡng tuyệt đối sẽ chặn MỌI
commit chạm 2 file tới khi user quyết phần nào được rời hot path — tức là ai cũng phải lách,
gate thành vô nghĩa. Ratchet: đang vượt thì commit chỉ được giữ nguyên hoặc GIẢM; dưới ngưỡng
thì là ngưỡng tuyệt đối thường.

Bỏ qua: MIKE_KB_SIZE_GATE=warn (in cảnh báo, không chặn — consolidate.sh/kb_nightly.sh dùng cho
commit tự động: cron KHÔNG được fail) · =off · SKIP=kb-hot-size-gate (cơ chế pre-commit).

⚠️ PHẠM VI THẬT: gate chỉ CHẶN commit TAY. consolidate.sh/kb_nightly.sh/fleet_backup.sh commit ở chế độ
warn, nên nội dung đã vượt ngưỡng trong working tree vẫn được cron commit lại trong vòng ~1 giờ ⇒ với
thay đổi chưa commit, gate là NHẮC NHỞ, không phải hàng rào. Hàng rào thật là kb_nightly Phase 4.6
(cảnh báo pack >45KB) + người sửa tôn trọng thông báo chặn.
"""
import os
import subprocess
import sys

LIMIT = 30000
FILES = ("kb/current_ops.md", "kb/canonical.md")


def _size(spec):
    """Byte size of a git object spec (':path' = index, 'HEAD:path'); 0 if absent."""
    r = subprocess.run(["git", "cat-file", "-s", spec], capture_output=True, text=True)
    if r.returncode != 0:
        return 0
    return int(r.stdout.strip())


def main():
    mode = os.environ.get("MIKE_KB_SIZE_GATE", "block")
    if mode == "off":
        return 0
    staged = {f: _size(":" + f) for f in FILES}
    head = {f: _size("HEAD:" + f) for f in FILES}
    st, hd = sum(staged.values()), sum(head.values())
    if st <= LIMIT or st <= hd:
        if st > LIMIT:
            print(f"kb-hot-size-gate: {st} byte > {LIMIT} nhưng không tăng so với HEAD ({hd}) — cho qua (ratchet).")
        return 0
    detail = ", ".join(f"{f}={staged[f]}" for f in FILES)
    msg = (
        f"⛔ kb-hot-size-gate: {detail} ⇒ tổng {st} byte > {LIMIT} và TĂNG so với HEAD ({hd}, +{st - hd}).\n"
        "Hai file này nạp vào MỌI phiên Mike qua kb/context_pack.md. Cách sửa (không viết lại sự thật):\n"
        "  1. Chuyển NGUYÊN VĂN phần tường thuật dự án ĐÃ ĐÓNG/đã LIVE (diễn biến, vòng review, số\n"
        "     SUPERSEDED, bằng chứng) sang kb/projects/<slug>.md (có sẵn thì append), để lại 1 dòng pointer.\n"
        "  2. GIỮ trong file gốc mọi thứ đổi hành động phiên sau: kill-switch, trạng thái LIVE/cổng,\n"
        "     ngày/ngưỡng, câu KHÔNG/CẤM, mục CÒN MỞ/CHƯA vá/CẦN USER.\n"
        "  3. Kiểm: python3 bin/kb_move_verify.py --base HEAD  (mọi dòng bị xoá phải có nguyên văn ở kb/projects).\n"
        "Bỏ qua 1 lần (phải nêu lý do trong commit message): MIKE_KB_SIZE_GATE=warn git commit ..."
    )
    if mode == "warn":
        print(msg.replace("⛔", "⚠️ (warn, không chặn)"))
        return 0
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
