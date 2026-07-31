#!/usr/bin/env python3
"""selfcheck_capit_episode_gates.py — Bước 4 job Taylor_20260731_034933.

Kiểm tra 2 gate BÁO CÁO đã chuyển sang episode-aware (`capit_signal_today OR capit_episode_open`):
  1. telegram_recommend.build_message()  — khối "CAPIT v2 monitor"
  2. mike/bin/bq_freshness_check.sh      — CAPIT_NOTE bơm vào prompt DollarBill

Kịch bản quan trọng nhất = T2: ĐÚNG tình huống thật hôm nay (07-31) — tín hiệu ngày chạy TẮT
(`capit_signal_today=False`) nhưng vị thế THẬT còn giữ (`capit_episode_open=True`). Trước patch
cả 2 kênh im lặng hoàn toàn (đó là sự cố); sau patch phải hiện "ĐANG GIỮ".

Gate shell được test bằng cách TRÍCH ĐÚNG đoạn code thật ra khỏi bq_freshness_check.sh (sed) rồi
eval trên fixture — không chép lại logic, để test không thể đúng trong khi bản thật sai.
"""
import json
import os
import subprocess
import sys
import tempfile

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
SH = os.path.join(WORKDIR, "mike/bin/bq_freshness_check.sh")
sys.path.insert(0, WORKDIR)

import pandas as pd  # noqa: E402
import telegram_recommend as tr  # noqa: E402

# ── fixtures: 4 trạng thái status.json ───────────────────────────────────────
EP = {
    "capit_episode_open": True,
    "capit_episode_id": "CAPIT-2026-07-20",
    "capit_episode_entry_date": "2026-07-20",
    "capit_episode_basket": ["NCT", "PVT", "SAB", "SIP", "VNM"],
    "capit_episode_size": 0.75,
    "capit_sessions_held": 8,
    "capit_episode_remaining_qty": {"SpaceX": {"NCT": 500, "SAB": 1100},
                                    "ZaloPay": {"NCT": 373}},
    "capit_episode_error": None,
}
BASE = {"breadth_oversold": 0.22, "w_lag_target": 0.65, "w_lag_current": 0.65,
        "capit_size": 0.0, "capit_grind": False}

CASES = {
    # T1: gate hôm nay bắn (hành vi CŨ phải giữ nguyên)
    "T1_fired": {**BASE, "breadth_oversold": 0.33, "capit_signal_today": True,
                 "capit_size": 0.75, **{**EP, "capit_episode_open": True}},
    # T2: TÌNH HUỐNG THẬT 07-31 — tín hiệu tắt, vị thế còn
    "T2_holding": {**BASE, "capit_signal_today": False, **EP},
    # T3: không tín hiệu, không episode -> dormant (im lặng ĐÚNG)
    "T3_dormant": {**BASE, "capit_signal_today": False, "capit_episode_open": False},
    # T4: status ghi TRƯỚC lần đổi tên + trước khi có sổ episode (alias fallback, không crash)
    "T4_legacy": {**BASE, "capit_fired": False},
    # T5: sổ episode lỗi -> vẫn phải hiện cảnh báo, không nuốt lỗi
    "T5_error": {**BASE, "capit_signal_today": False, "capit_episode_open": False,
                 "capit_episode_error": "positions snapshot stale (12d)"},
}

EMPTY = pd.DataFrame()


def tg(st):
    return tr.build_message("SpaceX", 3, "NEUTRAL", EMPTY, EMPTY, EMPTY, {}, 0,
                            include_universe=False, v23_status=st)


def sh_note(st):
    """Chạy ĐÚNG đoạn CAPIT_STATE/CAPIT_NOTE trích từ bq_freshness_check.sh trên fixture."""
    block = subprocess.run(
        ["sed", "-n", '/^  CAPIT_STATE="\\$(cd "\\$WORKDIR"/,/^  fi$/p', SH],
        capture_output=True, text=True, check=True).stdout
    assert "capit_episode_open" in block and block.strip().endswith("fi"), \
        "trích sai đoạn shell — sửa regex sed"
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "data"))
        with open(os.path.join(d, "data/golive_v23_status.json"), "w") as f:
            json.dump(st, f)
        script = f'WORKDIR="{d}"\n{block}\necho "NOTE:$CAPIT_NOTE"\necho "STATE:$CAPIT_STATE"'
        out = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
        return out.stdout


def main():
    fails = []

    def chk(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'} — {name}{'' if cond else ' :: ' + detail}")
        if not cond:
            fails.append(name)

    print("── 1. telegram_recommend.build_message ──")
    m1 = tg(CASES["T1_fired"])
    chk("T1 fired -> WASHOUT (hành vi cũ giữ nguyên)", "WASHOUT" in m1 and "ĐANG GIỮ" not in m1)

    m2 = tg(CASES["T2_holding"])
    chk("T2 holding -> hiện ĐANG GIỮ (KHÔNG im lặng)", "ĐANG GIỮ" in m2 and "dormant" not in m2)
    chk("T2 hiện entry date", "2026-07-20" in m2)
    chk("T2 hiện số phiên giữ", "8 phiên" in m2)
    chk("T2 hiện rổ gốc đủ 5 mã", all(t in m2 for t in EP["capit_episode_basket"]))
    chk("T2 hiện qty còn lại theo account", "SpaceX" in m2 and "ZaloPay" in m2)
    chk("T2 nói rõ exit do người quyết", "exit do NGƯỜI quyết" in m2)

    m3 = tg(CASES["T3_dormant"])
    chk("T3 dormant (không tín hiệu, không vị thế)", "dormant" in m3 and "ĐANG GIỮ" not in m3)

    # T4: status CŨ (chưa có key episode — bản ghi của lần golive trước khi sổ ra đời).
    # Reader phải fallback đọc THẲNG sổ episode, nếu không thì im lặng suốt cửa sổ
    # telegram-18:00 < golive-19:00. observe() được monkeypatch để test tất định.
    import capit_episode
    _real_observe = capit_episode.observe
    try:
        capit_episode.observe = lambda *a, **k: {k2: v for k2, v in EP.items()}
        m4 = tg(CASES["T4_legacy"])
        chk("T4a status cũ + sổ CÓ episode mở -> fallback hiện ĐANG GIỮ",
            "ĐANG GIỮ" in m4 and "2026-07-20" in m4)
        capit_episode.observe = lambda *a, **k: {**{k2: None for k2 in EP},
                                                 "capit_episode_open": False}
        chk("T4b status cũ + sổ KHÔNG có episode -> dormant", "dormant" in tg(CASES["T4_legacy"]))

        def _boom(*a, **k):
            raise RuntimeError("ledger hỏng")
        capit_episode.observe = _boom
        m4c = tg(CASES["T4_legacy"])
        chk("T4c sổ lỗi -> không crash + hiện cảnh báo",
            "ledger hỏng" in m4c and "CAPIT" in m4c)
    finally:
        capit_episode.observe = _real_observe

    # Sổ THẬT trên đĩa: observe() phải thấy episode đang mở (không gọi broker, không ghi)
    obs = capit_episode.observe()
    chk("T4d observe() trên sổ thật -> episode CAPIT-2026-07-20 đang mở",
        obs.get("capit_episode_open") is True and obs.get("capit_episode_id") == "CAPIT-2026-07-20",
        str(obs)[:200])

    m5 = tg(CASES["T5_error"])
    chk("T5 lỗi sổ episode -> hiện cảnh báo", "sổ episode" in m5 and "stale" in m5)

    print("── 2. bq_freshness_check.sh (prompt DollarBill) ──")
    o1 = sh_note(CASES["T1_fired"])
    chk("T1 fired -> STATE=fired + note ĐÃ KÍCH HOẠT",
        "STATE:fired" in o1 and "ĐÃ KÍCH HOẠT" in o1, o1)
    chk("T1 note dùng tên mới capit_signal_today", "capit_signal_today=true" in o1)

    o2 = sh_note(CASES["T2_holding"])
    chk("T2 holding -> note ĐANG GIỮ VỊ THẾ (prompt không còn im lặng)",
        "ĐANG GIỮ VỊ THẾ" in o2, o2)
    chk("T2 note có entry + số phiên + rổ",
        "2026-07-20" in o2 and "8 phiên" in o2 and "NCT,PVT,SAB,SIP,VNM" in o2, o2)
    chk("T2 note cấm tự sinh lệnh bán", "KHÔNG tự sinh lệnh BÁN" in o2)

    o3 = sh_note(CASES["T3_dormant"])
    chk("T3 dormant -> note RỖNG (không nhiễu ngày thường)",
        "STATE:no" in o3 and o3.splitlines()[0] == "NOTE:", o3)

    o4 = sh_note(CASES["T4_legacy"])
    chk("T4 status cũ -> note rỗng, không lỗi", o4.splitlines()[0] == "NOTE:", o4)

    o5 = sh_note({})
    chk("T5b status hỏng/thiếu key -> fail-safe 'no'", "STATE:no" in o5, o5)

    print(f"\n{'ALL PASS' if not fails else 'FAILED: ' + ', '.join(fails)} "
          f"({len(fails)} fail)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
