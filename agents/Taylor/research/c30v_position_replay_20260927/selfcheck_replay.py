#!/usr/bin/env python3
"""Selfcheck for the position replay — MUTATION + PROPERTY based.

A replay that agrees with the engine is only evidence if the agreement is FRAGILE: each mutation
below removes or corrupts one piece of the model and MUST move the number. A mutation that leaves
the result unchanged means that piece was never wired in, and the agreement it produced was luck.

Two of the six checks are PROPERTY checks rather than mutations, deliberately, because round 1 got
them wrong in the opposite direction — asserting "must move" on something that provably cannot:
  * M4 (px-repair): with the repair bounded to real price-adjusting ex-dates it touches 8 cells
    panel-wide and 0 of them coincide with a share step inside the basket. The thing worth
    asserting is exactly that ZERO — it is what keeps the "raw" leg independent of the adjusted
    chain it audits (see build_prices' caveat). Asserting "CAGR must move" would be asserting the
    repair is material, which it is not, and round 1's stated reason for the non-movement
    ("giá kẹt triệt tiêu t/t+1") is a wrong model: with daily reweighting the weight enters each
    day's return linearly, so a stale price does NOT telescope.
  * the NAV-machinery identity is asserted inside replay.py (event-free replay == an independently
    written raw-price weighted chain, 5e-15), which is a real identity and not true by
    construction, unlike "cash balance reconciles" (cash IS the residual there).

Runs the replay as a SUBPROCESS so each leg gets a clean interpreter, under whatever TZ the caller
hands it — §16 of kb/coding_guidelines.md: a selfcheck that only runs under the author's own
correct TZ proves nothing about the code's TZ dependence.
"""
import os
import re
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PY = "/home/trido/thanhdt/wc_venv/bin/python"
# Mỗi lần chạy phải có KHÔNG GIAN TÊN riêng cho artifact. Vòng 2 chạy 2 instance song song, cả hai
# ghi `levels_sc_*.parquet` cùng tên ⇒ check M4 (đọc parquet từ ĐĨA, dòng dưới) có thể so artifact
# của HAI run khác nhau. §8 coding_guidelines. Caller đặt SC_RUN (run_selfcheck.sh dùng PID+TZ).
RUN = os.environ.get("SC_RUN", "")
RX = re.compile(r"^(ENGINE_FLAT|ENGINE_LEGACY|REPLAY_A|REPLAY_B)\s+level.*CAGR\s+([-\d.]+)%")


BASE_START = "2014-08-05"   # cửa sổ của chân BASE; mọi mutation bị GHIM vào đúng nó (xem M5)


def run(flags, tag):
    # --fixed-start: round 2's M5 re-keyed wmap, which drops its first key and silently measured on
    # a one-session-shorter window (0,017pp of the reported -0,348pp). A mutation must move the
    # thing under test and NOTHING else, so every leg is pinned to the base window.
    out = subprocess.run([PY, f"{HERE}/replay.py", "--out-prefix", tag, "--fixed-start", BASE_START] + flags,
                         capture_output=True, text=True, cwd="/home/trido/thanhdt/WorkingClaude")
    if out.returncode != 0:
        print(out.stdout[-3000:], out.stderr[-3000:])
        raise SystemExit(f"replay.py thất bại cho {tag}")
    got = {m.group(1): float(m.group(2)) for m in
           (RX.match(ln.strip()) for ln in out.stdout.splitlines()) if m}
    assert len(got) == 4, f"không parse được 4 chân cho {tag}: {got}"
    return got, out.stdout


fails = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def engine_ok(name, got, base):
    """A mutation that only changes the replay must leave the engine legs byte-identical — that is
    what proves the mutation is SCOPED to the thing under test and not a global edit."""
    check(f"{name} ⇒ KHÔNG đụng chân engine",
          abs(got["ENGINE_FLAT"] - base["ENGINE_FLAT"]) < 1e-9
          and abs(got["ENGINE_LEGACY"] - base["ENGINE_LEGACY"]) < 1e-9,
          f"flat {got['ENGINE_FLAT']:.3f} legacy {got['ENGINE_LEGACY']:.3f}")


print(f"TZ = {os.environ.get('TZ', '(unset)')!r}")
print("\nBASE")
base, out0 = run([], RUN + "sc_base")
for k, v in base.items():
    print(f"    {k:14s} {v:8.3f}%")

check("0a. harness tái lập chân engine khớp build_pit (assert cứng trong replay.py)",
      "[harness]" in out0 and "max |Δ| = " in out0)
check("0b. identity: replay không sự kiện/không phí == chuỗi giá thô độc lập (assert cứng)",
      "[identity]" in out0)
m = re.search(r"cửa sổ PREREG; bỏ ([\d.]+)y chưa đầu tư", out0)
check("0c. CAGR đo từ rebal ĐẦU TIÊN, không tính thời gian chưa đầu tư", bool(m),
      f"bỏ {m.group(1)}y" if m else "")
m = re.search(r"ô sửa GIAO với một bước số CP trong rổ: (\d+)", out0)
check("0d. px-repair KHÔNG giao với bất kỳ bước số CP nào trong rổ ⇒ replay không bị cưỡng bức "
      "khớp chuỗi Close ở đúng những ô đó", bool(m) and int(m.group(1)) == 0,
      f"giao = {m.group(1) if m else '?'}")
m = re.search(r"ô sửa NẰM TRONG RỔ phiên đó: (\d+)", out0)
check("0d2. KHÔNG ô sửa nào NẰM TRONG RỔ phiên đó ⇒ đường cưỡng bức khớp Close không bao giờ được "
      "đi, với MỌI loại sự kiện (kể cả cổ tức tiền: r_rep = r_flat·(1−D/P)), không chỉ bước số CP",
      bool(m) and int(m.group(1)) == 0, f"trong rổ = {m.group(1) if m else '?'}")

MUT = [
    ("M1 bỏ hẳn bước N×(1+Σq)", ["--no-share-step"], "neg"),
    ("M1b hệ số cùng ngày NHÂN thay vì CỘNG (lỗi vòng 1)", ["--mult-share-step"], "posB"),
    ("M2 mark-to-market bằng Close (adj) thay vì Price (thô)", ["--mark-close"], "any"),
    ("M3 bỏ phí rebal 0,1%/chiều", ["--no-fee"], "posA"),
    ("M5 trễ trọng số 1 phiên (lỗi vòng 1)", ["--lag-weights"], "movesA"),
    ("M6 trả cổ tức tiền CHẬM 40 phiên (độ nhạy PREREG §4)", ["--div-lag", "40"], "any"),
]
for name, flags, direction in MUT:
    # prefix bám theo TÊN mutation, không theo chỉ số vòng lặp — vòng 2 để M5 (i=4) và M4 ghi
    # trùng `sc_m4` nên artifact của M5 bị xoá sạch (coding_guidelines §8).
    tag = RUN + "sc_" + name.split()[0].lower()
    got, _ = run(flags, tag)
    dA, dB = got["REPLAY_A"] - base["REPLAY_A"], got["REPLAY_B"] - base["REPLAY_B"]
    det = f"ΔCAGR A {dA:+.3f}pp / B {dB:+.3f}pp"
    check(f"{name} ⇒ PHẢI làm lệch", abs(dA) > 0.01 or abs(dB) > 0.01, det)
    if direction == "neg":
        check(f"{name} ⇒ lệch chiều ÂM (mất cổ phiếu thưởng)", dA < 0 and dB < 0, det)
    if direction == "posB":
        check(f"{name} ⇒ lệch chiều DƯƠNG (nhân = số CP ảo)", dB > 0, det)
    if direction == "posA":
        check(f"{name} ⇒ REPLAY_A lệch chiều DƯƠNG (bỏ phí)", dA > 0, det)
    if direction == "movesA":
        # M5 đổi CẢ chân engine (engine_legs dùng chính wmap đã trễ) — đó là bản chất của lỗi vòng
        # 1: nó dịch cả hai chân, nên so sánh giữa chúng trông "ổn" trong khi mỗi chân đều sai.
        check(f"{name} ⇒ dịch CẢ chân engine (chứng minh trễ là biến chung, không phải riêng replay)",
              abs(got["ENGINE_FLAT"] - base["ENGINE_FLAT"]) > 0.01,
              f"flat {base['ENGINE_FLAT']:.3f} -> {got['ENGINE_FLAT']:.3f}")
    else:
        engine_ok(name, got, base)

# M4 = property, not mutation (see docstring)
got4, out4 = run(["--no-px-repair"], RUN + "sc_m4px")
d4 = got4["REPLAY_B"] - base["REPLAY_B"]
lb = pd.read_parquet(f"{HERE}/levels_{RUN}sc_base.parquet")["REPLAY_B"].pct_change()
lm = pd.read_parquet(f"{HERE}/levels_{RUN}sc_m4px.parquet")["REPLAY_B"].pct_change()
dd = (lb - lm).abs()
check("M4 bỏ px-repair ⇒ CAGR KHÔNG được lệch đáng kể (repair đã bị giới hạn vào ngày ex thật, "
      "8 ô toàn panel, 0 ô giao bước số CP trong rổ)", abs(d4) < 0.01,
      f"ΔCAGR B {d4:+.4f}pp; {int((dd>1e-9).sum())} phiên chuỗi ngày lệch, max {dd.max()*1e4:.2f} bp")
engine_ok("M4 bỏ px-repair", got4, base)

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print(f"OK — selfcheck_replay PASS ({len(MUT)} mutation + 5 property, TZ={os.environ.get('TZ','(unset)')!r})")
