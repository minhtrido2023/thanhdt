#!/usr/bin/env python3
"""Selfcheck cho bin/question_commit_hint.py — chạy trên GIT LOG THẬT của 2 repo.

Ca hồi quy #1 là chính sự cố sinh ra công cụ: câu hỏi
`Winston/sell-loanpackage-deal-not-found-zalopay-20260929` (29/09) được sửa bằng commit
d51c735e trên WorkingClaude/main mà không ai ghi event `answer` (Pattern B lần 3). Công cụ
PHẢI chỉ ra được commit đó. Ca #2 chốt chiều ngược lại — báo động giả đã đo thật.

⚠️ Ca e2e 1c dùng cửa sổ `--days max(14, tuổi(d51c735e)+1)`: nó được THIẾT KẾ để SIẾT DẦN —
cửa sổ chỉ nới ra theo thời gian nên số ứng viên cạnh tranh chỉ TĂNG. Khi nó đỏ, phân biệt
trước: (a) HỒI QUY thật trong logic xếp hạng, hay (b) ROT do repo tích tụ commit khớp từ khoá
mới. Đừng nới ngưỡng/`--max` để làm nó xanh lại trước khi loại trừ (a).
"""
import importlib.util
import io
import os
import re
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


def check_or_skip(name, cond, detail="", available=True):
    """arch-review 2026-09-30: ca hồi quy neo vào sha THẬT (d51c735e) phải SKIP CÓ THÔNG BÁO khi
    sha không còn (clone shallow / history rewrite) — assert cứng sẽ đỏ vì ROT, không vì hồi quy,
    và selfcheck đỏ vì lý do sai thì lần sau không ai đọc nữa."""
    if not available:
        print("  SKIP " + name + "  — sha neo không còn trong repo (clone shallow/history "
              "rewrite): KHÔNG phải hồi quy")
        return
    check(name, cond, detail)


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

        # ── arch-review 2026-09-30 (vòng 2 của nhánh ranking) ────────────────────────────
        # (A) CAP TẦNG CÂU HỎI: trước đây rows[:limit] cắt IM LẶNG *và* sort theo tuổi GIẢM
        #     dần ⇒ câu hỏi TRẺ NHẤT bị cắt trước — đúng lớp ca Pattern B (câu 0-1 ngày).
        #     Hai chốt: (1) phải NÓI RA còn N câu hỏi; (2) câu TRẺ phải SỐNG qua cap.
        q_old = {"agent": "Wags", "topic": "brokers-resolve-sell-loan-package-sellable",
                 "ts": "x", "age_days": 9}
        q_young = dict(q)             # age_days = 0, cùng điểm hạng
        _rc, outq = _run(m, [q_young, q_old], ["--max", "1"])
        check("cap câu hỏi: in 1 và NÓI RA còn 1 câu hỏi treo khác",
              "còn 1 câu hỏi treo khác" in outq, outq.strip()[:400])
        # "Bị cắt" = không còn MỤC riêng (dòng `  · agent/topic (Nd treo) ←`); TÊN vẫn phải
        # xuất hiện trong dòng nói-ra-phần-cắt (nit arch-review vòng 3: nói SỐ mà không nói TÊN
        # thì phần bị cắt vẫn vô hình).
        _entry = lambda q: "· %s/%s (" % (q.get("agent"), q["topic"])
        check("cap câu hỏi: câu TRẺ (0d, ca Pattern B) SỐNG, câu GIÀ (9d) mất MỤC riêng",
              _entry(q_young) in outq and _entry(q_old) not in outq, outq.strip()[:400])
        check("cap câu hỏi: dòng nói-ra NÊU TÊN câu bị cắt, không chỉ đếm số",
              q_old["topic"] in outq.split("còn 1 câu hỏi treo khác")[-1], outq.strip()[:400])
        check("dòng nói-ra-phần-cắt chỉ đúng flag THẬT (--max), không chỉ sai đường",
              "--max 2" in outq, outq.strip()[:400])

        # (C) HIỆU ỨNG XẾP HẠNG của is_code — không chỉ phân lớp _is_code (arch-review
        #     2026-09-30: fixture cũ đậu vì commit code thắng bằng ĐIỂM 6-5, nên khoá
        #     -int(is_code) trong cands.sort chưa bao giờ bị thử; mutant bỏ nó vẫn SỐNG).
        #     Ca này dựng NGƯỢC: commit DOCS điểm CAO HƠN commit CODE, code vẫn phải đứng trước.
        tmp2 = tempfile.mkdtemp(prefix="qch_rank_")
        try:
            d2, c2 = os.path.join(tmp2, "mike"), os.path.join(tmp2, "WorkingClaude")
            topic_r = "sell-loanpackage-deal-not-found-zalopay-20260929"
            # docs: nhồi token vào CẢ subject lẫn body ⇒ điểm cao nhất có thể.
            _git_repo(d2, [("docs(retro): sell loanpackage deal not found zalopay ghi chú",
                            "sell loanpackage deal not found zalopay loanpackage deal", [])])
            # code: chỉ khớp ở body, subject không có token ⇒ điểm THẤP hơn hẳn.
            _git_repo(c2, [("fix(brokers): resolve package của deal thật",
                            "sell loanpackage deal not found zalopay", ["trading_bot/x.py"])])
            m.REPOS = [d2, c2]
            _rc, outr = _run(m, [{"agent": "Winston", "topic": topic_r, "ts": "x",
                                  "age_days": 0}])
            sha_d = subprocess.run(["git", "-C", d2, "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()
            sha_c = subprocess.run(["git", "-C", c2, "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()
            pts = dict((ln.split("@")[1].split(":")[0].strip(),
                        int(ln.split("đ]")[0].rsplit("/", 1)[1]))
                       for ln in outr.splitlines() if "đ] " in ln)
            check("rank fixture dựng ĐÚNG chiều: commit docs ĐIỂM CAO HƠN commit code",
                  pts.get(sha_d, 0) > pts.get(sha_c, 0), "%s / %s" % (pts, outr[:300]))
            check("xếp hạng: commit CODE vẫn đứng TRƯỚC docs dù ĐIỂM THẤP HƠN",
                  sha_c in outr and sha_d in outr and outr.index(sha_c) < outr.index(sha_d),
                  outr.strip()[:400])
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)
            m.REPOS = [mike, wc]

        # (B) --per-question là flag THẬT: dòng gợi ý ở tầng commit trỏ vào nó.
        m.REPOS = [mike, wc, os.path.join(tmp, "third")]
        _rc, outp = _run(m, [q], ["--per-question", "3"])
        check("--per-question 3: in cả 3 ứng viên, không còn dòng cắt",
              outp.count("đ] ") == 3 and "ứng viên khác" not in outp, outp.strip()[:400])
        _rc, outp1 = _run(m, [q], ["--per-question", "1"])
        check("--per-question 1: cắt còn 1 và trỏ vào --per-question 3",
              outp1.count("đ] ") == 1 and "--per-question 3" in outp1, outp1.strip()[:400])
        m.REPOS = [mike, wc]
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
    check("lời gọi có timeout (thống nhất với dispatch_question_hint.py, foreground trước setsid)",
          all("timeout " in c for c in calls), str(calls))
    check("hint THẬT SỰ đi vào prompt dispatch (${COMMIT_HINT:+...})",
          "${COMMIT_HINT:+" in src, "không thấy trong wags_autofix.sh")


def wired_into_dispatch_completion():
    """User mandate 2026-09-30 (option B + hướng bổ sung): việc GỌI hint phải BẮT BUỘC ở đường
    HOÀN TẤT của MỌI job ĐI QUA dispatch.sh, không chỉ khi wags_autofix chạy vòng coord (ngoại
    lệ có chủ đích: bin/verify_finding.sh tự dựng job record riêng — job verify không sinh commit
    fix nên không có gì để gợi ý). dispatch.sh có HAI đường
    hoàn tất (--bg trong _bg_wrapper, và foreground) — vá một đường là bỏ lọt nửa còn lại
    (đúng tiền lệ dispatch_question_hint.py). Fail-open + im lặng ⇒ cơ chế chết âm thầm nếu
    call site bị xoá, nên ghim lại bằng test."""
    src = open(os.path.join(ROOT, "bin", "dispatch.sh"), encoding="utf-8").read()
    calls = [ln for ln in src.splitlines()
             if "bin/question_commit_hint.py" in ln and not ln.strip().startswith("#")]
    check("dispatch.sh gọi question_commit_hint.py ở CẢ 2 đường hoàn tất (--bg + foreground)",
          len(calls) == 2, str(calls))
    check("2 lời gọi dispatch.sh đều fail-open (|| true)",
          all("|| true" in c for c in calls), str(calls))
    check("2 lời gọi dispatch.sh đều có timeout",
          all("timeout " in c for c in calls), str(calls))
    # Nhánh --bg là headless: stderr không ai đọc ⇒ hint phải đi vào log job VÀ vào prompt
    # AUTO-CALLBACK gửi ngược cho agent đã giao việc, nếu không thì vô hình.
    check("nhánh --bg đưa hint vào prompt AUTO-CALLBACK (${_commit_hint:+...})",
          "${_commit_hint:+" in src, "không thấy trong dispatch.sh")
    cb = [ln for ln in src.splitlines() if "AUTO-CALLBACK job=" in ln]
    check("dòng AUTO-CALLBACK có tham chiếu _commit_hint",
          any("_commit_hint" in c for c in cb), str(cb))
    check("hint trong AUTO-CALLBACK có nhãn THÔNG TIN NỀN (không bị hiểu là việc được giao)",
          "[THÔNG TIN NỀN" in src, "không thấy nhãn")
    # Nhánh --bg headless: 2>/dev/null nuốt traceback/timeout ⇒ cơ chế "không thể quên" chết
    # lặng, chính là Pattern B ở tầng cơ chế (arch-review 2026-09-30, fail_silent).
    bg = [c for c in calls if "_commit_hint=" in c]
    # Khẳng định MẠNH (arch-review vòng 2): "không có 2>/dev/null" vẫn đậu với `2>> /dev/null`
    # hay bất kỳ file rác nào. Phải đi TỚI $logfile — file duy nhất được surface theo job qua
    # jobs.sh status / trace.sh. logs/consolidator.log KHÔNG tính: consolidate.sh:35-36 tự ghi
    # nó là "nobody reads: the 2026-07-28 loss ran 9h unnoticed".
    check("nhánh --bg đưa stderr của hint TỚI $logfile (không /dev/null, không consolidator.log)",
          bg and all(re.search(r'2>>?\s*"\$logfile"', c) for c in bg), str(bg))
    # Đường hoàn tất THỨ BA trong dispatch.sh sẽ làm mandate "mọi job" sai mà không ai biết.
    dones = [ln for ln in src.splitlines()
             if "JSET status=done" in ln and not ln.strip().startswith("#")]
    check("dispatch.sh vẫn chỉ có ĐÚNG 2 điểm ghi status=done (thêm đường thứ 3 ⇒ phải wire hint)",
          len(dones) == 2, str(dones))
    _preview_window_untainted(src)


def _bg_region(lines):
    """Chỉ xét thân _bg_wrapper() — writer $logfile ngoài đó (vd $logfile.workerpid trong
    _hb_aware_timeout) không liên quan tới thứ tự chụp/ghi ở đường hoàn tất."""
    i = next(i for i, ln in enumerate(lines) if re.match(r"\s*_bg_wrapper\(\)\s*\{", ln))
    j = next(j for j in range(i + 1, len(lines)) if lines[j].rstrip() == "  }")
    return i, j


_WRITE = re.compile(r'(>>?\s*"?\$logfile"?(\s|$)|tee\s+(-a\s+)?"?\$logfile"?)')


def _preview_window_untainted(src):
    """KILLER OBJECTION arch-review 2026-09-30: hint append vào $logfile (~812B) trong khi
    `tail -c 500 $logfile` là preview Discord USER-FACING và `head -c 400` là cb_summary ⇒ chụp
    SAU khi append thì kết luận agent bị xoá sạch khỏi thông báo cho user. Test này trích dòng
    THẬT từ dispatch.sh theo ĐÚNG thứ tự xuất hiện rồi chạy chúng — đảo thứ tự là chết.

    ⚠️ GIỚI HẠN đã biết (arch-review vòng 3, mutant M-N): đây là phân tích TĨNH theo thứ tự
    DÒNG, nên bảo đảm là "không có write TRỰC TIẾP vào $logfile trước 2 cửa sổ chụp", KHÔNG
    phải "không có write nào". Một helper định nghĩa NGOÀI vùng _bg_wrapper rồi gọi trước
    capture sẽ thoát cả chốt tĩnh lẫn e2e. Chi phí trace runtime vượt giá trị ⇒ chấp nhận,
    ghi ra đây để người sau không tưởng chốt này mạnh hơn thực tế."""
    lines = src.splitlines()
    lo, hi = _bg_region(lines)
    reg = range(lo, hi)
    idx_read = [i for i in reg
                if 'tail -c 500 "$logfile"' in lines[i] or 'head -c 400 "$logfile"' in lines[i]]
    # Loại theo INDEX (i not in idx_read), KHÔNG theo substring "tail -c"/"head -c"
    # (arch-review vòng 3, mutant M-O): 2 clause substring đó không bảo vệ gì — dòng capture
    # không khớp _WRITE vì không có `>` trước "$logfile" — mà mở cửa cho mọi write ẩn trong
    # một dòng tình cờ có chứa "tail -c".
    idx_write = [i for i in reg
                 if _WRITE.search(lines[i]) and not lines[i].strip().startswith("#")
                 and i not in idx_read
                 and ".workerpid" not in lines[i] and "CLI_ARGV" not in lines[i]]
    check("có đủ 2 cửa sổ chụp log (_preview tail -c 500 + _cb_summary head -c 400)",
          len(idx_read) == 2, str(idx_read))
    check("MỌI lệnh ghi thêm vào $logfile nằm SAU khi đã chụp preview/cb_summary",
          bool(idx_read) and bool(idx_write) and min(idx_write) > max(idx_read),
          "reads=%s writes=%s" % (idx_read, idx_write))
    # nit arch-review vòng 2: không có chốt nào buộc CONSUMER dùng biến đã chụp ⇒ mutant đọc
    # lại `$(cat "$logfile")` ngay tại chỗ gửi Discord vẫn thoát.
    nt = [lines[i] for i in reg if "notify_thread.sh" in lines[i] and "xong (job" in lines[i]]
    check("ping Discord dùng BIẾN đã chụp ($_preview), không đọc lại $logfile tại chỗ",
          nt and any("$_preview" in ln for ln in nt)
          and all("$logfile" not in ln for ln in nt), str(nt))
    cbl = [lines[i] for i in reg if "AUTO-CALLBACK job=" in lines[i]]
    check("prompt AUTO-CALLBACK dùng BIẾN đã chụp ($_cb_summary), không đọc lại $logfile",
          cbl and all("$_cb_summary" in ln and "$logfile" not in ln for ln in cbl), str(cbl))

    # Chạy thật các dòng đã trích, thứ tự nguyên bản trong file. Dòng ghi lấy đúng lệnh append
    # TEXT hint (không lấy dòng redirect stderr của lời gọi python — nó cần $ROOT thật).
    idx_sim = [i for i in idx_write if "printf" in lines[i]]
    picked = sorted(idx_read + idx_sim)
    body = "\n".join(lines[i].strip() for i in picked)
    tmp = tempfile.mkdtemp(prefix="wags_preview_")
    try:
        log = os.path.join(tmp, "job.log")
        with open(log, "w", encoding="utf-8") as f:
            f.write("nap context...\n" * 3 + "KET_LUAN_AGENT: CAGR 23,37%-25,71%, KHONG GO-LIVE.\n")
        script = os.path.join(tmp, "sim.sh")
        with open(script, "w", encoding="utf-8") as f:
            f.write("set -u\nlogfile=%s\n" % log)
            f.write("_commit_hint=\"$(head -c 900 /dev/zero | tr '\\0' 'x' | sed 's/^/HINT_NAG_X/')\"\n")
            f.write("local() { :; }\n")   # 'local' ngoài hàm ⇒ vô hại hoá
            f.write(body + "\n")
            f.write('printf "PREVIEW=%s\\nCB=%s\\n" "$_preview" "$_cb_summary"\n')
        r = subprocess.run(["bash", script], capture_output=True, text=True, timeout=30)
        out = r.stdout
        prev = [l for l in out.splitlines() if l.startswith("PREVIEW=")]
        cbv = [l for l in out.splitlines() if l.startswith("CB=")]
        detail = (out + r.stderr)[:400]
        check("e2e (hint NON-EMPTY): trích được cả 2 cửa sổ + lệnh append, script chạy được",
              bool(prev) and bool(cbv) and len(picked) >= 3, "picked=%s %s" % (picked, detail))
        check("e2e (hint NON-EMPTY): preview Discord còn kết luận agent",
              prev and "KET_LUAN_AGENT" in prev[0], detail)
        check("e2e (hint NON-EMPTY): preview Discord KHÔNG chứa text hint",
              prev and "HINT_NAG" not in prev[0], detail)
        check("e2e (hint NON-EMPTY): cb_summary AUTO-CALLBACK KHÔNG chứa text hint",
              cbv and "HINT_NAG" not in cbv[0], detail)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    m = _mod()
    print("question_commit_hint_selfcheck")

    # 1) HỒI QUY — ca thật 2026-09-29. Chỉ có nghĩa khi commit d51c735e còn trong cửa sổ --days.
    have = subprocess.run(["git", "-C", os.path.dirname(ROOT), "cat-file", "-e", "d51c735e^{commit}"],
                          capture_output=True).returncode == 0
    q = {"agent": "Winston", "topic": "sell-loanpackage-deal-not-found-zalopay-20260929",
         "ts": "2026-09-29T06:35:29Z", "age_days": 0}
    rc, out = _run(m, [q], ["--days", "3650"])
    if not have:
        print("  NOTE: commit neo d51c735e không còn trong repo — các ca hồi quy neo vào nó sẽ "
              "SKIP (không phải hồi quy). Ca fixture + unit vẫn chạy đủ.")
    # Cố ý KHÔNG chốt cứng ĐÚNG sha nào được in: cùng sự cố có cả một CHÙM commit hợp lệ (fix
    # trên WorkingClaude + ghi chú vận hành trên mike). Yêu cầu THẬT là câu hỏi phải được NÊU
    # TÊN kèm một commit của chùm đó — chốt cứng 1 sha là chốt vào thứ tự duyệt repo.
    check_or_skip("regression: câu hỏi sell-loanpackage được nêu tên trong gợi ý",
                  "sell-loanpackage-deal-not-found-zalopay-20260929" in out,
                  out.strip()[:200] or "(rỗng)", have)
    check_or_skip("regression: rc=0", rc == 0, "", have)

    # 1b) Mức FUNCTION — chính commit sửa d51c735e phải đạt điểm khớp, độc lập với thứ tự duyệt.
    hint = m._load_hint_module()
    tok = hint._tokens(q["topic"])
    hit = [c[0] for c in m._commits(os.path.dirname(ROOT), 3650)
           if c[0].startswith("d51c735e") and m._score(tok, c[2], c[3]) >= m._MIN_SCORE]
    check_or_skip("regression(function): d51c735e đạt ngưỡng khớp trên repo WorkingClaude",
                  bool(hit), "", have)

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
    # ĐỘ LỚN thưởng subject phải là ĐÚNG +1/token (arch-review 2026-09-30: mutant nhân đôi
    # thưởng vẫn SỐNG với bộ chốt cũ vì chúng chỉ kiểm "commit có subject khớp xếp trước").
    _tok4 = {"loanpackage": 1, "dealnotfound": 1, "zalopay": 1, "sellable": 1}
    _body = "loanpackage dealnotfound zalopay sellable"
    _base = m._score(_tok4, _body, _body.replace(" ", ""), "")
    check("_score: 4 token khớp body, subject rỗng ⇒ đúng 4 điểm (không thưởng)", _base == 4,
          str(_base))
    _s2 = m._score(_tok4, _body, _body.replace(" ", ""), "fix: loanpackage dealnotfound")
    check("_score: thưởng subject ĐÚNG +1/token (2 token ở subject ⇒ 6đ, không phải 8)",
          _s2 == 6, str(_s2))
    _s4 = m._score(_tok4, _body, _body.replace(" ", ""), _body)
    check("_score: cả 4 token ở subject ⇒ đúng 8đ (trần thưởng = số token khớp)", _s4 == 8,
          str(_s4))

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
    check_or_skip(f"regression(e2e, git log THẬT, --days {win} = max(mặc-định-14, tuổi+1); "
                  f"'{age}'): commit SỬA THẬT d51c735e ĐƯỢC IN RA (không bị hoà điểm + cap cắt)",
                  "d51c735e" in out1c and rc1c == 0, out1c.strip()[:600] or "(rỗng)", have)

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
    wired_into_dispatch_completion()

    print(("FAIL: %d" % len(FAILS)) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
