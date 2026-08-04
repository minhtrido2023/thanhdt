#!/usr/bin/env python3
"""A3 — Cổng WARN CAPIT ở `send_plan_report.sh` có thật sự bắt được sự cố 07-21 không?

Không đọc code rồi phán. File này **trích ĐÚNG khối python của cổng** ra khỏi
`mike/bin/send_plan_report.sh` (giữa hai mốc văn bản trong chính file production) rồi `exec`
nó trên **dữ liệu plan THẬT** của 4 phiên. Ai sửa câu chữ/ngưỡng bên production thì test này
thấy ngay, vì nó chạy chính văn bản đó chứ không phải bản chép tay.

Chạy:  python3 mike/agents/Taylor/research/capit_warn_gate_replay_20260804.py
KHÔNG mạng, KHÔNG broker, KHÔNG ghi file.
"""
import json
import os
import re
import sys

_here = os.path.abspath(__file__)
WC = _here
for _ in range(5):
    WC = os.path.dirname(WC)

SH = os.path.join(WC, "mike", "bin", "send_plan_report.sh")
BEGIN = "# ── CAPIT: Σ lệnh mua thật vs VND mục tiêu đã publish (WARN, KHÔNG chặn)"
END = "# ── ĐÒN BẨY MARGIN: nêu BẬT LOẠT"

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def extract_gate_source(path=SH):
    src = open(path, encoding="utf-8").read()
    i, j = src.find(BEGIN), src.find(END)
    if i < 0 or j < 0 or j <= i:
        raise SystemExit("KHÔNG trích được khối cổng — mốc văn bản đã đổi, sửa BEGIN/END.")
    return src[i:j]


def run_gate(gate_src, orders, status, acct):
    """Chạy khối cổng production trong namespace tối thiểu nó cần."""
    tmpdir = os.path.join(os.environ.get("TMPDIR", "/tmp"),
                          f"capit_replay_{os.getpid()}")
    os.makedirs(os.path.join(tmpdir, "data"), exist_ok=True)
    with open(os.path.join(tmpdir, "data", "golive_v23_status.json"), "w",
              encoding="utf-8") as f:
        json.dump(status, f)
    cwd = os.getcwd()
    os.chdir(tmpdir)                      # cổng đọc "data/golive_v23_status.json" tương đối
    try:
        ns = {"json": json, "os": os, "orders": orders, "acct": acct,
              "_order_price": lambda o: (o.get("ref_price") or o.get("price")
                                         or o.get("limit_price_vnd"))}
        exec(compile(gate_src, SH, "exec"), ns)
        return ns.get("capit_note", "")
    finally:
        os.chdir(cwd)


def plan_orders(account, date):
    p = os.path.join(WC, "data", "trade_plans", f"plan_{account}_{date}.json")
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8")).get("orders", [])


def capit_buys(orders):
    return [o for o in orders or [] if str(o.get("book", "")).upper() == "CAPIT"
            and str(o.get("side", "")).lower() in ("buy", "mua", "b")]


def main():
    print("=" * 78)
    print("A3 — replay cổng WARN CAPIT trên dữ liệu plan THẬT")
    print("=" * 78)
    gate = extract_gate_source()
    print(f"\nTrích được {len(gate.splitlines())} dòng từ {os.path.relpath(SH, WC)}")
    m = re.search(r"abs\(_dev\)\s*>\s*([\d.]+)", gate)
    thr = float(m.group(1)) if m else None
    check("đọc được ngưỡng từ chính văn bản production", thr is not None, gate[:200])
    print(f"  → ngưỡng hiện tại: {thr:.0%}")

    # ── 1. SỰ CỐ THẬT 07-21: Σ 254,4tr vs mục tiêu 348,4tr (5 mã × 69,68tr) ──────────────
    print("\n[1] SỰ CỐ THẬT 2026-07-21 SpaceX (nhân capit_size hai lần, thiếu 87,1tr)")
    orders = plan_orders("SpaceX", "2026-07-21")
    cb = capit_buys(orders)
    actual = sum(float(o.get("actual_vnd") or 0)
                 or float(o.get("qty") or 0) * float(o.get("ref_price") or 0) for o in cb)
    print(f"  plan thật: {len(cb)} lệnh CAPIT, Σ = {actual:,.0f}đ")
    check("Σ khớp con số sự cố 254,4tr", abs(actual - 254_425_000) < 1000, actual)
    status = {"capit_slot_targets": {"SpaceX": {"capit_slot_target_vnd": 348_400_000 / 5}},
              "capit_lever": {"active": False}}
    note = run_gate(gate, orders, status, "SpaceX")
    print(f"  → cổng nói: {note}")
    check("CỔNG BẮT ĐƯỢC (⚠️, không phải ✅)", note.startswith("⚠️ CAPIT:"), note)
    check("nêu đúng độ lệch ~−27%", "-27.0%" in note or "-27." in note, note)
    check("nêu đúng nguyên nhân nghi ngờ (nhân capit_size hai lần)",
          "nhân capit_size hai lần" in note, note)

    # ── 2. Plan ĐÚNG (Σ == mục tiêu) → phải im, không kêu oan ────────────────────────────
    print("\n[2] plan ĐÚNG (Σ == mục tiêu) → cổng phải im")
    status_ok = {"capit_slot_targets":
                 {"SpaceX": {"capit_slot_target_vnd": actual / len(cb)}},
                 "capit_lever": {"active": False}}
    note_ok = run_gate(gate, orders, status_ok, "SpaceX")
    print(f"  → cổng nói: {note_ok}")
    check("✅ chứ không ⚠️", note_ok.startswith("✅ CAPIT:"), note_ok)

    # ── 3. BIÊN ngưỡng 10% ──────────────────────────────────────────────────────────────
    # Ngưỡng là `abs(_dev) > 0.10`. ĐÚNG 10,0% là điểm mà số dấu phẩy động không quyết định
    # được (dựng target = actual/(1+0,10) rồi tính ngược ra _dev = 0.10000000000000009 > 0.10
    # ⇒ kêu). Không assert ở đúng điểm đó — vô nghĩa; assert hai bên nó.
    print("\n[3] biên ngưỡng: 9,5% → im; 10,5% → kêu (đúng 10,0% là điểm float, bỏ qua)")
    for dev, want_warn in ((0.095, False), (0.105, True), (-0.095, False), (-0.105, True)):
        tgt = actual / (len(cb) * (1 + dev))
        st = {"capit_slot_targets": {"SpaceX": {"capit_slot_target_vnd": tgt}},
              "capit_lever": {"active": False}}
        n = run_gate(gate, orders, st, "SpaceX")
        got_warn = n.startswith("⚠️")
        check(f"lệch {dev:+.1%} → {'kêu' if want_warn else 'im'}", got_warn == want_warn, n)

    # ── 4. ĐIỂM MÙ 1: plan viết THIẾU MÃ (target scale theo số lệnh trong plan) ──────────
    print("\n[4] ĐIỂM MÙ — plan chỉ viết 3/5 mã của rổ (thiếu 40% vốn) → cổng có thấy?")
    subset = cb[:3]
    others = [o for o in orders if o not in cb]
    slot_correct = 348_400_000 / 5
    st = {"capit_slot_targets": {"SpaceX": {"capit_slot_target_vnd": slot_correct}},
          "n_capit_basket": 5, "capit_lever": {"active": False}}
    # cho từng lệnh đúng cỡ slot để chỉ còn khác biệt "thiếu mã"
    subset_ok = [dict(o, actual_vnd=slot_correct) for o in subset]
    note_sub = run_gate(gate, subset_ok + others, st, "SpaceX")
    print(f"  → cổng nói: {note_sub}")
    check("cổng nói ✅ dù thiếu 2/5 mã (= ĐIỂM MÙ có thật)",
          note_sub.startswith("✅ CAPIT:"), note_sub)
    check("cổng KHÔNG hề nhắc tới n_capit_basket",
          "n_capit_basket" not in gate, "gate có đọc n_capit_basket?")

    # ── 5. ĐIỂM MÙ 2: capit_slot_targets RỖNG (đúng trạng thái hôm nay) ──────────────────
    print("\n[5] ĐIỂM MÙ — capit_slot_targets = {} (trạng thái THẬT hôm nay) → fail-open")
    live = json.load(open(os.path.join(WC, "data", "golive_v23_status.json"),
                          encoding="utf-8"))
    check("status LIVE hôm nay có capit_slot_targets rỗng",
          not (live.get("capit_slot_targets") or {}), live.get("capit_slot_targets"))
    note_empty = run_gate(gate, orders, {"capit_slot_targets": {}}, "SpaceX")
    print(f"  → cổng nói: {note_empty}")
    check("cổng tự khai KHÔNG đối chiếu được (fail-open, không im lặng)",
          "KHÔNG đối chiếu được" in note_empty, note_empty)

    # ── 6. Cổng đã CHẠY THẬT lần nào chưa? ───────────────────────────────────────────────
    print("\n[6] cổng đã chạy thật trên plan có lệnh CAPIT lần nào chưa?")
    dates_with_capit = []
    d = os.path.join(WC, "data", "trade_plans")
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("plan_") or not fn.endswith(".json"):
            continue
        try:
            o = json.load(open(os.path.join(d, fn), encoding="utf-8")).get("orders", [])
        except Exception:
            continue
        if capit_buys(o):
            dates_with_capit.append(fn)
    print(f"  plan có lệnh CAPIT: {dates_with_capit}")
    last = max((f.split("_")[-1][:-5] for f in dates_with_capit), default="")
    print(f"  phiên gần nhất có lệnh CAPIT: {last}")
    print(f"  cổng WARN được thêm: 2026-07-31 (commit d3aa3f05)")
    check("cổng CHƯA từng chạy trên plan có lệnh CAPIT (0 bằng chứng sống)",
          last < "2026-07-31", last)

    patched_gate(live, orders, cb)

    print("\n" + "=" * 78)
    print(f"KẾT QUẢ: {PASS} PASS / {FAIL} FAIL")
    print("=" * 78)
    return 1 if FAIL else 0


def patched_gate(live, orders_0721, cb_0721):
    """Cùng cách trích, nhưng trên bản ĐÃ VÁ (patch A3) — chứng minh hai điểm mù đã đóng
    và bản vá KHÔNG làm hỏng ca 07-21 mà bản cũ đang bắt đúng."""
    import subprocess
    import shutil
    import tempfile
    print("\n" + "-" * 78)
    print("BẢN ĐÃ VÁ (capit_gate_topup_coverage.patch) — chưa wire, kiểm trên bản copy")
    print("-" * 78)
    patch = os.path.join(WC, "mike", "agents", "Taylor", "research",
                         "capit_gate_topup_coverage.patch")
    if not os.path.exists(patch):
        check("có file patch", False, patch)
        return
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "wc")
        os.makedirs(os.path.join(work, "mike", "bin"))
        shutil.copy(SH, os.path.join(work, "mike", "bin"))
        r = subprocess.run(["git", "apply", patch], cwd=work, capture_output=True, text=True)
        if r.returncode:
            check("áp được patch", False, r.stderr)
            return
        newsh = os.path.join(work, "mike", "bin", "send_plan_report.sh")
        # rc=0 KHÔNG đủ — phải kiểm chứng nội dung (bài học E2E của A2)
        if "capit_episode_remaining_qty" not in open(newsh, encoding="utf-8").read():
            check("patch thật sự đổi file", False, "rc=0 nhưng nội dung không đổi")
            return
        gate2 = extract_gate_source(newsh)

        # a) KHÔNG hồi quy: ca 07-21 vẫn bị bắt y như cũ
        st = {"capit_slot_targets": {"SpaceX": {"capit_slot_target_vnd": 348_400_000 / 5}},
              "n_capit_basket": 5, "capit_lever": {"active": False}}
        n = run_gate(gate2, orders_0721, st, "SpaceX")
        check("[vá] ca 07-21 VẪN bị bắt (không hồi quy)", n.startswith("⚠️ CAPIT:"), n)

        # b) điểm mù 1 đóng: 3/5 mã đúng cỡ slot → vẫn ✅ nhưng PHẢI nói rõ chỉ phủ 3/5
        slot = 348_400_000 / 5
        others = [o for o in orders_0721 if o not in cb_0721]
        sub = [dict(o, actual_vnd=slot) for o in cb_0721[:3]]
        n = run_gate(gate2, sub + others, st, "SpaceX")
        print(f"  → {n}")
        check("[vá] nêu rõ phủ 3/5 mã của rổ", "phủ 3/5 mã" in n, n)
        check("[vá] cảnh báo lệch ~0% KHÔNG nghĩa là đủ vốn",
              "KHÔNG có nghĩa đã triển khai đủ vốn" in n, n)

        # c) điểm mù 2 đóng: dùng status LIVE HÔM NAY (episode mở, slot_targets rỗng)
        rem = (live.get("capit_episode_remaining_qty") or {}).get("SpaceX") or {}
        check("status LIVE: episode đang mở", live.get("capit_episode_open") is True, live)
        check("status LIVE: có remaining_qty cho SpaceX", bool(rem), rem)
        ok_orders = [{"book": "CAPIT", "side": "buy", "ticker": t, "qty": q,
                      "ref_price": 10_000} for t, q in list(rem.items())[:3]]
        n = run_gate(gate2, ok_orders, live, "SpaceX")
        print(f"  → {n}")
        check("[vá] top-up ĐÚNG (≤ còn thiếu) → ✅, hết 'KHÔNG đối chiếu được'",
              n.startswith("✅ CAPIT top-up"), n)
        tk, q = next(iter(rem.items()))
        over = [{"book": "CAPIT", "side": "buy", "ticker": tk, "qty": int(q) + 100,
                 "ref_price": 10_000}]
        n = run_gate(gate2, over, live, "SpaceX")
        print(f"  → {n}")
        check("[vá] mua VƯỢT phần còn thiếu → ⚠️", n.startswith("⚠️ CAPIT top-up"), n)
        check("[vá] nêu đúng mã vượt", tk in n, n)
        out = [{"book": "CAPIT", "side": "buy", "ticker": "ZZZ", "qty": 100,
                "ref_price": 10_000}]
        n = run_gate(gate2, out, live, "SpaceX")
        check("[vá] mã KHÔNG thuộc rổ episode → ⚠️", "KHÔNG thuộc rổ episode" in n, n)

        # d) không episode + không slot targets → vẫn fail-open như cũ (không chặn)
        n = run_gate(gate2, ok_orders, {"capit_slot_targets": {},
                                        "capit_episode_open": False}, "SpaceX")
        check("[vá] không episode + không target → vẫn fail-open, tự khai",
              "KHÔNG đối chiếu được" in n, n)

        # e) bản CŨ trên cùng dữ liệu LIVE hôm nay = tối
        old = run_gate(extract_gate_source(), ok_orders, live, "SpaceX")
        print(f"  → [bản cũ, cùng dữ liệu] {old}")
        check("[đối chứng] bản CŨ mù trên phiên top-up hôm nay",
              "KHÔNG đối chiếu được" in old, old)


if __name__ == "__main__":
    sys.exit(main())
