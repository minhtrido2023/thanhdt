#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho CỔNG GHIM vintage corp-action của `basket_price_basis_selfcheck.py`
(VIỆC 3, job Taylor_20260927_131720).

Phạm vi CÓ CHỦ Ý (§23 coding_guidelines): chỉ kiểm `_pin_corp_action_vintage()` +
`_ca_snapshot_candidates()` — đúng hai hàm được THÊM, và chúng không chạm BQ. Phần hành vi
T1-T5 không đổi một dòng, tính tất định của nó được chứng minh riêng bằng 6 lần chạy ĐẦY ĐỦ
liên tiếp (`determinism.txt` + `pinned_run*.log`, mỗi lần ~3 phút và chạm BQ) — selfcheck này
KHÔNG lặp lại chuyện đó.

Bốn câu hỏi:
  P1. Ghim MẶC ĐỊNH resolve vintage nằm TRONG cây của chính file, và ĐẶT được env cho
      `custom_basket` đọc (in ra số dòng + digest để kiểm từ ngoài).
  P2. FAIL-CLOSED thật: đường dẫn không tồn tại ⇒ SystemExit, KHÔNG âm thầm rơi về LIVE BQ.
  P3. Hai lối thoát TƯỜNG MINH còn sống: env trỏ file khác (env thắng) và env RỖNG (khai muốn live).
  P4. Chạy từ WORKTREE thật (data/snapshots CHƯA có vintage) vẫn resolve sang cây canonical —
      nếu không, cổng sẽ chết đúng lúc cần nhất: lúc review một branch trong worktree.

Mỗi câu có MUTATION đi kèm (`--mutations`): cố ý làm hỏng đúng cơ chế đang xét và đòi phép thử
tương ứng PHẢI đỏ.

Chạy:  $DNA_PYEXE pin_resolution_selfcheck.py --mutations
       TZ=America/New_York $DNA_PYEXE pin_resolution_selfcheck.py --mutations
"""
import os
import shutil
import subprocess
import sys
import tempfile

CANON = "/home/trido/thanhdt/WorkingClaude"
# SUT = bản ĐANG SỬA trong worktree (canonical CHƯA có bản vá này — chưa merge, đúng chỉ đạo).
WT = os.path.join(CANON, "mike/agents/Taylor/wt-casnap-2709/WorkingClaude")
SUT = os.path.join(WT, "basket_price_basis_selfcheck.py")
VINTAGE_NAME = "corp_action_share_20260927.parquet"
VINTAGE = os.path.join(CANON, "data", "snapshots", VINTAGE_NAME)
FAILS = []


def check(name, cond, detail=""):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}", flush=True)
    if not cond:
        FAILS.append(name)


def _probe(tree, env_extra=None, mutate=None):
    """Nạp selfcheck từ `tree` trong MỘT process con và trả (rc, stdout+stderr).

    Vì sao process con: `_pin_corp_action_vintage()` GHI vào `os.environ` và module làm
    `os.chdir(WORKDIR)` ngay ở tầng module ⇒ mấy phép thử chạy trong cùng process sẽ nhiễm
    nhau, và "PASS" của phép sau không còn nói về cái nó tưởng mình đang đo.
    """
    code = (
        "import os,sys,importlib.util\n"
        f"spec=importlib.util.spec_from_file_location('bpb', {os.path.join(tree, 'basket_price_basis_selfcheck.py')!r})\n"
        "m=importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        + (mutate or "")
        + "m._pin_corp_action_vintage()\n"
        "print('ENV_AFTER=' + os.environ.get('BASKET_CA_SNAPSHOT','<unset>'))\n"
    )
    env = {k: v for k, v in os.environ.items() if k != "BASKET_CA_SNAPSHOT"}
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def _fake_tree(with_vintage=True):
    """Cây tạm CÓ vintage tại chỗ — để đo nhánh "resolve trong WORKDIR" tách biệt khỏi nhánh
    fallback. Không phải repo git nên `git rev-parse` fail ⇒ chỉ còn ứng viên WORKDIR: đúng
    điều kiện cần cho P1, và cũng chứng minh nhánh `except` không làm sập cổng."""
    d = tempfile.mkdtemp(prefix="pinsc_")
    shutil.copy(SUT, os.path.join(d, "basket_price_basis_selfcheck.py"))
    if with_vintage:
        os.makedirs(os.path.join(d, "data", "snapshots"))
        os.symlink(VINTAGE, os.path.join(d, "data", "snapshots", VINTAGE_NAME))
    return d


def p1_default():
    print("\nP1. Ghim MẶC ĐỊNH — vintage nằm TRONG cây của chính file")
    d = _fake_tree()
    try:
        rc, out = _probe(d)
        check("P1 rc=0", rc == 0, out.strip().splitlines()[-1] if out.strip() else "")
        check("P1 in ra nhãn [pin mặc định] (không phải nhãn fallback)",
              "[pin mặc định]" in out and "cây canonical" not in out)
        want = os.path.join(d, "data", "snapshots", VINTAGE_NAME)
        check("P1 đặt env cho custom_basket đọc", f"ENV_AFTER={want}" in out)
        check("P1 in dấu vết vintage (số dòng ISS+AIS + digest) để kiểm tất định từ ngoài",
              "vintage:" in out and "digest=" in out,
              ([l.strip() for l in out.splitlines() if "vintage:" in l] or [""])[0])
        check("P1 cây không-phải-git vẫn chạy được (nhánh except không làm sập cổng)", rc == 0)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def p2_failclosed():
    print("\nP2. FAIL-CLOSED khi thiếu file (KHÔNG âm thầm rơi về LIVE BQ)")
    bogus = os.path.join(tempfile.gettempdir(), "khong_ton_tai_ca_snapshot.parquet")
    rc, out = _probe(WT, {"BASKET_CA_SNAPSHOT": bogus})
    check("P2a env trỏ file không tồn tại -> rc != 0", rc != 0, f"rc={rc}")
    check("P2a nói FAIL-CLOSED + liệt kê nơi đã tìm + cách sinh lại",
          "FAIL-CLOSED" in out and "Đã tìm" in out and "corp_action_share_snapshot.py" in out)
    d = _fake_tree(with_vintage=False)
    try:
        rc, out = _probe(d)
        check("P2b cây KHÔNG có vintage ở đâu cả -> rc != 0 (không im lặng đọc live)",
              rc != 0, f"rc={rc}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def p3_escapes():
    print("\nP3. Hai lối thoát TƯỜNG MINH")
    rc, out = _probe(WT, {"BASKET_CA_SNAPSHOT": VINTAGE})
    check("P3a env trỏ file thật -> nhãn [env], env THẮNG pin mặc định",
          rc == 0 and "[env]" in out and "[pin mặc định]" not in out, f"rc={rc}")
    rc, out = _probe(WT, {"BASKET_CA_SNAPSHOT": ""})
    check("P3b env RỖNG = khai tường minh muốn LIVE BQ, KHÔNG fail-closed",
          rc == 0 and "LIVE BQ, khai tường minh" in out, f"rc={rc}")
    check("P3b và KHÔNG tự đặt lại env thành vintage (nếu đặt thì 'live' chỉ là lời nói)",
          "ENV_AFTER=" in out and f"ENV_AFTER={VINTAGE}" not in out)


def p4_worktree():
    print("\nP4. Chạy từ WORKTREE thật -> rơi về cây canonical")
    wt_local = os.path.join(WT, "data", "snapshots", VINTAGE_NAME)
    check("P4 tiền đề: worktree THẬT không có vintage tại chỗ (có thì phép thử vô nghĩa)",
          not os.path.exists(wt_local), wt_local)
    rc, out = _probe(WT)
    check("P4 rc=0 từ worktree", rc == 0, out.strip().splitlines()[-1] if out.strip() else "")
    check("P4 resolve sang cây canonical, có NHÃN riêng để người đọc log thấy",
          "cây canonical" in out and VINTAGE in out)
    check("P4 env trỏ vintage canonical", f"ENV_AFTER={VINTAGE}" in out)


# ── MUTATION: làm hỏng đúng cơ chế đang xét, đòi phép thử tương ứng PHẢI đỏ ────────────────
def mutations():
    print("\nMUTATION")
    res = []
    # M1: bỏ fallback canonical (= đúng bản TRƯỚC bản vá này) -> P4 phải sập
    m1 = ("m._ca_snapshot_candidates = lambda: "
          "[m.os.path.join(m.WORKDIR,'data','snapshots',m.CA_SNAPSHOT_NAME)]\n")
    rc, out = _probe(WT, mutate=m1)
    res.append(("M1 bỏ fallback canonical (bản tiền-vá)", rc != 0 and "FAIL-CLOSED" in out,
                f"rc={rc} => P4 đỏ"))
    # M2: exists() luôn True -> fail-closed mất tác dụng
    bogus = os.path.join(tempfile.gettempdir(), "khong_ton_tai_ca_snapshot.parquet")
    rc, out = _probe(WT, {"BASKET_CA_SNAPSHOT": bogus},
                     mutate="m.os.path.exists = lambda p: True\n")
    res.append(("M2 bỏ fail-closed (âm thầm rơi về LIVE BQ)",
                not (rc != 0 and "FAIL-CLOSED" in out), f"rc={rc} => P2a đỏ"))
    # M3: in đẹp nhưng không đặt env -> custom_basket vẫn đọc LIVE
    m3 = ("class _NoSet(dict):\n"
          "    def __setitem__(self,k,v):\n        pass\n"
          "m.os.environ=_NoSet(dict(m.os.environ))\n")
    d = _fake_tree()
    try:
        want = os.path.join(d, "data", "snapshots", VINTAGE_NAME)
        rc, out = _probe(d, mutate=m3)
        res.append(("M3 quên đặt env (log nói ghim, thực tế đọc live)",
                    f"ENV_AFTER={want}" not in out, "=> P1 đỏ"))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # M4: env RỖNG bị coi như chưa set -> lối thoát 'muốn live' biến thành ghim ngầm
    m4 = ("_orig=m._pin_corp_action_vintage\n"
          "def _p():\n"
          "    m.os.environ.pop('BASKET_CA_SNAPSHOT',None) if m.os.environ.get("
          "'BASKET_CA_SNAPSHOT')=='' else None\n"
          "    return _orig()\n"
          "m._pin_corp_action_vintage=_p\n")
    rc, out = _probe(WT, {"BASKET_CA_SNAPSHOT": ""}, mutate=m4)
    res.append(("M4 coi env RỖNG như chưa set (ghim ngầm thay vì đọc live)",
                "LIVE BQ, khai tường minh" not in out, "=> P3b đỏ"))
    killed = 0
    for name, k, detail in res:
        print(f"  [{'killed' if k else 'SURVIVED'}] {name} — {detail}")
        killed += bool(k)
    print(f"  => {killed}/{len(res)} mutation bị giết")
    return killed == len(res)


def main():
    print(f"TZ = {os.environ.get('TZ', '(gỡ hẳn — dùng TZ của host)')} | "
          f"python = {sys.version.split()[0]} | SUT = {SUT}")
    p1_default()
    p2_failclosed()
    p3_escapes()
    p4_worktree()
    ok_mut = True
    if "--mutations" in sys.argv:
        ok_mut = mutations()
    print("\n" + "=" * 70)
    if FAILS or not ok_mut:
        print(f"KẾT QUẢ: FAIL — {', '.join(FAILS) or 'mutation sống sót'}")
        return 1
    print("KẾT QUẢ: PASS (P1 ghim / P2 fail-closed / P3 lối thoát / P4 worktree"
          + (" + mutation" if "--mutations" in sys.argv else "") + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
