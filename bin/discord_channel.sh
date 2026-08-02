#!/usr/bin/env bash
# discord_channel.sh <name-or-id>
#
# Phan giai TEN-Y-NGHIA cua 1 Discord topic -> ID that, doc tu kb/discord_channels.json.
# In ID ra stdout. Ten khong ton tai => exit 1 + liet ke ten hop le ra stderr (FAIL LOUD).
#
# WHY: truoc 2026-08-02, ID Discord duoc viet TRAN o 31 file trong bin/ duoi 8 ten bien khac
# nhau cho CUNG 1 channel. Mot ID tran khong kiem chung duoc — nhin mot chuoi 19 chu so
# khong ai biet tac gia dinh gui Trading Daily hay Trading Report, nen copy-paste sai la im
# lang vinh vien. Day la ly do 4 lan patch ro-ri-cheo-topic truoc deu khong triet de.
# Xem kb/discord_channels.json va bin/discord_id_gate.sh.
#
# ID tran (18-19 chu so) van duoc PASSTHROUGH: dispatch.sh phai truyen lai dung ID da ghim
# tren job record (bus/jobs/<job_id>.json discord_thread_id) — do la ID that cua topic da goi
# viec, khong phai mot ten trong registry.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY="${DISCORD_CHANNELS_REGISTRY:-$ROOT/kb/discord_channels.json}"

key="${1:-}"
if [ -z "$key" ]; then
  echo "usage: discord_channel.sh <name-or-id>" >&2
  exit 2
fi

# Passthrough cho ID that (snowflake 17-20 chu so).
if [[ "$key" =~ ^[0-9]{17,20}$ ]]; then
  printf '%s' "$key"
  exit 0
fi

python3 - "$REGISTRY" "$key" <<'PY'
import json, sys
registry_path, key = sys.argv[1], sys.argv[2]
try:
    with open(registry_path, encoding="utf-8") as fh:
        channels = json.load(fh)["channels"]
except Exception as e:                                    # registry mat/hong => fail loud
    print(f"discord_channel: khong doc duoc registry {registry_path}: {e}", file=sys.stderr)
    sys.exit(1)
entry = channels.get(key)
if entry is None:
    print(f"discord_channel: KHONG CO channel ten '{key}' trong {registry_path}", file=sys.stderr)
    print("  ten hop le: " + ", ".join(sorted(channels)), file=sys.stderr)
    sys.exit(1)
sys.stdout.write(entry["id"])
PY
