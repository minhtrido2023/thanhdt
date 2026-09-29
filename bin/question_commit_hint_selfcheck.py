#!/usr/bin/env python3
"""Selfcheck cho bin/question_commit_hint.py — chạy trên GIT LOG THẬT của 2 repo.

Ca hồi quy #1 là chính sự cố sinh ra công cụ: câu hỏi
`Winston/sell-loanpackage-deal-not-found-zalopay-20260929` (29/09) được sửa bằng commit
d51c735e trên WorkingClaude/main mà không ai ghi event `answer` (Pattern B lần 3). Công cụ
PHẢI chỉ ra được commit đó. Ca #2 chốt chiều ngược lại — báo động giả đã đo thật.
"""
import importlib.util
import io
import os
import subprocess
import sys
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def _mod():
    spec = importlib.util.spec_from_file_location(
        "question_commit_hint", os.path.join(ROOT, "bin", "question_commit_hint.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run(m, pending, argv=()):
    """main() với danh sách pending GIẢ, git log THẬT."""
    real_loader = m._load_hint_module

    class _Hint:
        def __init__(self, inner):
            self._tokens = inner._tokens

        def _pending(self):
            return pending

    m._load_hint_module = lambda: _Hint(real_loader())
    old = sys.argv
    sys.argv = ["question_commit_hint.py"] + list(argv)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = m.main()
    finally:
        sys.argv = old
        m._load_hint_module = real_loader
    return rc, buf.getvalue()


def check(name, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + name + (("  — " + detail) if not cond else ""))
    if not cond:
        FAILS.append(name)


def main():
    m = _mod()
    print("question_commit_hint_selfcheck")

    # 1) HỒI QUY — ca thật 2026-09-29. Chỉ có nghĩa khi commit d51c735e còn trong cửa sổ --days.
    have = subprocess.run(["git", "-C", os.path.dirname(ROOT), "cat-file", "-e", "d51c735e^{commit}"],
                          capture_output=True).returncode == 0
    q = {"agent": "Winston", "topic": "sell-loanpackage-deal-not-found-zalopay-20260929",
         "ts": "2026-09-29T06:35:29Z", "age_days": 0}
    rc, out = _run(m, [q], ["--days", "3650"])
    check("regression: commit d51c735e còn trong repo (không thì ca hồi quy vô nghĩa)", have)
    # Cố ý KHÔNG chốt cứng ĐÚNG sha nào được in: cùng sự cố có cả một CHÙM commit hợp lệ (fix
    # trên WorkingClaude + ghi chú vận hành trên mike). Yêu cầu THẬT là câu hỏi phải được NÊU
    # TÊN kèm một commit của chùm đó — chốt cứng 1 sha là chốt vào thứ tự duyệt repo.
    check("regression: câu hỏi sell-loanpackage được nêu tên trong gợi ý",
          "sell-loanpackage-deal-not-found-zalopay-20260929" in out, out.strip()[:200] or "(rỗng)")
    check("regression: rc=0", rc == 0)

    # 1b) Mức FUNCTION — chính commit sửa d51c735e phải đạt điểm khớp, độc lập với thứ tự duyệt.
    hint = m._load_hint_module()
    tok = hint._tokens(q["topic"])
    hit = [sha for sha, subj, low, flat in m._commits(os.path.dirname(ROOT), 3650)
           if sha.startswith("d51c735e") and m._score(tok, low, flat) >= m._MIN_SCORE]
    check("regression(function): d51c735e đạt ngưỡng khớp trên repo WorkingClaude", bool(hit))

    # 2) PRECISION — lớp câu hỏi mà ngày là token phân biệt duy nhất không được khớp
    #    commit bất kỳ chỉ vì commit đó nhắc cùng ngày (báo động giả 84b7dbd3 đã đo).
    q2 = {"agent": "Wags", "topic": "wags-fix-not-confirmed: coord-2026-09-28",
          "ts": "2026-09-28T06:03:00Z", "age_days": 1}
    rc2, out2 = _run(m, [q2], ["--days", "30"])
    check("precision: topic chỉ-có-ngày KHÔNG khớp commit cùng ngày", out2.strip() == "",
          out2.strip()[:200])
    check("precision: rc=0 và im lặng", rc2 == 0)

    # 3) pending rỗng ⇒ im lặng tuyệt đối (không in tiêu đề rỗng vào prompt dispatch)
    rc3, out3 = _run(m, [])
    check("pending rỗng ⇒ không in gì", out3 == "" and rc3 == 0, repr(out3[:120]))

    # 4) _score: token NGẮN phải theo ranh giới từ; token DÀI được khớp trên bản dẹt.
    tok = {"deal": 1, "loanpackage": 1, "zalopay": 1, "found": 1}
    low = "the dealer idealized founder zalopays loanpackages"
    check("_score: token ngắn không khớp chuỗi con (dealer/founder)",
          m._score({"deal": 1, "found": 1, "abcdefg": 1, "hijklmn": 1}, low, low.replace(" ", "")) == 0)
    check("_score: đủ điểm + 2 token đặc thù ⇒ khớp",
          m._score(tok, "sell deal not found zalopay loanpackage 1826",
                   "selldealnotfoundzalopayloanpackage1826") >= 4)
    check("_score: token dài khớp qua bản dẹt (closerepair ↔ close_repair)",
          m._score({"closerepair": 1, "approval": 1, "needed": 1, "tolerance": 1},
                   "fix(close_repair): approval needed tolerance",
                   "fixcloserepairapprovalneededtolerance") >= 4)
    check("_score: 1 token đặc thù thôi ⇒ KHÔNG khớp (cần 2)",
          m._score({"loanpackage": 1, "deal": 1, "sell": 1, "abcd": 1},
                   "loanpackage deal sell abcd", "loanpackagedealsellabcd") == 0)

    # 3b) META-COMMIT: một commit khớp NHIỀU câu hỏi là commit tài liệu/retro liệt kê topic,
    #     không phải resolver ⇒ bỏ cả cụm. Dùng commit THẬT 85b744a1 (ghi chú vận hành, nhắc cả
    #     sự cố loanpackage lẫn PLACE_FAIL_STOPPED/runbook .proposed).
    qa = {"agent": "Winston", "topic": "sell-loanpackage-deal-not-found-zalopay-20260929",
          "ts": "x", "age_days": 0}
    qb = {"agent": "Wags", "topic": "place-fail-stopped-runbook-proposed-nguong",
          "ts": "x", "age_days": 0}
    _, solo = _run(m, [qb], ["--days", "3650"])
    check("meta-commit(tiền đề): 85b744a1 CÓ khớp khi chỉ 1 câu hỏi treo",
          "85b744a1" in solo, solo.strip()[:160] or "(rỗng)")
    _, both = _run(m, [qa, qb], ["--days", "3650"])
    check("meta-commit: commit khớp 2 câu hỏi bị loại", "85b744a1" not in both,
          both.strip()[:200])

    # 4b) TỰ LOẠI TRỪ: commit sửa chính công cụ này không được tự nhận là resolver của các
    #     câu hỏi mà message của nó lấy làm ví dụ (a9c4a421 — đã xảy ra thật).
    shas = [sha for sha, _s, _l, _f in m._commits(ROOT, 3650)]
    check("self-exclusion: commit chạm question_commit_hint.py bị loại khỏi nguồn quét",
          not any(x.startswith("a9c4a421") for x in shas), str(shas[:5]))

    # 5) FAIL-OPEN: repo không tồn tại ⇒ _commits im lặng trả rỗng, không ném.
    check("_commits: repo rác ⇒ [] chứ không ném", m._commits("/nonexistent-repo-xyz", 7) == [])

    print(("FAIL: %d" % len(FAILS)) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
