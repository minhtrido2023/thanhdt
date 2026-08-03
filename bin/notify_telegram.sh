#!/usr/bin/env bash
# notify_telegram.sh "<message>" — gửi 1 tin nhắn qua Telegram Bot API.
#
# VÌ SAO TỒN TẠI (2026-08-03, vòng 6 arch-reviewer, sự cố registry 2026-08-02): MỌI đường báo
# hiện có của fleet — `notify_thread.sh` (TÊN → `discord_channel.sh` → `kb/discord_channels.json`)
# và `notify.sh` → `notify_discord.sh` — cuối cùng đều đi qua CÙNG bridge `127.0.0.1:8199` và
# CÙNG registry. Registry hỏng ⇒ CẢ HAI câm cùng lúc. Đó chính là ca đã xảy ra thật 2026-08-02.
# Đây là đường THỨ HAI thật sự độc lập: HTTPS thẳng tới api.telegram.org, không bridge, không
# registry, credential riêng. Không phải đường chính — chỉ dùng khi Discord ĐÃ thất bại.
#
# KHÔNG phải cơ chế mới: `secrets/telegram_config.json` +
# `telegram_recommend.send_telegram_text` đã chạy production ở ~15 script (bot_execute.py,
# macro_healthcheck.py, crisis_alert_push.py, risk_monitor.py…). Script này chỉ bọc lại cho
# tầng bash gọi được, cố ý KHÔNG tự định nghĩa lại cách gửi.
#
# Exit: 0 = Telegram xác nhận ok. Khác 0 = thiếu credential / API từ chối / lỗi mạng — caller
# PHẢI xử lý (đừng bọc `|| true`: đây đã là đường dự phòng cuối, nuốt lỗi ở đây = im lặng hoàn
# toàn, đúng thứ nó sinh ra để chống).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"

msg="${1:?usage: notify_telegram.sh \"<message>\"}"

python3 - "$WC_ROOT" "$msg" << 'PY'
import json, os, sys

wc_root, message = sys.argv[1], sys.argv[2]
cfg_path = os.environ.get("TELEGRAM_CONFIG") or os.path.join(
    wc_root, "secrets", "telegram_config.json")

try:
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
except OSError as e:
    print(f"notify_telegram: không đọc được {cfg_path}: {e}", file=sys.stderr)
    sys.exit(2)

sys.path.insert(0, wc_root)
from telegram_recommend import send_telegram_text  # noqa: E402

# parse_mode="" — tin vận hành là văn bản thô có ký tự Markdown/HTML tự do (`**`, `<`, `_`);
# để parse_mode mặc định HTML thì Telegram trả 400 và tin RƠI. Cùng lý do bot_execute.py:78.
LIMIT = 4000  # dưới trần 4096 của Telegram, chừa chỗ cho tiền tố
pieces = [message[i:i + LIMIT] for i in range(0, len(message), LIMIT)] or [""]
rc = 0
for i, piece in enumerate(pieces, 1):
    body = f"[{i}/{len(pieces)}]\n{piece}" if len(pieces) > 1 else piece
    try:
        res = send_telegram_text(cfg["bot_token"], cfg["chat_id"], body, parse_mode="")
    except Exception as e:  # requests lỗi mạng / thiếu key trong config
        print(f"notify_telegram: gửi thất bại: {e}", file=sys.stderr)
        sys.exit(1)
    # send_telegram_text KHÔNG raise khi Telegram từ chối (chỉ in WARNING) — phải tự kiểm 'ok',
    # nếu không script này báo thành công cho một tin chưa bao giờ tới.
    if not (isinstance(res, dict) and res.get("ok")):
        print(f"notify_telegram: Telegram từ chối: {res}", file=sys.stderr)
        rc = 1
sys.exit(rc)
PY
