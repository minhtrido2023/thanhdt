#!/usr/bin/env python3
"""Selfcheck cho `mike_json.py circuit-tripped` + hang so HB_FRESH_S trong dispatch.sh.

Bao ve HAI quyet dinh, ca hai deu la su co that 2026-08-19 (job Wags_20260819_054508):

  1. Doc trang thai circuit breaker phai SO VOI NOW. `tripped_until` khong bao gio duoc
     don khi het han neu khong co dispatch moi (circuit-check don lazy) => bat ky checker
     nao test truthiness se bao TRIPPED vinh vien. ops_health_check.sh check #4 tung nhu vay
     va da dot mot job Wags(Opus) cho breaker Taylor het han truoc do 2 phut.

  2. circuit-tripped phai READ-ONLY. No chay tu cron health-check; neu no "tien tay" don
     trip het han thi checker se GHI vao state ma duong dispatch dang doc — va lan doc thu
     hai se thay khac lan dau.

Chay: python3 bin/circuit_expiry_selfcheck.py    (exit 0 = PASS)
Mutation RED: --mutate <ten> co y lam hong de chung minh assertion that su do dung cai gi.
"""
import json, os, re, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Cho phep tro sang mot BAN SAO da bi lam hong — day la co che mutation RED (chung minh
# assertion that su do dung cai gi). Production luon dung ban trong repo.
MIKE_JSON = os.environ.get("SELFCHECK_MIKE_JSON") or os.path.join(ROOT, "bin", "mike_json.py")
DISPATCH = os.path.join(ROOT, "bin", "dispatch.sh")
MUTATE = ""
_fails = []


def check(name, got, want):
    ok = got == want
    print("  %s %-58s got=%r want=%r" % ("PASS" if ok else "FAIL", name, got, want))
    if not ok:
        _fails.append(name)


def run_tripped(state_dir):
    p = subprocess.run([sys.executable, MIKE_JSON, "circuit-tripped", state_dir],
                       capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        return "ERR:" + (p.stderr or "").strip()[:120]
    return [ln.split()[0] for ln in p.stdout.splitlines() if ln.strip()]


def write_state(d, name, obj):
    with open(os.path.join(d, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f)


def main():
    now = int(time.time())
    with tempfile.TemporaryDirectory() as d:
        # A: dang trong cooldown -> PHAI bao
        write_state(d, "AgentOpen", {"fails": 3, "tripped_until": now + 900, "last_fail_at": now})
        # B: da het han -> PHAI IM (day la ca lam sinh ra bug goc)
        write_state(d, "AgentExpired", {"fails": 3, "tripped_until": now - 135, "last_fail_at": now - 1935})
        # C: chua bao gio trip
        write_state(d, "AgentClean", {"fails": 0, "tripped_until": 0})
        # D: co fail nhung chua cham nguong -> chua bi chan
        write_state(d, "AgentPartial", {"fails": 2, "tripped_until": 0, "last_fail_at": now})
        # E: file rac -> khong duoc lam chet ca lenh
        with open(os.path.join(d, "AgentCorrupt.json"), "w", encoding="utf-8") as f:
            f.write("{not json")

        got = run_tripped(d)
        check("chi agent CON trong cooldown moi duoc bao", got, ["AgentOpen"])
        check("agent het han KHONG bi bao (bug goc 2026-08-19)",
              "AgentExpired" in (got if isinstance(got, list) else []), False)
        check("file state hong khong lam chet lenh", isinstance(got, list), True)

        # READ-ONLY: state phai nguyen ven sau khi doc.
        # PHAI chup `before` tren mot thu muc CHUA TUNG bi circuit-tripped cham vao. Ban dau
        # test nay chup `before` sau khi da goi run_tripped(d) o tren => mot ban lam hong
        # "tien tay don trip het han" van XANH, vi hong xong roi moi chup va lan goi thu hai
        # thi idempotent. Mutation M3 bat duoc dung loi nay (2026-08-19).
        with tempfile.TemporaryDirectory() as d2:
            write_state(d2, "AgentOpen", {"fails": 3, "tripped_until": now + 900})
            write_state(d2, "AgentExpired", {"fails": 3, "tripped_until": now - 135,
                                             "last_fail_at": now - 1935})
            write_state(d2, "AgentClean", {"fails": 0, "tripped_until": 0})
            before = {n: open(os.path.join(d2, n), encoding="utf-8").read()
                      for n in sorted(os.listdir(d2))}
            run_tripped(d2)
            after = {n: open(os.path.join(d2, n), encoding="utf-8").read()
                     for n in sorted(os.listdir(d2))}
            check("circuit-tripped la READ-ONLY (khong sua state)", after, before)

        # Ranh gioi: tripped_until == now => da het han, khong con chan
        # (circuit-check dung `n >= tripped_until` de mo lai; hai ben phai khop nhau)
        write_state(d, "AgentOpen", {"fails": 3, "tripped_until": int(time.time()), "last_fail_at": now})
        check("tripped_until == now => coi la het han", "AgentOpen" in run_tripped(d), False)

        # circuit-check (duong dispatch) va circuit-tripped (duong checker) phai DONG THUAN
        write_state(d, "AgentOpen", {"fails": 3, "tripped_until": int(time.time()) + 900})
        cc = subprocess.run([sys.executable, MIKE_JSON, "circuit-check", d, "AgentOpen"],
                            capture_output=True, text=True, timeout=30)
        check("circuit-check chan == circuit-tripped bao",
              (cc.returncode == 1, "AgentOpen" in run_tripped(d)), (True, True))
        write_state(d, "AgentExpired2", {"fails": 3, "tripped_until": int(time.time()) - 10})
        listed = "AgentExpired2" in run_tripped(d)
        cc2 = subprocess.run([sys.executable, MIKE_JSON, "circuit-check", d, "AgentExpired2"],
                             capture_output=True, text=True, timeout=30)
        check("het han: circuit-check cho qua VA circuit-tripped im",
              (cc2.returncode, listed), (0, False))

    # HB_FRESH_S: chan viec ai do lang le ha lai ve 120s (xem do luong p90=557s trong
    # chu thich tai cho). Khong assert dung 600 — assert "du rong so voi nhip that".
    src = open(DISPATCH, encoding="utf-8").read()
    if MUTATE == "hb_fresh_revert":
        src = src.replace('HB_FRESH_S="${DISPATCH_HB_FRESH_S:-600}"',
                          'HB_FRESH_S="${DISPATCH_HB_FRESH_S:-120}"')
    m = re.search(r'HB_FRESH_S="\$\{DISPATCH_HB_FRESH_S:-(\d+)\}"', src)
    check("dispatch.sh co dinh nghia HB_FRESH_S", bool(m), True)
    if m:
        check("HB_FRESH_S >= 557s (p90 khoang cach heartbeat that)", int(m.group(1)) >= 557, True)
    m2 = re.search(r'MAX_EXT="\$\{DISPATCH_HB_MAX_EXTENSIONS:-(\d+)\}"', src)
    check("MAX_EXT van chan tong doi mot attempt (<=5)",
          bool(m2) and 1 <= int(m2.group(1)) <= 5, True)

    print("\n%s — %d/%d" % ("FAIL" if _fails else "PASS",
                            8 - len(_fails) + (len(_fails) and 0), 8) if False else "")
    if _fails:
        print("FAILED: %s" % ", ".join(_fails))
        return 1
    print("PASS — tat ca assertion xanh")
    return 0


if __name__ == "__main__":
    if "--mutate" in sys.argv:
        MUTATE = sys.argv[sys.argv.index("--mutate") + 1]
        print("[MUTATION=%s] mong doi FAIL" % MUTATE)
    sys.exit(main())
