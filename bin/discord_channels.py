"""Phan giai ten-y-nghia Discord topic -> ID that (ban Python cua bin/discord_channel.sh).

Nguon su that duy nhat: kb/discord_channels.json. KHONG viet ID tran o bat ky file .py nao
trong bin/ — bin/discord_id_gate.sh (pre-commit) chan viec do.

    from discord_channels import resolve
    resolve("trading_daily")       -> ID that cua Trading Daily
    resolve("<id-19-chu-so>")     -> passthrough (ID that, vd doc tu job record)
    resolve("khong_ton_tai")   -> raise KeyError (FAIL LOUD, khong doan bua)
"""
import json
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.environ.get(
    "DISCORD_CHANNELS_REGISTRY", os.path.join(_ROOT, "kb", "discord_channels.json")
)
_SNOWFLAKE = re.compile(r"^[0-9]{17,20}$")


def _load():
    with open(REGISTRY_PATH, encoding="utf-8") as fh:
        return json.load(fh)["channels"]


def resolve(name_or_id):
    """Tra ve ID that. ID tran duoc passthrough; ten khong co trong registry -> KeyError."""
    key = str(name_or_id)
    if _SNOWFLAKE.match(key):
        return key
    channels = _load()
    if key not in channels:
        raise KeyError(
            f"discord_channels: khong co channel ten {key!r} trong {REGISTRY_PATH}; "
            f"ten hop le: {', '.join(sorted(channels))}"
        )
    return channels[key]["id"]
