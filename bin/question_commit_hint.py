#!/usr/bin/env python3
"""question_commit_hint.py — câu hỏi bus còn treo này có commit nào TRÔNG NHƯ đã sửa nó chưa?

VẤN ĐỀ (Pattern B, lần thứ 3 trong 7 tuần: TV1-ceiling 08-13, closerepair-fix-approval 09-29,
sell-loanpackage-deal-not-found 09-29). Quyết định/khắc phục đi qua kênh HÀNH ĐỘNG — user duyệt
trên Discord, agent sửa code, COMMIT — nhưng không ai ghi event `answer`. Checker §5 chỉ đọc bus
nên câu hỏi vẫn "treo", wags_autofix bị đánh thức, một job trọn vẹn bị đốt chỉ để đọc lại git log
và kết luận "đã sửa từ lâu rồi".

`dispatch_question_hint.py` đã bịt nhánh DISPATCH (quyết định nằm trong prompt). Nhánh COMMIT
chưa có gì — đây là nó. Cùng một matcher, khác nguồn văn bản.

PHẠM VI (cố ý hẹp, giống hệt dispatch_question_hint):
  · Đây là NHẮC, KHÔNG tự động đóng. Đóng theo suy đoán văn bản = đóng oan escalation tiền thật.
  · Token phân biệt của topic lấy thẳng từ dispatch_question_hint._tokens (nguồn CHÍNH THỐNG,
    port của check #5) — không viết bản sao thứ 5. NGƯỠNG thì CHẶT HƠN bản dispatch, xem _score:
    một prompt dispatch nói về đúng việc đang giao nên 2 điểm là đủ; git log 14 ngày là hàng trăm
    commit không liên quan nên cùng ngưỡng đó cho ra toàn báo động giả (đo thật: 5/5 gợi ý đầu
    tiên đều sai). Nhắc bị phớt lờ tệ hơn không có nhắc.
  · Nguồn "câu hỏi nào còn treo" = bin/bus_question_audit.py --json, cũng qua module đó.

FAIL-OPEN TUYỆT ĐỐI: mọi lỗi ⇒ im lặng, exit 0. Không được làm hỏng vòng wags_autofix.

  question_commit_hint.py [--days N] [--max N]
"""
import importlib.util
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Hai repo song song: mike (fleet code) và WorkingClaude (trading code — cha của mike).
REPOS = [ROOT, os.path.dirname(ROOT)]
_DEFAULT_DAYS = 14
_DEFAULT_MAX = 5


def _load_hint_module():
    path = os.path.join(ROOT, "bin", "dispatch_question_hint.py")
    spec = importlib.util.spec_from_file_location("dispatch_question_hint", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _commits(repo, days):
    """[(sha, subject, text_để_match)] — QUÉT CẢ BODY, không chỉ subject: bằng chứng mạnh nhất
    (đường dẫn file incident, tên biến, slug câu hỏi) hầu như luôn nằm trong body, còn subject
    thì viết bằng tiếng Việt tự nhiên và gần như không bao giờ chứa slug topic."""
    r = subprocess.run(
        ["git", "-C", repo, "log", f"--since={days}.days", "--no-merges",
         "--format=%h%x1f%s%x1f%B%x1e"],
        capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return []
    out = []
    for rec in r.stdout.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split("\x1f")
        if len(parts) < 3:
            continue
        sha, subj, body = parts[0], parts[1], parts[2]
        # Bản DẸT (bỏ mọi ký tự không chữ-số) để token "closerepair" của topic khớp được
        # "close_repair"/"close-repair" trong commit. Giữ CẢ bản gốc để phép so nguyên-topic
        # (mức "CHẮC" của _matches, có dấu gạch) vẫn còn cửa khớp.
        low = body.lower()
        flat = "".join(c for c in low if c.isalnum())
        out.append((sha, subj, low, flat))
    return out


_MIN_SCORE = 4          # tổng điểm token khớp
_MIN_SPECIFIC = 2       # số token ĐẶC THÙ (đủ dài) phải khớp
_SPECIFIC_LEN = 7
_FLAT_LEN = 7           # chỉ token đủ dài mới được khớp trên bản DẸT


_DATE_RE = re.compile(r"^\d{2,4}-\d{2}(-\d{2})?$")


def _score(tokens, low, flat):
    """Điểm khớp của 1 topic với 1 commit. Token NGÀY bị LOẠI hẳn ở nguồn commit (khác bản
    dispatch, nơi ngày là token đặc thù nhất): mọi commit đều nhắc ngày của chính nó, nên
    "2026-09-28" + một từ tầm thường là đủ 4 điểm — đo thật, đó đúng là báo động giả duy nhất
    còn lại (84b7dbd3 "quant-skeptic CONFIRMED 2026-09-28" khớp câu hỏi
    wags-fix-not-confirmed: coord-2026-09-28). Hệ quả CHẤP NHẬN: lớp câu hỏi mà ngày là token
    phân biệt DUY NHẤT sẽ không bao giờ khớp từ nguồn commit — đúng, vì với nguồn này nó không
    mang thông tin. Token NGẮN phải khớp theo RANH GIỚI TỪ trên văn bản
    gốc — cho nó khớp chuỗi con trên bản dẹt thì "deal" trúng "dealer", "idealized", và mọi
    commit tiếng Việt viết liền đều thành ứng viên."""
    hits = {}
    for t, pt in tokens.items():
        if _DATE_RE.match(t):
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", low):
            hits[t] = pt
        elif len(t) >= _FLAT_LEN and t in flat:
            hits[t] = pt
    if sum(hits.values()) < _MIN_SCORE:
        return 0
    if sum(1 for t in hits if len(t) >= _SPECIFIC_LEN) < _MIN_SPECIFIC:
        return 0
    return sum(hits.values())


def main():
    argv = sys.argv[1:]
    days, limit = _DEFAULT_DAYS, _DEFAULT_MAX
    for i, a in enumerate(argv):
        if a == "--days" and i + 1 < len(argv):
            days = int(argv[i + 1])
        elif a == "--max" and i + 1 < len(argv):
            limit = int(argv[i + 1])

    hint = _load_hint_module()
    pending = hint._pending()
    if not pending:
        return 0

    # topic -> (mức, sha, subject, repo). Giữ commit MỚI NHẤT khớp mạnh nhất cho mỗi câu hỏi.
    best = {}
    for repo in REPOS:
        name = os.path.basename(repo)
        for sha, subj, low, flat in _commits(repo, days):
            for q in pending:
                topic = str(q.get("topic") or "")
                if not topic:
                    continue
                lvl = 2 if topic.lower() in low else 0
                if not lvl:
                    lvl = 1 if _score(hint._tokens(topic), low, flat) else 0
                if not lvl:
                    continue
                key = (q.get("agent", "?"), topic)
                if key not in best or lvl > best[key][0]:
                    best[key] = (lvl, sha, subj, name, q)
    if not best:
        return 0

    rows = sorted(best.values(), key=lambda x: (-x[0], -int(x[4].get("age_days") or 0)))[:limit]
    print("[Có commit TRÔNG NHƯ đã xử lý câu hỏi treo — CHỈ LÀ GỢI Ý theo từ khoá, phải tự đọc "
          "commit xem có đúng cùng việc không. Nếu ĐÚNG là đã xong mà chỉ thiếu event `answer` "
          "(Pattern B) thì đóng vòng bằng close_bus_question.py, đừng sửa lại lần nữa:]")
    for lvl, sha, subj, repo, q in rows:
        agent, topic, age = q.get("agent", "?"), q.get("topic", "?"), q.get("age_days", "?")
        mark = "CHẮC" if lvl == 2 else "có thể"
        print(f"  · [{mark}] {agent}/{topic} ({age}d treo) ← {repo}@{sha}: {subj}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Im lặng CÓ CHỦ ĐÍCH, giống dispatch_question_hint.py: đây là nhắc phụ trợ, không phải
        # đường escalation. Hỏng ⇒ hành vi như trước khi có nó.
        sys.exit(0)
