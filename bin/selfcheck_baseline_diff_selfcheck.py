#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selfcheck cho bin/selfcheck_baseline_diff.py + phạm vi quét của
bin/selfcheck_weekly_baseline_check.sh (job Wags_20260812_112724).

Cách test: import module thật, thay `bus`/`discord` bằng stub ghi vào list. KHÔNG thêm hook
test nào vào file production.

Mỗi ca "chặn được X" đều có CA CHỨNG MINH NGƯỢC. Bài học Wags 2026-08-12 (fixture làm test
XANH trên code HỎNG): assertion chưa từng chạy trên bản đỏ là assertion chưa biết mình có tác
dụng gì.
"""
import datetime as dt
import fcntl
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MIKE = os.path.dirname(HERE)
WC = os.path.dirname(MIKE)
RUNNER = os.path.join(HERE, "selfcheck_weekly_baseline_check.sh")

_spec = importlib.util.spec_from_file_location("scbd", os.path.join(HERE, "selfcheck_baseline_diff.py"))
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name, ("  — " + detail) if detail else ""))


class H:
    """Một lần chạy diff_and_escalate với bus/discord bị thay bằng stub."""

    def __init__(self, tmp, baseline, statuses, min_files=0):
        self.tmp = tmp
        self.baseline_path = os.path.join(tmp, "baseline.json")
        self.result_path = os.path.join(tmp, "result.json")
        self.jsonl = os.path.join(tmp, "raw.jsonl")
        self.events, self.discords = [], []
        self.min_files = min_files
        with open(self.baseline_path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, ensure_ascii=False) if not isinstance(baseline, str) else f.write(baseline)
        self.set_statuses(statuses)

    def set_statuses(self, statuses):
        with open(self.jsonl, "w", encoding="utf-8") as f:
            for k, v in statuses.items():
                f.write(json.dumps({"file": k, "status": v}) + "\n")

    def run(self):
        M.bus = lambda et, tp, pl: (self.events.append((et, tp, pl)), True)[1]
        M.discord = lambda m: self.discords.append(m)
        return M.diff_and_escalate(self.baseline_path, self.result_path, self.jsonl,
                                   min_files=self.min_files)

    def baseline(self):
        with open(self.baseline_path, encoding="utf-8") as f:
            return json.load(f)

    def result(self):
        with open(self.result_path, encoding="utf-8") as f:
            return json.load(f)

    def topics(self, etype):
        return [t for et, t, _ in self.events if et == etype]


EMPTY_BASE = {"known_red": {}, "required_env": {"default_timeout_s": 150, "slow_files": {}}}


# ────────────────────────────────────────────── [1] phạm vi quét của runner (bash)
print("\n[1] Phạm vi quét THẬT của selfcheck_weekly_baseline_check.sh")
src = open(RUNNER, encoding="utf-8").read()
m = re.search(r"^mapfile -t SC_FILES < <\((.*)\)\s*$", src, re.M)
check("1.1 runner còn dùng glob động (không danh sách chép tay)", bool(m), m.group(1) if m else "KHÔNG THẤY")
if m:
    files = subprocess.run(["bash", "-c", "cd %s && %s" % (WC, m.group(1).strip())],
                           capture_output=True, text=True).stdout.split()
    check("1.2 quét ra >= 85 file", len(files) >= 85, "thấy %d" % len(files))
    check("1.3 KHÔNG file test_*.py nào (§23: 165 script R&D ở gốc KHÔNG phải test)",
          not [f for f in files if os.path.basename(f).startswith("test_")],
          str([f for f in files if os.path.basename(f).startswith("test_")][:3]))
    check("1.4 KHÔNG quét worktree/pending_/exp_ (nhiễu làm chìm ca đỏ thật)",
          not [f for f in files if any(d.startswith(("wt-", "pending_", "exp_", "job_"))
                                       for d in os.path.dirname(f).split("/"))],
          str([f for f in files if "wt-" in f][:3]))
    check("1.5 phủ CẢ 2 gốc (code giao dịch + mike/bin tooling)",
          any("/" not in f for f in files) and any(f.startswith("mike/bin/") for f in files))
    for f in ("extreme_regime_selfcheck.py", "hard_no_chase_ceiling_selfcheck.py",
              "paper_main_window_selfcheck.py", "t2_settlement_selfcheck.py"):
        check("1.6 phủ ca đỏ THẬT của sự cố 08-10: %s" % f, f in files)
    check("1.7 phủ selfcheck tooling fleet (thiếu chúng là lỗ hổng #2 đang vá)",
          "mike/bin/ops_health_check_selfcheck.py" in files)
    # CONTROL: glob "hồn nhiên" *.py ở gốc nuốt >100 script R&D ⇒ 1.3 không phải khẳng định suông
    naive = subprocess.run(["bash", "-c", "cd %s && ls -1 test_*.py | wc -l" % WC],
                           capture_output=True, text=True).stdout.strip()
    check("1.8 CONTROL: có %s file test_*.py ở gốc — glob sai một chữ là nuốt hết" % naive,
          int(naive) > 100, naive)
# Log tạm phải làm phẳng `/` — nếu không, MỌI ca mike/bin thành FAIL giả (redirect vào thư mục
# không tồn tại). Ca này pin đúng dòng đã sửa.
check("1.9 tên log tạm làm phẳng '/' cho đường dẫn mike/bin (nếu không: FAIL giả hàng loạt)",
      '${f//\\//_}' in src, "không thấy phép thay thế trong: %s" %
      [l for l in src.splitlines() if "wk_sc_" in l])


# ────────────────────────────────────────────── [2] đỏ MỚI: escalate đúng 1 lần, không lặp
print("\n[2] Đỏ MỚI ⇒ escalate ĐÚNG 1 LẦN; chạy lại KHÔNG lặp (lỗ hổng L2 đang vá)")
with tempfile.TemporaryDirectory() as td:
    st = {"extreme_regime_selfcheck.py": "FAIL", "hard_no_chase_ceiling_selfcheck.py": "FAIL",
          "paper_main_window_selfcheck.py": "FAIL", "t2_settlement_selfcheck.py": "FAIL",
          "ok1_selfcheck.py": "PASS", "ok2_selfcheck.py": "PASS"}
    h = H(td, dict(EMPTY_BASE), st)
    rc = h.run()
    check("2.1 rc=1 khi có đỏ mới (bash notify chỉ chạy ở rc=1)", rc == 1, "rc=%d" % rc)
    check("2.2 đúng 4 question, 1 ca / 1 question", len(h.topics("question")) == 4,
          str(h.topics("question")))
    check("2.3 mỗi question kèm đúng 1 ack triaged-needs-human (không đốt job Wags mỗi ngày)",
          len([t for t in h.topics("status") if t.startswith(M.ACK_PREFIX)]) == 4)
    check("2.4 topic khoá theo TÊN FILE, không free text (close-the-loop bug B)",
          sorted(h.topics("question")) == sorted(M.TOPIC_PREFIX + f for f in st if st[f] == "FAIL"))
    check("2.5 KHÔNG escalate file PASS",
          not any("ok1" in t or "ok2" in t for t in h.topics("question")))
    kr = h.baseline()["known_red"]
    check("2.6 4 ca đã được GHI vào known_red kèm topic + escalated_utc",
          len(kr) == 4 and all(v.get("topic") and v.get("escalated_utc") and v.get("auto")
                               for v in kr.values()))
    check("2.7 entry auto nói rõ 'CHƯA AI TRIAGE' (không giả vờ là đỏ đã chấp nhận)",
          all("CHƯA AI TRIAGE" in v["reason"] for v in kr.values()))
    check("2.8 Discord gửi 1 tin GỘP (không phải 4 tin)", len(h.discords) == 1)

    n = len(h.events)
    rc2 = h.run()
    check("2.9 lần 2 cùng trạng thái ⇒ 0 event mới", len(h.events) == n,
          "thêm %d" % (len(h.events) - n))
    check("2.10 lần 2 ⇒ 0 tin Discord mới", len(h.discords) == 1)
    check("2.11 lần 2 rc=0 ⇒ bash KHÔNG notify lại", rc2 == 0, "rc=%d" % rc2)
    check("2.12 result.json ghi still_red_known = 4 (vẫn thấy được, chỉ không báo lại)",
          len(h.result()["still_red_known"]) == 4)

# CONTROL: bản CŨ (không ghi known_red) — mô phỏng bằng cách xoá known_red trước lần 2
with tempfile.TemporaryDirectory() as td:
    h = H(td, dict(EMPTY_BASE), {"a_selfcheck.py": "FAIL"})
    h.run()
    b = h.baseline(); b["known_red"] = {}
    with open(h.baseline_path, "w", encoding="utf-8") as f:
        json.dump(b, f)
    h.run()
    check("2.13 CONTROL: không ghi known_red ⇒ escalate LẠI (đúng bug L2 của bản 08-08)",
          len(h.topics("question")) == 2, str(h.topics("question")))


# ────────────────────────────────────────────── [3] xanh trở lại ⇒ tự đóng vòng
print("\n[3] Đỏ → xanh ⇒ gỡ baseline + tự đóng câu hỏi cũ kèm bằng chứng (close-the-loop A)")
with tempfile.TemporaryDirectory() as td:
    h = H(td, dict(EMPTY_BASE), {"x_selfcheck.py": "FAIL", "y_selfcheck.py": "FAIL"})
    h.run()
    q_topic = M.TOPIC_PREFIX + "x_selfcheck.py"
    h.set_statuses({"x_selfcheck.py": "PASS", "y_selfcheck.py": "FAIL"})
    h.run()
    ans = [(t, p) for et, t, p in h.events if et == "answer"]
    check("3.1 đúng 1 answer cho ca đã xanh", len(ans) == 1, str([t for t, _ in ans]))
    check("3.2 topic answer CHỨA NGUYÊN topic câu hỏi ⇒ khớp _resolved() của ops_health_check "
          "(r == q hoặc q in r)", q_topic in ans[0][0], ans[0][0])
    check("3.3 answer kèm artifact chạy lại, không phải self-report",
          "artifact" in ans[0][1] and "PASS" in ans[0][1]["artifact"])
    check("3.4 answer ghi decided_by (§20: phân biệt automation với người quyết)",
          "decided_by" in ans[0][1])
    check("3.5 x gỡ khỏi known_red, y vẫn còn",
          "x_selfcheck.py" not in h.baseline()["known_red"]
          and "y_selfcheck.py" in h.baseline()["known_red"])
    check("3.6 KHÔNG đóng oan ca y", not any("y_selfcheck" in t for t, _ in ans))
    # CONTROL: topic answer viết khác kiểu thì _resolved KHÔNG khớp ⇒ 3.2 có ý nghĩa
    check("3.7 CONTROL: 'recovered: x_selfcheck.py' KHÔNG chứa topic gốc ⇒ không đóng được",
          q_topic not in "recovered: x_selfcheck.py")

print("\n[3b] Entry known_red do NGƯỜI curate: không escalate, xanh lại chỉ gỡ (không đăng answer)")
with tempfile.TemporaryDirectory() as td:
    human = {"known_red": {"immutable_publish_selfcheck.py": {
        "reason": "IAM: thiếu bigquery.tables.create", "since": "2026-08-08",
        "verified_by": "Mike, 2026-08-08"}}}
    h = H(td, human, {"immutable_publish_selfcheck.py": "FAIL", "a_selfcheck.py": "PASS"})
    rc = h.run()
    check("3b.1 entry người curate đang đỏ ⇒ 0 event, rc=0", h.events == [] and rc == 0, "rc=%d" % rc)
    h.set_statuses({"immutable_publish_selfcheck.py": "PASS", "a_selfcheck.py": "PASS"})
    h.run()
    check("3b.2 xanh lại ⇒ gỡ khỏi known_red", not h.baseline()["known_red"])
    check("3b.3 KHÔNG đăng answer (ta chưa từng hỏi câu nào cho ca này)",
          not [t for et, t, _ in h.events if et == "answer"], str(h.events))


# ────────────────────────────────────────────── [4] anti-empty-scan
print("\n[4] Quét rỗng/thiếu ⇒ KHÔNG kết luận, KHÔNG đụng baseline (bảo vệ trí nhớ known_red)")
with tempfile.TemporaryDirectory() as td:
    base = {"known_red": {"a_selfcheck.py": {"reason": "đã biết", "since": "2026-08-01"}}}
    h = H(td, dict(base), {"only_one_selfcheck.py": "PASS"}, min_files=60)
    rc = h.run()
    check("4.1 rc=2 (khác hẳn rc=1 'có đỏ mới')", rc == 2, "rc=%d" % rc)
    check("4.2 known_red GIỮ NGUYÊN — không bị 'mọi ca đều xanh' xoá sạch",
          h.baseline()["known_red"] == base["known_red"], str(h.baseline()["known_red"]))
    check("4.3 KHÔNG event nào lên bus", h.events == [])
    check("4.4 CÓ báo Discord, nói rõ 'KHÔNG kết luận gì'",
          len(h.discords) == 1 and "KHÔNG kết luận" in h.discords[0], str(h.discords))
    check("4.5 KHÔNG ghi result.json (không đóng băng một kết luận sai)",
          not os.path.exists(h.result_path))
# CONTROL cho [4]: hại THẬT của một lần quét cụt là "xanh giả" — file known_red LỌT vào tập
# cụt và tình cờ PASS ⇒ bị gỡ khỏi baseline + đăng answer "đã hồi phục" cho một lần quét không
# đại diện. (Ghi chú: file KHÔNG có trong kết quả thì code giữ nguyên trong known_red — đã kiểm
# ở 4.2; guard bịt đúng nhánh xanh-giả này, không phải nhánh vắng-mặt.)
with tempfile.TemporaryDirectory() as td:
    base = {"known_red": {"a_selfcheck.py": {"reason": "đã biết", "since": "2026-08-01",
                                             "auto": True, "topic": M.TOPIC_PREFIX + "a_selfcheck.py"}}}
    h = H(td, json.loads(json.dumps(base)), {"a_selfcheck.py": "PASS"}, min_files=0)
    h.run()
    check("4.6 CONTROL: bỏ guard ⇒ quét cụt 1 file làm known_red bị gỡ + đăng answer 'đã hồi "
          "phục' GIẢ (đúng lỗ hổng guard đang bịt)",
          h.baseline()["known_red"] == {} and len([t for et, t, _ in h.events if et == "answer"]) == 1,
          str(h.baseline()["known_red"]))
with tempfile.TemporaryDirectory() as td:
    base = {"known_red": {"a_selfcheck.py": {"reason": "đã biết", "since": "2026-08-01",
                                             "auto": True, "topic": M.TOPIC_PREFIX + "a_selfcheck.py"}}}
    h = H(td, json.loads(json.dumps(base)), {"a_selfcheck.py": "PASS"}, min_files=60)
    rc = h.run()
    check("4.7 CÓ guard ⇒ đúng ca đó KHÔNG bị gỡ, KHÔNG đăng answer giả",
          rc == 2 and h.baseline()["known_red"] and h.events == [],
          "rc=%d known_red=%s" % (rc, list(h.baseline()["known_red"])))


# ────────────────────────────────────────────── [5] bus lỗi / kill giữa chừng
print("\n[5] Đăng bus hỏng hoặc bị kill ⇒ KHÔNG đánh dấu đã escalate (không nuốt cảnh báo, §5)")
with tempfile.TemporaryDirectory() as td:
    h = H(td, dict(EMPTY_BASE), {"a_selfcheck.py": "FAIL"})
    M.bus = lambda et, tp, pl: False
    M.discord = lambda m: h.discords.append(m)
    rc = M.diff_and_escalate(h.baseline_path, h.result_path, h.jsonl, min_files=0)
    check("5.1 đăng hỏng ⇒ KHÔNG ghi known_red (lần sau thử lại)",
          h.baseline()["known_red"] == {}, str(h.baseline()["known_red"]))
    check("5.2 rc vẫn = 1 (vẫn có đỏ mới chưa báo được — không được báo 'sạch')", rc == 1)
    check("5.3 result.json nêu rõ ca KHÔNG đăng được", h.result()["escalated"] == []
          and "a_selfcheck.py" in h.result()["new_red"])
with tempfile.TemporaryDirectory() as td:
    h = H(td, dict(EMPTY_BASE), {"a_selfcheck.py": "FAIL", "b_selfcheck.py": "FAIL",
                                 "c_selfcheck.py": "FAIL"})
    n = {"i": 0}

    def killer(et, tp, pl):
        if et == "question":
            n["i"] += 1
            if n["i"] == 2:
                raise KeyboardInterrupt("mô phỏng bị kill")
        h.events.append((et, tp, pl))
        return True

    M.bus = killer
    M.discord = lambda m: h.discords.append(m)
    try:
        M.diff_and_escalate(h.baseline_path, h.result_path, h.jsonl, min_files=0)
    except KeyboardInterrupt:
        pass
    kr = h.baseline()["known_red"]
    check("5.4 ca đã báo xong ĐÃ nằm trong known_red (không báo lại lần sau)",
          "a_selfcheck.py" in kr, str(list(kr)))
    check("5.5 ca chưa kịp báo KHÔNG bị đánh dấu (lần sau vẫn báo)",
          "b_selfcheck.py" not in kr and "c_selfcheck.py" not in kr)
    check("5.6 baseline không bị cụt/hỏng sau khi kill (ghi nguyên tử)",
          isinstance(kr, dict) and "known_red" in h.baseline())


# ────────────────────────────────────────────── [6] TIMEOUT cũng là đỏ
print("\n[6] TIMEOUT được xử như ĐỎ (một selfcheck treo = một guard không bảo vệ gì)")
with tempfile.TemporaryDirectory() as td:
    h = H(td, dict(EMPTY_BASE), {"slow_selfcheck.py": "TIMEOUT", "ok_selfcheck.py": "PASS"})
    rc = h.run()
    check("6.1 TIMEOUT ⇒ escalate", h.topics("question") == [M.TOPIC_PREFIX + "slow_selfcheck.py"])
    check("6.2 known_red ghi đúng status TIMEOUT (phân biệt với FAIL khi triage)",
          h.baseline()["known_red"]["slow_selfcheck.py"]["status"] == "TIMEOUT")


# ────────────────────────────────────────────── [7] ACK_PREFIX đồng bộ với consumer
print("\n[7] Chuỗi giao ước với ops_health_check.sh phải khớp NGUYÊN VĂN")
ohc = open(os.path.join(HERE, "ops_health_check.sh"), encoding="utf-8").read()
m2 = re.search(r'^ACK_PREFIX\s*=\s*"([^"]+)"', ohc, re.M)
check("7.1 tìm được ACK_PREFIX trong ops_health_check.sh", bool(m2), m2.group(1) if m2 else "")
if m2:
    check("7.2 ACK_PREFIX khớp (lệch 1 khoảng trắng = ack vô hiệu, escalation lặp âm thầm)",
          M.ACK_PREFIX.strip() == m2.group(1).strip(),
          "diff=%r vs %r" % (M.ACK_PREFIX, m2.group(1)))
check("7.3 ops_health_check đọc ĐÚNG baseline mà diff ghi (kb/selfcheck_baseline.json)",
      "selfcheck_baseline.json" in ohc)
check("7.4 topic Discord dùng TÊN registry, không hardcode ID số",
      M.DISCORD_CHANNEL == "architecture" and not M.DISCORD_CHANNEL.isdigit())


# ────────────────────────────────────────────── [8] Khoá chống chạy-song-song (CHẠY THẬT)
# Vì sao có mục này: "escalate đúng 1 lần" ở tầng Python chỉ đúng khi hai lần quét KHÔNG đọc
# baseline cùng lúc. Ngày 2026-08-12 đã có thật 2 lần quét chồng nhau (12:08Z/12:15Z) — thoát nạn
# chỉ nhờ chúng cách nhau 7'. Khoá là thứ biến "may" thành "bảo đảm", nên nó phải được TEST BẰNG
# CHẠY THẬT, không phải bằng đọc code (guideline §4: văn bản mô tả không tự chứng minh hành vi).
print("\n[8] Khoá chống 2 lần quét chồng nhau — chạy thật script bash, không đọc code")
SWEEP = os.path.join(HERE, "selfcheck_weekly_baseline_check.sh")
check("8.1 script quét vẫn tồn tại đúng chỗ", os.path.exists(SWEEP))

# 8.2-8.4 — khoá ĐANG BỊ GIỮ ⇒ bỏ lượt, và tuyệt đối KHÔNG được quét (quét = đã vào vùng tranh chấp).
#
# HERMETIC BẮT BUỘC, KHÔNG PHẢI CHO SẠCH SẼ — chính file selfcheck NÀY nằm trong phạm vi quét của
# bộ quét (glob `mike/bin/*_selfcheck.py`, file #65/93). Bản đầu giữ khoá PRODUCTION rồi gọi runner
# thật; khi bộ quét chạy nó, bộ quét ĐANG giữ fd 9 trên đúng lockfile đó suốt ~20' ⇒ `flock` ở đây
# block vô hạn ⇒ `finally: holder.wait()` block mãi ⇒ DEADLOCK. Tái lập thật 2026-08-12: rc=124
# sau 40s. Hậu quả: bộ quét ghi TIMEOUT cho chính selfcheck của mình ⇒ escalate một ca đỏ VĨNH VIỄN
# (chỉ PASS khi chạy standalone, nên không bao giờ tự xanh) + để lại flock mồ côi.
# ⇒ Mọi tài nguyên toàn cục (khoá, logs, baseline) phải nằm trong tmpdir RIÊNG, y như 8.5-8.7.
lr = tempfile.mkdtemp(prefix="sc_lockheld_")
holder = None
try:
    os.makedirs(os.path.join(lr, "bin")); os.makedirs(os.path.join(lr, "logs"))
    os.makedirs(os.path.join(lr, "kb"))      # để trống: nếu KHÔNG bỏ lượt thì FATAL thiếu baseline
    shutil.copy(SWEEP, os.path.join(lr, "bin"))
    lockfile = os.path.join(lr, "logs", ".selfcheck_sweep.lock")
    # GIỮ KHOÁ NGAY TRONG TIẾN TRÌNH NÀY, không đẻ tiến trình phụ: `flock -c "sleep N"` để lại
    # tiến trình mồ côi nếu bị giết đúng lúc chưa fork xong — mỗi ngày một cái, và chính "flock mồ
    # côi" là một phần tác hại của bug F1. fcntl không có cửa đó, cũng không cần chờ-tới-khi-cầm-được.
    # Con cháu KHÔNG kế thừa fd này (close_fds mặc định True) ⇒ runner con thấy khoá đang bị giữ THẬT.
    holder = open(lockfile, "a")
    fcntl.flock(holder, fcntl.LOCK_EX)
    env = dict(os.environ, SC_LOCK_WAIT_S="3")
    t0 = time.time()
    p = subprocess.run(["bash", os.path.join(lr, "bin", os.path.basename(SWEEP))],
                       capture_output=True, text=True, timeout=90, env=env)
    dur = time.time() - t0
    out = p.stdout + p.stderr
    check("8.2 khoá bị giữ ⇒ BỎ LƯỢT (exit 0, không coi là lỗi)", p.returncode == 0 and "BỎ LƯỢT" in out,
          "rc=%d %.0fs" % (p.returncode, dur))
    check("8.3 bỏ lượt ⇒ KHÔNG hề bắt đầu quét (không có dòng 'Phạm vi')", "Phạm vi" not in out)
    check("8.4 bỏ lượt nhanh theo SC_LOCK_WAIT_S, không treo tới hết 300s", dur < 30, "%.0fs" % dur)
finally:
    if holder is not None:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()
    shutil.rmtree(lr, ignore_errors=True)

# 8.8 — CHỐNG TÁI PHÁT, E2E ĐÚNG ĐƯỜNG PRODUCTION CHẠY.
# Bài học 2026-08-12 (gate commit-collision): classifier XANH + wrapper XANH vẫn không bằng E2E.
# Ở đây cũng vậy — 8.2-8.4 XANH y hệt nhau dù chạy standalone hay đang deadlock-under-sweep, nên
# hành vi đúng của chúng KHÔNG tự bảo vệ được chính chúng. Ca duy nhất bắt được lỗi là chạy CHÍNH
# file này trong đúng điều kiện bộ quét chạy nó: khoá production ĐANG BỊ GIỮ.
# Chống đệ quy vô hạn bằng SC_SELF_UNDER_LOCK: tiến trình con chạy mọi mục KHÁC (gồm 8.2-8.4 — chỗ
# deadlock) nhưng bỏ chính ca 8.8.
if os.environ.get("SC_SELF_UNDER_LOCK") == "1":
    print("  [skip] 8.8 (đang là tiến trình con của chính ca 8.8)")
else:
    _prod_lock = os.path.join(os.path.dirname(HERE), "logs", ".selfcheck_sweep.lock")
    # Mở "a" chứ KHÔNG "w": "w" sẽ TRUNCATE file khoá production. Giữ bằng fcntl trong chính tiến
    # trình này (không đẻ tiến trình phụ ⇒ không thể để lại flock mồ côi).
    # LOCK_NB = KHÔNG xếp hàng: mượn được ⇒ không có bộ quét thật nào đang chạy ⇒ an toàn để thử.
    # Tiến trình con KHÔNG kế thừa fd (close_fds mặc định True) ⇒ nó thấy khoá bị giữ THẬT.
    _probe = open(_prod_lock, "a")
    try:
        fcntl.flock(_probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _got = True
    except OSError:
        _got = False
    if not _got:
        # Không mượn được khoá = bộ quét THẬT đang chạy. Nói TO là đã bỏ ca, không im lặng xanh.
        _probe.close()
        check("8.8 [BỎ QUA] không mượn được khoá production — bộ quét thật đang chạy, không thử E2E",
              True, "chạy lại lúc rảnh để có bằng chứng E2E")
    else:
        try:
            _t0 = time.time()
            _child = subprocess.run([sys.executable, os.path.abspath(__file__)],
                                    capture_output=True, text=True, timeout=150,
                                    env=dict(os.environ, SC_SELF_UNDER_LOCK="1"))
            _cd = time.time() - _t0
            check("8.8 chạy CHÍNH file này khi khoá production ĐANG BỊ GIỮ ⇒ vẫn xong, không "
                  "deadlock (bộ quét chạy nó trong đúng điều kiện này)",
                  _child.returncode == 0, "rc=%d %.0fs" % (_child.returncode, _cd))
        except subprocess.TimeoutExpired:
            check("8.8 chạy CHÍNH file này khi khoá production ĐANG BỊ GIỮ ⇒ vẫn xong, không "
                  "deadlock (bộ quét chạy nó trong đúng điều kiện này)", False,
                  "TREO >150s = đúng bug F1 đã tái phát")
        finally:
            fcntl.flock(_probe, fcntl.LOCK_UN)
            _probe.close()

# 8.5-8.7 — KHÔNG mở nổi file khoá: phải KÊU TO + CHẠY TIẾP, tuyệt đối không im lặng bỏ lượt.
# Đây là bug THẬT bản đầu mắc phải (gộp 2 nhánh) — fd hỏng làm cả bộ quét im lặng exit 0, cron
# báo thành công mà không ai quét: tái tạo đúng sự cố 4-selfcheck-đỏ-2-ngày mà cơ chế này chống.
fr = tempfile.mkdtemp(prefix="sc_lock_")
try:
    os.makedirs(os.path.join(fr, "bin")); os.makedirs(os.path.join(fr, "logs"))
    os.makedirs(os.path.join(fr, "kb"))          # CỐ Ý để trống: thiếu baseline ⇒ FATAL exit 2
    shutil.copy(SWEEP, os.path.join(fr, "bin"))
    os.chmod(os.path.join(fr, "logs"), 0o500)    # không ghi được ⇒ exec 9> thất bại
    p2 = subprocess.run(["bash", os.path.join(fr, "bin", os.path.basename(SWEEP))],
                        capture_output=True, text=True, timeout=90)
    out2 = p2.stdout + p2.stderr
    check("8.5 fd khoá hỏng ⇒ kêu to (không nuốt)", "KHÔNG mở được file khoá" in out2)
    check("8.6 fd khoá hỏng ⇒ KHÔNG im lặng bỏ lượt (đó là bug bản đầu)", "BỎ LƯỢT" not in out2)
    check("8.7 fd khoá hỏng ⇒ CHẠY TIẾP tới tầng kiểm tra sau, rc≠0 (không báo thành công giả)",
          "FATAL" in out2 and p2.returncode != 0, "rc=%d" % p2.returncode)
finally:
    os.chmod(os.path.join(fr, "logs"), 0o700)
    shutil.rmtree(fr, ignore_errors=True)


# ────────────────────────────────────────────── [9] ACK hỏng phải THỬ LẠI (F2)
# Vì sao: ack là thứ DUY NHẤT ngăn ops_health_check thấy question treo ⇒ COORD_WARN ⇒ dispatch
# job Wags ~2 lần/ngày MÃI MÃI cho việc Wags bị CẤM làm (sửa logic giao dịch). Bản đầu bỏ qua giá
# trị trả về của ack: question OK + ack hỏng ⇒ vẫn ghi known_red ⇒ KHÔNG BAO GIỜ có lượt thử lại.
# Đây là lỗi IM LẶNG — không có dòng log nào, chỉ có một vòng lặp báo động giả không hồi kết.
print("\n[9] ACK thất bại ⇒ ghi nợ + THỬ LẠI lượt sau (không nuốt, không lặp báo động giả)")
with tempfile.TemporaryDirectory() as td:
    h = H(td, json.loads(json.dumps(EMPTY_BASE)), {"a_selfcheck.py": "FAIL"})

    def q_ok_ack_fail(et, tp, pl):
        if et == "status" and tp.startswith(M.ACK_PREFIX):
            return False              # ack hỏng, câu hỏi thành công — đúng tổ hợp bản đầu bỏ lọt
        h.events.append((et, tp, pl))
        return True

    M.bus = q_ok_ack_fail
    M.discord = lambda m: h.discords.append(m)
    M.diff_and_escalate(h.baseline_path, h.result_path, h.jsonl, min_files=0)
    e = h.baseline()["known_red"].get("a_selfcheck.py", {})
    check("9.1 câu hỏi ĐÃ đăng ⇒ vẫn ghi known_red (không đăng lại câu hỏi trùng)", bool(e))
    check("9.2 ack hỏng ⇒ ghi nợ ack_pending=True (bản đầu: mất dấu vĩnh viễn)",
          e.get("ack_pending") is True, "ack_pending=%r" % e.get("ack_pending"))

    # lượt sau: bus lành lại ⇒ phải TỰ đăng lại ack, và KHÔNG đăng lại câu hỏi
    h.events.clear()
    M.bus = lambda et, tp, pl: (h.events.append((et, tp, pl)), True)[1]
    M.diff_and_escalate(h.baseline_path, h.result_path, h.jsonl, min_files=0)
    e2 = h.baseline()["known_red"]["a_selfcheck.py"]
    acks = [t for et, t, _ in h.events if et == "status" and t.startswith(M.ACK_PREFIX)]
    check("9.3 lượt sau TỰ đăng lại ack còn nợ", len(acks) == 1, str(acks))
    check("9.4 ack đăng lại ĐÚNG topic đã lưu (không dựng lại chuỗi — bug B close-the-loop)",
          acks == [M.ACK_PREFIX + e2["topic"]] if acks else False)
    check("9.5 xoá nợ sau khi đăng được (không retry mãi)", e2.get("ack_pending") is False)
    check("9.6 KHÔNG đăng lại câu hỏi trùng ở lượt retry",
          not [t for et, t, _ in h.events if et == "question"],
          str([t for et, t, _ in h.events if et == "question"]))

with tempfile.TemporaryDirectory() as td:
    # CONTROL NGƯỢC: ack hỏng LIÊN TỤC thì nợ phải CÒN NGUYÊN (không tự xoá vì "đã thử rồi").
    h = H(td, json.loads(json.dumps(EMPTY_BASE)), {"a_selfcheck.py": "FAIL"})
    M.bus = lambda et, tp, pl: not (et == "status" and tp.startswith(M.ACK_PREFIX))
    M.discord = lambda m: None
    M.diff_and_escalate(h.baseline_path, h.result_path, h.jsonl, min_files=0)
    M.diff_and_escalate(h.baseline_path, h.result_path, h.jsonl, min_files=0)
    check("9.7 CONTROL: ack hỏng mãi ⇒ nợ VẪN còn (không im lặng bỏ cuộc)",
          h.baseline()["known_red"]["a_selfcheck.py"].get("ack_pending") is True)

with tempfile.TemporaryDirectory() as td:
    # Đường XANH bình thường: ack chạy ngon thì không để lại nợ nào.
    h = H(td, json.loads(json.dumps(EMPTY_BASE)), {"a_selfcheck.py": "FAIL"})
    h.run()
    check("9.8 ack thành công ⇒ ack_pending=False, không sinh việc thừa cho lượt sau",
          h.baseline()["known_red"]["a_selfcheck.py"].get("ack_pending") is False)


# ────────────────────────────────────────────── tổng kết
fails = [n for n, ok, _ in RESULTS if not ok]
print("\n" + "=" * 84)
print("  KẾT QUẢ: %d/%d PASS" % (len(RESULTS) - len(fails), len(RESULTS)))
if fails:
    print("  FAIL: %s" % fails)
print("=" * 84)
sys.exit(1 if fails else 0)
