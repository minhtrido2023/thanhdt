#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check 2 việc user duyệt 16:52 ICT 2026-09-28.

  #1 `bot_execute._notify_failopen` — 3 cổng fail-open nay BÁO VÀO TELEGRAM, không chỉ in log
  #2 `rating_8l_history` — refresh `tav2_bq.fa_ratings_8l` TỰ SUY theo ĐÍCH GHI, không còn
     "mặc định refresh trừ khi nhớ bật cờ tắt" (retro 2026-09-27 Pattern 1)

⚠️ KHÔNG gọi BQ, KHÔNG gửi Telegram/Discord thật: `_notify_trading_daily` và `refresh_bq_table`
đều bị thay bằng stub; khối quyết định được TRÍCH NGUYÊN VĂN và chạy trong sandbox.
§5b: `MIKE_BOT_TEST_MODE=1` đặt trước mọi import.

Chạy:  $DNA_PYEXE failopen_telegram_refresh_selfcheck.py
"""
import os

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

import re          # noqa: E402
import subprocess  # noqa: E402
import sys         # noqa: E402
import tempfile    # noqa: E402
import textwrap    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_REF = os.environ.get("FOTG_OLD_REF", "").strip() or "bfccf9af^"
_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        raise AssertionError(msg)


def src(rel, ref=None):
    if ref is None:
        return open(os.path.join(HERE, rel), encoding="utf-8").read()
    r = subprocess.run(["git", "show", f"{ref}:WorkingClaude/{rel}"], cwd=HERE,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"không đọc được {ref}:{rel} — git: {r.stderr.strip()}")
    return r.stdout


def fn_src(text, name, what):
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines) if l.startswith(f"def {name}(")), None)
    assert i is not None, f"không thấy `def {name}(` top-level trong {what} — dừng, đừng đoán"
    j = next((k for k in range(i + 1, len(lines))
              if lines[k].startswith("def ") or lines[k].startswith("class ")), len(lines))
    return "".join(lines[i:j])


# ───────────────── #1 — fail-open phải tới Telegram ─────────────────
def t1_notify_failopen_reaches_telegram():
    code = fn_src(src("bot_execute.py"), "_notify_failopen", "bot_execute MỚI")
    sent = []
    g = {"print": lambda *a, **k: None,
         "_notify_trading_daily": lambda m: sent.append(m)}
    exec(textwrap.dedent(code), g)
    g["_notify_failopen"]("SpaceX", "LAG rating 8L≤3", "BQ down: connection refused")
    ok(len(sent) == 1, f"#1 phải gửi ĐÚNG 1 tin qua _notify_trading_daily, được {sent}")
    m = sent[0]
    ok("SpaceX" in m and "LAG rating 8L≤3" in m, f"#1 tin thiếu account/tên cổng:\n{m}")
    ok("BQ down: connection refused" in m, f"#1 tin không mang LÝ DO THẬT (§29):\n{m}")
    ok("fail-open" in m.lower(), f"#1 tin không nói rõ đây là fail-open:\n{m}")
    ok("VẪN ĐI RA" in m, f"#1 tin không nói lệnh vẫn đi ra:\n{m}")
    # `_notify_trading_daily` THẬT có gửi Telegram không? (đọc code, không gửi thật)
    real = fn_src(src("bot_execute.py"), "_notify_trading_daily", "bot_execute")
    ok("send_telegram_text" in real, "#1 _notify_trading_daily KHÔNG gửi Telegram — sai kênh user yêu cầu")
    ok("notify_thread.sh" in real, "#1 _notify_trading_daily mất kênh Discord")


def t1b_all_three_gates_wired_two_sided():
    new, old = src("bot_execute.py"), src("bot_execute.py", OLD_REF)
    for gate in ("signal_holds", "LAG rating 8L≤3", "LAG quản trị (BANNED/forensic)"):
        ok(f'_notify_failopen(p["label"], "{gate}"' in new,
           f"#1 cổng {gate!r} CHƯA wire vào _notify_failopen")
    ok(new.count("_notify_failopen(p[") == 3, f"#1 phải đúng 3 call-site, đếm được "
                                              f"{new.count('_notify_failopen(p[')}")
    # 2 CHIỀU: bản CŨ chỉ `print`, KHÔNG có helper nào
    ok("_notify_failopen" not in old, "#1 bản CŨ không lẽ đã có helper?")
    for needle in ("⚠⚠ signal_holds gate KHÔNG CHẠY ĐƯỢC",
                   "⚠⚠ LAG gate rating KHÔNG CHẠY ĐƯỢC",
                   "⚠⚠ LAG gate quản trị KHÔNG ĐẦY ĐỦ"):
        ok(needle in old, f"#1 bản CŨ phải có dòng print {needle!r} (tiền đề A/B)")
        ok(needle not in new or "_notify_failopen" in new,
           f"#1 bản MỚI vẫn còn print-only cho {needle!r}")


# ───────────────── #2 — refresh tự suy theo đích ghi ─────────────────
def _run_refresh_block(ref, out_env, env_extra=None):
    """Chạy khối quyết định refresh; trả (có_gọi_refresh, stdout)."""
    text = src("rating_8l_history.py", ref)
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines)
              if l.strip().startswith("path = os.environ.get(\"R8L_HIST_OUT\")")
              or l.strip().startswith("_canon = os.path.join(WORKDIR")), None)
    assert i is not None, f"không thấy ĐẦU khối refresh @{ref or 'HEAD'}"
    j = next((k for k in range(i, len(lines)) if "refresh_bq_table(path)" in lines[k]), None)
    assert j is not None, f"không thấy `refresh_bq_table(path)` @{ref or 'HEAD'}"
    # Kết thúc khối = dòng NGAY TRƯỚC `print("\\ndistribution by route` (phần thống kê cuối
    # hàm). Heuristic "đi tiếp chừng nào còn thụt" đã cắt lố vào code dùng `pd` (bắt được lúc viết).
    e = next((k for k in range(j, len(lines)) if "distribution by route x rating" in lines[k]), None)
    assert e is not None, f"không thấy mốc kết thúc khối refresh @{ref or 'HEAD'}"
    block = textwrap.dedent("".join(lines[i:e]))
    d = tempfile.mkdtemp(prefix="r8l_")
    os.makedirs(os.path.join(d, "data"), exist_ok=True)
    called, printed = [], []

    class _Out:
        def to_csv(self, *a, **k):
            pass

        def __len__(self):
            return 1

    env_bak = dict(os.environ)
    for k2 in ("R8L_HIST_OUT", "R8L_HIST_NO_BQ_REFRESH", "R8L_HIST_BQ_REFRESH"):
        os.environ.pop(k2, None)
    if out_env:
        os.environ["R8L_HIST_OUT"] = out_env
    os.environ.update(env_extra or {})
    g = {"os": os, "WORKDIR": d, "out": _Out(), "len": len,
         "refresh_bq_table": lambda p: called.append(p),
         "print": lambda *a, **k: printed.append(" ".join(str(x) for x in a))}
    try:
        exec(block, g)
    finally:
        os.environ.clear(); os.environ.update(env_bak)
    return called, "\n".join(printed), d


def t2_refresh_infers_from_target():
    # (a) ĐÍCH = canonical ⇒ refresh (hành vi production KHÔNG đổi)
    called, log, d = _run_refresh_block(None, None)
    ok(len(called) == 1, f"#2 đích canonical phải refresh, called={called}")
    # (b) ĐÍCH KHÁC (run thí nghiệm) ⇒ KHÔNG chạm BQ + nói rõ vì sao
    exp = os.path.join(tempfile.mkdtemp(prefix="r8l_"), "EXP_thu_nghiem.csv")
    called, log, _ = _run_refresh_block(None, exp)
    ok(called == [], f"#2 đích KHÁC canonical mà VẪN refresh ⇒ đúng sự cố 27/09: {called}")
    ok("KHONG phai canonical" in log, f"#2 không nói rõ lý do bỏ qua:\n{log}")
    ok("R8L_HIST_BQ_REFRESH=1" in log, f"#2 không chỉ cách ép tường minh:\n{log}")
    # (c) ÉP tường minh ⇒ vẫn refresh được (đường phục hồi)
    called, log, _ = _run_refresh_block(None, exp, {"R8L_HIST_BQ_REFRESH": "1"})
    ok(len(called) == 1, f"#2 ép tường minh phải refresh, called={called}")
    # (d) cờ TẮT cũ vẫn tôn trọng
    called, log, _ = _run_refresh_block(None, None, {"R8L_HIST_NO_BQ_REFRESH": "1"})
    ok(called == [], f"#2 R8L_HIST_NO_BQ_REFRESH=1 vẫn phải chặn: {called}")
    # (e) 2 CHIỀU — bản CŨ: đích KHÁC canonical mà VẪN refresh (chính là sự cố)
    called_o, log_o, _ = _run_refresh_block(OLD_REF, exp)
    ok(len(called_o) == 1,
       f"#2 bản CŨ phải VẪN refresh dù ghi ra file khác (sự cố 27/09), called={called_o}")
    ok(called_o[0] == exp, f"#2 bản CŨ refresh từ chính file thí nghiệm: {called_o}")


TESTS = [t1_notify_failopen_reaches_telegram, t1b_all_three_gates_wired_two_sided,
         t2_refresh_infers_from_target]

if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '(unset)')}  python={sys.version.split()[0]}  OLD_REF={OLD_REF}")
    fails = 0
    for t in TESTS:
        try:
            t()
            print(f"  PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"  FAIL {t.__name__}: {e}")
    print()
    print(f"{'PASS' if not fails else 'FAIL'}  ({_n} assertion"
          + (")" if not fails else f", {fails} test FAIL)"))
    sys.exit(1 if fails else 0)
