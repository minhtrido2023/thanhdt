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
import shutil
import subprocess
import sys
import tempfile
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


def _git_repo(path, commits):
    """[(subject, body, [file,...])] -> repo git thật ở path (docs-only khi files rỗng)."""
    os.makedirs(path)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x")
    subprocess.run(["git", "init", "-q", path], check=True, env=env)
    for subj, body, files in commits:
        for f in files:
            fp = os.path.join(path, f)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "a") as fh:
                fh.write("x\n")
            subprocess.run(["git", "-C", path, "add", f], check=True, env=env)
        subprocess.run(["git", "-C", path, "commit", "-q", "--allow-empty", "-m", subj,
                        "-m", body], check=True, env=env)


_FIX_CODE_SUBJ = "fix(execution): lệnh BÁN dùng gói vay của DEAL THẬT + dừng retry PLACE_FAIL lỗi cấu trúc"
_FIX_CODE_BODY = ("Incident: kb/incidents/2026-09/2026-09-29-zalopay-sell-deal-not-found-loanpackage-1826.md\n"
                  "Thêm _resolve_sell_loan_package_id: gộp sellable theo gói của chính mã đó; "
                  "mọi lệnh bán ZaloPay mang gói 1258 nên DNSE trả deal not found.")
_FIX_DOCS_SUBJ = "docs(ops): lý do cho 2 file của Taylor bị cuốn vào a9c4a421"
_FIX_DOCS_BODY = ("Commit rỗng — GHI LẠI lý do. Lý do thay đổi (incident "
                  "zalopay-sell-deal-not-found-loanpackage-1826): PLACE_FAIL_STOPPED vào tập "
                  "concerning. Kèm WorkingClaude d51c735e.")


def fixture_cases(m):
    tmp = tempfile.mkdtemp(prefix="qch_fixture_")
    real_repos = m.REPOS
    try:
        mike, wc = os.path.join(tmp, "mike"), os.path.join(tmp, "WorkingClaude")
        _git_repo(mike, [(_FIX_DOCS_SUBJ, _FIX_DOCS_BODY, [])])
        _git_repo(wc, [(_FIX_CODE_SUBJ, _FIX_CODE_BODY, ["trading_bot/brokers.py"])])
        m.REPOS = [mike, wc]          # mike TRƯỚC: đúng thứ tự đã gây chọn nhầm ở v2
        q = {"agent": "Winston", "topic": "sell-loanpackage-deal-not-found-zalopay-20260929",
             "ts": "x", "age_days": 0}
        _rc, out = _run(m, [q])       # --days MẶC ĐỊNH
        code_sha = subprocess.run(["git", "-C", wc, "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
        docs_sha = subprocess.run(["git", "-C", mike, "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
        check("fixture(--days mặc định): commit SỬA THẬT được in ra", code_sha in out,
              out.strip()[:300] or "(rỗng)")
        check("fixture: commit sửa code đứng TRƯỚC commit ghi chú (hết bias thứ tự repo)",
              docs_sha in out and out.index(code_sha) < out.index(docs_sha), out.strip()[:300])
        check("fixture: commit rỗng/docs-only được dán nhãn docs", "/docs/" in out,
              out.strip()[:200])

        # META: commit khớp TỪ 3 câu hỏi ⇒ bỏ; khớp 2 câu hỏi họ hàng ⇒ GIỮ (luật cũ
        # `!= 1` xoá luôn gợi ý đúng khi có câu hỏi họ hàng treo — chính bug arch-review bắt).
        # Cả 2 topic phụ PHẢI khớp CHÍNH commit code (đã đo: 5 và 6 điểm) — nếu chọn topic chỉ
        # khớp commit docs thì ca ">=3 bị loại" đậu vì lý do sai (commit code mới khớp 2).
        qb = {"agent": "Wags", "topic": "brokers-resolve-sell-loan-package-sellable",
              "ts": "x", "age_days": 0}
        qc = {"agent": "Wags", "topic": "resolve-sell-loan-package-id-sellable-zalopay",
              "ts": "x", "age_days": 0}
        _rc, out2 = _run(m, [q, qb])
        check("meta: commit khớp 2 câu hỏi họ hàng vẫn được GIỮ", code_sha in out2,
              out2.strip()[:300] or "(rỗng)")
        # CAP: 3 commit khớp 1 câu hỏi ⇒ in 2, và PHẢI NÓI RA còn 1 (im lặng thì người đọc
        # tưởng chỉ có 2 ứng viên — đúng cách d51c735e biến mất ở vòng 2).
        _git_repo(os.path.join(tmp, "third"), [(_FIX_CODE_SUBJ, _FIX_CODE_BODY, ["x.py"])])
        m.REPOS = [mike, wc, os.path.join(tmp, "third")]
        _rc, outc = _run(m, [q])
        check("cap: 3 ứng viên ⇒ in 2 và NÓI RA còn 1",
              outc.count("[có thể/") == 2 and "còn 1 ứng viên" in outc, outc.strip()[:400])
        m.REPOS = [mike, wc]

        _rc, out3 = _run(m, [q, qb, qc])
        check("meta: commit khớp >=3 câu hỏi bị loại (commit tài liệu/retro liệt kê topic)",
              code_sha not in out3, out3.strip()[:300])
    finally:
        m.REPOS = real_repos
        shutil.rmtree(tmp, ignore_errors=True)


def wired_into_wags_autofix():
    """Fail-open TUYỆT ĐỐI + im lặng = cơ chế có thể chết âm thầm mà không ai biết. Chốt duy
    nhất là ghim call site lại (tiền lệ production_manifest.py:418 từng xoá mất cả một dòng
    gọi). Mẫu lấy từ dispatch_question_hint_selfcheck.py:160."""
    src = open(os.path.join(ROOT, "bin", "wags_autofix.sh"), encoding="utf-8").read()
    calls = [ln for ln in src.splitlines()
             if "bin/question_commit_hint.py" in ln and not ln.strip().startswith("#")]
    check("wags_autofix.sh còn gọi bin/question_commit_hint.py", len(calls) == 1, str(calls))
    check("lời gọi fail-open tại call site (|| true)",
          all("|| true" in c for c in calls), str(calls))
    check("lời gọi có timeout (thống nhất dispatch.sh:1612/:1732, nằm foreground trước setsid)",
          all("timeout " in c for c in calls), str(calls))
    check("hint THẬT SỰ đi vào prompt dispatch (${COMMIT_HINT:+...})",
          "${COMMIT_HINT:+" in src, "không thấy trong wags_autofix.sh")


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
    hit = [c[0] for c in m._commits(os.path.dirname(ROOT), 3650)
           if c[0].startswith("d51c735e") and m._score(tok, c[2], c[3]) >= m._MIN_SCORE]
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
    # arch-review vòng 3 nit: bản cũ dùng token abcdefg/hijklmn KHÔNG có trong text nên _MIN_SCORE
    # chặn trước và guard len(t)>=_FLAT_LEN chưa bao giờ bị thử (mutant bỏ guard vẫn SỐNG). Bộ
    # token dưới đây có đủ 2 token đặc thù CÓ MẶT trong text: HEAD=0đ, bỏ guard ⇒ 5đ.
    _short = "chore: dealer idealized founder zalopays loanpackages upselling"
    check("_score: token ngắn không khớp chuỗi con (dealer/founder/zalopays)",
          m._score({"sell": 1, "loanpackage": 1, "deal": 1, "found": 1, "zalopay": 1},
                   _short, _short.replace(" ", "").replace(":", "")) == 0)
    check("_score: token ngắn không khớp chuỗi con — bản cũ (abcdefg/hijklmn)",
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

    # 1c) GIT LOG THẬT, cửa sổ = TUỔI(d51c735e)+1 ngày. arch-review vòng 2: fixture 2 repo × 1
    #     commit đã loại sẵn đúng cái gây lỗi (nhiều commit code HOÀ ĐIỂM rồi bị cap cắt theo
    #     thứ tự repo). Cửa sổ theo tuổi commit thì KHÔNG rot mà cũng KHÔNG nới lỏng: nó luôn là
    #     cửa sổ nhỏ nhất còn chứa commit đó, và ứng viên cạnh tranh chỉ TĂNG theo thời gian.
    age = subprocess.run(["git", "-C", os.path.dirname(ROOT), "log", "-1", "--format=%cr",
                          "d51c735e"], capture_output=True, text=True).stdout.strip()
    days_ago = subprocess.run(
        ["git", "-C", os.path.dirname(ROOT), "log", "-1", "--format=%ct", "d51c735e"],
        capture_output=True, text=True).stdout.strip()
    import time as _time
    # max(14, tuổi+1): hôm nay = ĐÚNG cửa sổ MẶC ĐỊNH (arch-review vòng 2 đòi chốt ở đó); khi
    # commit già hơn 14 ngày, cửa sổ chỉ NỚI RA ⇒ thêm ứng viên cạnh tranh ⇒ chốt CHẶT HƠN, không
    # bao giờ lỏng hơn. Vừa không rot, vừa không phải nới lỏng.
    win = max(14, int((_time.time() - int(days_ago)) // 86400) + 1) if days_ago else 0
    rc1c, out1c = _run(m, [q], ["--days", str(win)])
    check(f"regression(e2e, git log THẬT, --days {win} = max(mặc-định-14, tuổi+1); '{age}'): "
          "commit SỬA THẬT "
          "d51c735e ĐƯỢC IN RA (không bị hoà điểm + cap cắt mất)",
          "d51c735e" in out1c and rc1c == 0, out1c.strip()[:600] or "(rỗng)")

    # 3b) FIXTURE (thay ca meta cũ dựa trên git log THẬT): hai repo giả, message THẬT của
    #     d51c735e (fix code, repo WorkingClaude) và 85b744a1 (ghi chú rỗng, repo mike). Chạy ở
    #     --days MẶC ĐỊNH nên chốt này KHÔNG rot khi commit thật già đi — arch-review 2026-09-29
    #     required_change #2 đòi chốt mạnh ở cửa sổ mặc định, còn nới lỏng sang --days 3650 cho
    #     vừa hành vi thì ngược quy trình. Thứ tự REPOS đặt repo "mike" TRƯỚC, đúng cái làm bản
    #     v2 chọn nhầm sang commit ghi chú.
    fixture_cases(m)

    # 4b) TỰ LOẠI TRỪ: commit sửa chính công cụ này không được tự nhận là resolver của các
    #     câu hỏi mà message của nó lấy làm ví dụ (a9c4a421 — đã xảy ra thật).
    shas = [c[0] for c in m._commits(ROOT, 3650)]
    check("self-exclusion: commit chạm question_commit_hint.py bị loại khỏi nguồn quét",
          not any(x.startswith("a9c4a421") for x in shas), str(shas[:5]))

    # 5b) META-QUESTION: câu hỏi escalation của retro nói về một PATTERN lặp lại, không về một
    #     bug ⇒ không commit nào "đã xử lý nó". Đo thật 2026-09-30: cả 2 gợi ý live đều thuộc lớp
    #     này và cả 2 đều SAI (topic có sẵn 6+ token dài generic: pattern/recurring/question/
    #     closure/answer/event ⇒ mọi commit nói về bus đủ điểm).
    q5 = {"agent": "Mike", "topic": "retro-pattern-recurring-bus-question-closure-gap-real-fix-"
          "no-answer-event", "ts": "x", "age_days": 0}
    rc5, out5 = _run(m, [q5], ["--days", "30"])
    check("meta-question: topic retro-pattern-recurring-* KHÔNG bao giờ được gợi ý commit",
          out5.strip() == "" and rc5 == 0, out5.strip()[:300])

    # 5d) _is_code — .json là CONFIG HÀNH VI của fleet (trading_rules/plan/jobs), KHÔNG phải tài
    #     liệu (arch-review vòng 2: coi nó là docs thì commit sửa config-only bị hạ hạng xuống
    #     sau commit ghi chú). Tài liệu = đuôi văn bản HOẶC nằm trong thư mục tài liệu.
    check("_is_code: trading_rules.json là CODE/CONFIG, không phải docs",
          m._is_code("trading_rules.json") is True)
    check("_is_code: kb/x.json vẫn là docs (thư mục tài liệu)", m._is_code("kb/x.json") is False)
    check("_is_code: .md/.proposed/reports/ là docs",
          m._is_code("kb/a.md\nbin/b.md.proposed\nreports/c.csv") is False,
          "reports/*.csv cũng là sản phẩm tài liệu")
    check("_is_code: .sh/.py/.sql là code",
          m._is_code("bin/x.sh") and m._is_code("a.py") and m._is_code("q.sql"))
    check("_is_code: commit rỗng (không file) ⇒ docs", m._is_code("") is False)

    # 5c) GHIM _META_Q_PREFIX vào NGUỒN SINH slug. retro_escalate.py là chỗ duy nhất tạo lớp
    #     topic đó; đổi tiền tố bên đó mà đây không đổi thì luật lọc chết ÂM THẦM và 2/2 báo
    #     động giả quay lại (arch-reviewer đã tái lập bằng mutation). Assertion thay vì import:
    #     giữ fail-open, không để một lỗi import bên kia làm câm cái nhắc này.
    esc = os.path.join(ROOT, "bin", "retro_escalate.py")
    src = open(esc, encoding="utf-8").read() if os.path.exists(esc) else ""
    check("_META_Q_PREFIX khớp TOPIC_PREFIX của bin/retro_escalate.py (nguồn sinh slug)",
          ('TOPIC_PREFIX = "%s"' % m._META_Q_PREFIX) in src, m._META_Q_PREFIX)

    # 5) FAIL-OPEN: repo không tồn tại ⇒ _commits im lặng trả rỗng, không ném.
    check("_commits: repo rác ⇒ [] chứ không ném", m._commits("/nonexistent-repo-xyz", 7) == [])

    # 6) RÀNG BUỘC TÍCH HỢP — không có cái này thì hint chết âm thầm.
    wired_into_wags_autofix()

    print(("FAIL: %d" % len(FAILS)) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
