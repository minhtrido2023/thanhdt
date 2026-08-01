#!/usr/bin/env python3
"""wakeup_profile_selfcheck.py — selfcheck cho bin/wakeup_profile.py.

Chạy: python3 bin/wakeup_profile_selfcheck.py   (exit 0 = PASS, 1 = FAIL)

Mọi test dựng dữ liệu giả trong tmpdir riêng — KHÔNG đụng bus/jobs/ hay state/ thật.
Test cuối (f) chạy trên dữ liệu THẬT nhưng chỉ với --print (không ghi file).

Nguyên tắc `kb/skills/verify-before-done`: test phải fail được. Mỗi test dưới đây đã
được thử ngược (tạm bỏ logic tương ứng trong wakeup_profile.py) để xác nhận nó đỏ.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wakeup_profile as wp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)


def read_json(path):
    """Đọc JSON, trả None nếu thiếu/hỏng — để test báo FAIL sạch thay vì ném traceback.
    (Phát hiện lúc mutation-test 2026-08-01: mutant 'ghi thẳng vào file đích' làm
    selfcheck chết bằng FileNotFoundError, đúng là bị bắt nhưng đọc không ra vấn đề gì.)"""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def dig(obj, *keys):
    """obj['a']['b'] nhưng trả None thay vì ném KeyError/TypeError."""
    for k in keys:
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def rec(job_id, to, model, effort, started, dur, status="done"):
    r = {"job_id": job_id, "from": "Mike", "to": to,
         "status": status, "started_at": str(int(started)),
         "ended_at": str(int(started + dur))}
    if model:
        r["model"] = model
    if effort:
        r["effort"] = effort
    return r


def write_recs(d, name, records):
    """Ghi nhiều record vào 1 file, nối liền nhau, KHÔNG bọc trong JSON array."""
    with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False))


NOW = 1785000000.0  # thời điểm "bây giờ" cố định — test không phụ thuộc đồng hồ thật
DAY = 86400.0


def test_a_malformed_inputs():
    print("\n(a) file hỏng/rỗng/thiếu field không làm crash, chỉ skip + warn")
    d = tempfile.mkdtemp()
    try:
        open(os.path.join(d, "empty.json"), "w").close()
        with open(os.path.join(d, "broken.json"), "w") as fh:
            fh.write('{"job_id": "x", "to": ')            # JSON cụt
        with open(os.path.join(d, "notdict.json"), "w") as fh:
            fh.write('[1, 2, 3]')                          # đúng JSON, sai kiểu
        with open(os.path.join(d, "nofield.json"), "w") as fh:
            json.dump({"job_id": "y", "to": "Taylor", "status": "done"}, fh)
        with open(os.path.join(d, "badts.json"), "w") as fh:
            json.dump({"job_id": "z", "to": "Taylor", "status": "done",
                       "started_at": "abc", "ended_at": None}, fh)
        with open(os.path.join(d, "notjson.txt"), "w") as fh:
            fh.write("ignore me")                          # sai đuôi → bỏ qua im lặng
        # 8 record tốt để vẫn có 1 bucket ra được
        for i in range(8):
            write_recs(d, f"ok{i}.json",
                       [rec(f"ok{i}", "Taylor", "opus", "high", NOW - DAY, 100 + i)])

        prof, warns = wp.build_profile(d, 6, now=NOW)
        check("không raise exception", True)
        check("bucket tốt vẫn được tính",
              prof["buckets"].get("Taylor|opus|high", {}).get("n") == 8,
              str(prof["buckets"]))
        check("record hỏng KHÔNG lọt vào global_fallback",
              prof["global_fallback"]["n"] == 8,
              f"global n={prof['global_fallback']['n']}")
        check("có warning cho file hỏng/rỗng", len(warns) >= 3,
              f"{len(warns)} warning: {warns[:3]}")
    finally:
        shutil.rmtree(d)


def test_b_min_samples():
    print("\n(b) bucket dưới 8 mẫu KHÔNG xuất hiện trong output")
    d = tempfile.mkdtemp()
    try:
        for i in range(7):   # 7 mẫu — dưới ngưỡng
            write_recs(d, f"small{i}.json",
                       [rec(f"s{i}", "Wendy", "opus", "high", NOW - DAY, 300)])
        for i in range(8):   # 8 mẫu — đúng ngưỡng
            write_recs(d, f"big{i}.json",
                       [rec(f"b{i}", "Spyros", "opus", "high", NOW - DAY, 200)])
        prof, _ = wp.build_profile(d, 6, now=NOW)
        check("bucket n=7 bị loại", "Wendy|opus|high" not in prof["buckets"])
        check("bucket n=8 được giữ (biên bao gồm)",
              prof["buckets"].get("Spyros|opus|high", {}).get("n") == 8)
        check("mẫu bị loại VẪN nằm trong global_fallback",
              prof["global_fallback"]["n"] == 15,
              f"global n={prof['global_fallback']['n']} (kỳ vọng 15)")
    finally:
        shutil.rmtree(d)


def test_c_sliding_window():
    print("\n(c) cửa sổ trượt N tuần — record cũ hơn N tuần KHÔNG được tính")
    d = tempfile.mkdtemp()
    try:
        # 10 record CŨ (10 tuần trước) — duration dài, để nếu lọt vào sẽ thấy rõ
        for i in range(10):
            write_recs(d, f"old{i}.json",
                       [rec(f"o{i}", "Taylor", "opus", "high", NOW - 70 * DAY, 3000)])
        # 8 record MỚI (2 ngày trước) — duration ngắn
        for i in range(8):
            write_recs(d, f"new{i}.json",
                       [rec(f"n{i}", "Taylor", "opus", "high", NOW - 2 * DAY, 100)])

        prof6, _ = wp.build_profile(d, 6, now=NOW)
        b = prof6["buckets"].get("Taylor|opus|high", {})
        check("cửa sổ 6 tuần chỉ đếm 8 record mới", b.get("n") == 8, f"n={b.get('n')}")
        check("median phản ánh record mới (100s), không bị record cũ 3000s kéo",
              b.get("median_s") == 100, f"median={b.get('median_s')}")
        check("global_fallback cũng bị cắt theo cửa sổ",
              prof6["global_fallback"]["n"] == 8)

        # Nới cửa sổ ra 12 tuần → record cũ phải quay lại
        prof12, _ = wp.build_profile(d, 12, now=NOW)
        b12 = prof12["buckets"].get("Taylor|opus|high", {})
        check("cửa sổ 12 tuần đếm cả 18 record", b12.get("n") == 18, f"n={b12.get('n')}")

        # Biên: record đúng ngay mép cutoff (42 ngày - 1h) phải VÀO
        d2 = tempfile.mkdtemp()
        try:
            for i in range(8):
                write_recs(d2, f"edge{i}.json",
                           [rec(f"e{i}", "Mafee", "opus", "high",
                                NOW - 42 * DAY + 3600, 50)])
            pe, _ = wp.build_profile(d2, 6, now=NOW)
            check("record ngay TRONG mép cutoff được tính",
                  pe["buckets"].get("Mafee|opus|high", {}).get("n") == 8)
        finally:
            shutil.rmtree(d2)
    finally:
        shutil.rmtree(d)


def test_d_multi_object_file():
    print("\n(d) parse đúng file chứa NHIỀU JSON object nối liền nhau")
    d = tempfile.mkdtemp()
    try:
        # 1 file duy nhất chứa 3 object dính nhau — nếu parser dùng json.load()
        # thì cả file này bị vứt (Extra data) và bucket sẽ không đủ 8 mẫu.
        write_recs(d, "triple.json", [
            rec("t1", "Winston", "fable", "high", NOW - DAY, 500),
            rec("t2", "Winston", "fable", "high", NOW - DAY, 500),
            rec("t3", "Winston", "fable", "high", NOW - DAY, 500),
        ])
        # + 1 file có 2 object cách nhau bằng newline (biến thể format)
        with open(os.path.join(d, "double.json"), "w") as fh:
            fh.write(json.dumps(rec("t4", "Winston", "fable", "high", NOW - DAY, 500)))
            fh.write("\n")
            fh.write(json.dumps(rec("t5", "Winston", "fable", "high", NOW - DAY, 500)))
            fh.write("\n")
        for i in range(3):   # 3 file 1-object → tổng 8
            write_recs(d, f"single{i}.json",
                       [rec(f"s{i}", "Winston", "fable", "high", NOW - DAY, 500)])

        prof, warns = wp.build_profile(d, 6, now=NOW)
        b = prof["buckets"].get("Winston|fable|high", {})
        check("đọc đủ 8 record từ 5 file (3+2+3 object)", b.get("n") == 8,
              f"n={b.get('n')} — nếu =3 thì parser đang dùng json.load()")
        check("không sinh warning giả cho file multi-object", warns == [], str(warns))

        # Đối chứng: json.load() thuần chỉ lấy được 3 → chứng minh test này phân biệt được
        naive = 0
        for name in os.listdir(d):
            try:
                json.load(open(os.path.join(d, name), encoding="utf-8"))
                naive += 1
            except Exception:
                pass
        check("đối chứng: json.load() thuần chỉ đọc được 3/5 file", naive == 3,
              f"naive={naive}")
    finally:
        shutil.rmtree(d)


def test_e_atomic_write():
    print("\n(e) atomic write — kill giữa chừng không để lại file đích dở dang")
    d = tempfile.mkdtemp()
    try:
        dest = os.path.join(d, "wakeup_profile.json")
        good = {"generated_at": "2026-01-01T00:00:00Z", "buckets": {"a|b|c": {"n": 9}}}
        wp.atomic_write_json(dest, good)
        check("ghi bình thường ra file đọc lại được",
              dig(read_json(dest), "buckets", "a|b|c", "n") == 9)

        # e1: lỗi giữa lúc serialize (mô phỏng crash trong tiến trình)
        class Boom:
            def __repr__(self):  # json.dump sẽ raise TypeError khi gặp object này
                return "boom"
        try:
            wp.atomic_write_json(dest, {"buckets": {"x": Boom()}, "pad": "y" * 5000})
        except TypeError:
            pass
        after = read_json(dest)
        check("file đích GIỮ NGUYÊN bản cũ hợp lệ sau lỗi giữa chừng",
              dig(after, "buckets", "a|b|c", "n") == 9, str(after)[:120])
        orphans = [f for f in os.listdir(d) if ".tmp." in f]
        check("không để lại .tmp mồ côi (đường finally)", orphans == [], str(orphans))

        # e2: SIGKILL thật giữa lúc ghi — finally KHÔNG chạy, chỉ còn bảo đảm
        # "file đích không bao giờ dở dang" (đây mới là bảo đảm Mike phụ thuộc vào).
        script = (
            "import os,sys,signal,json;"
            f"sys.path.insert(0,{os.path.dirname(os.path.abspath(__file__))!r});"
            "import wakeup_profile as wp;"
            f"dest={dest!r};"
            "d=os.path.dirname(dest);"
            "tmp=os.path.join(d,'.'+os.path.basename(dest)+'.tmp.'+str(os.getpid()));"
            "fh=open(tmp,'w');fh.write('{\"buckets\": {\"partial');fh.flush();"
            "os.kill(os.getpid(), signal.SIGKILL)"
        )
        p = subprocess.run([sys.executable, "-c", script], capture_output=True)
        check("tiến trình con thật sự bị SIGKILL", p.returncode == -9,
              f"rc={p.returncode}")
        still = read_json(dest)
        check("file đích VẪN hợp lệ + là bản cũ sau SIGKILL giữa lúc ghi",
              dig(still, "buckets", "a|b|c", "n") == 9, str(still)[:120])
        leftover = [f for f in os.listdir(d) if ".tmp." in f]
        check("nếu SIGKILL để lại .tmp thì tên nó KHÁC file đích (không ai đọc nhầm)",
              all(f != os.path.basename(dest) for f in leftover),
              f"leftover={leftover}")
    finally:
        shutil.rmtree(d)


def test_f_real_data_smoke():
    print("\n(f) smoke test trên dữ liệu THẬT (chỉ --print, không ghi file)")
    p = subprocess.run(
        [sys.executable, os.path.join(ROOT, "bin", "wakeup_profile.py"), "--print"],
        capture_output=True, text=True)
    check("exit code 0", p.returncode == 0, p.stderr[-300:])
    try:
        prof = json.loads(p.stdout)
    except Exception as exc:
        check("stdout là JSON hợp lệ", False, str(exc))
        return
    check("stdout là JSON hợp lệ", True)
    for k in ("generated_at", "window_weeks", "buckets", "global_fallback"):
        check(f"có field {k}", k in prof)
    check("mọi bucket đều có n>=8",
          all(b["n"] >= 8 for b in prof["buckets"].values()))
    check("mọi bucket có key dạng to|model|effort",
          all(k.count("|") == 2 for k in prof["buckets"]))
    gf = prof.get("global_fallback") or {}
    check("global_fallback có mẫu", gf.get("n", 0) > 0, str(gf)[:120])
    check("global_fallback có median_s/p75_s", "median_s" in gf and "p75_s" in gf,
          str(gf)[:120])
    check("median_s <= p75_s ở mọi bucket",
          all(b.get("median_s", 0) <= b.get("p75_s", -1)
              for b in prof["buckets"].values()))
    print(f"      -> {len(prof['buckets'])} bucket, "
          f"global n={gf.get('n')} median={gf.get('median_s')}s")


def main():
    print("=== wakeup_profile_selfcheck ===")
    print(f"ROOT={ROOT}  MIN_SAMPLES={wp.MIN_SAMPLES}  "
          f"MAX_DURATION_S={wp.MAX_DURATION_S}")
    test_a_malformed_inputs()
    test_b_min_samples()
    test_c_sliding_window()
    test_d_multi_object_file()
    test_e_atomic_write()
    test_f_real_data_smoke()
    print()
    if FAILURES:
        print(f"FAIL — {len(FAILURES)} test đỏ: {FAILURES}")
        return 1
    print("PASS — tất cả test xanh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
