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


# `.json` KHÔNG nằm đây: trong fleet này .json là CONFIG HÀNH VI (trading_rules, plan, jobs) —
# coi nó là tài liệu thì commit sửa config-only bị hạ hạng xuống sau commit ghi chú
# (arch-review vòng 2, 2026-09-30). Tài liệu nhận ra bằng ĐUÔI văn bản hoặc THƯ MỤC tài liệu.
_DOC_EXT = (".md", ".txt", ".proposed")
_DOC_DIRS = ("/kb/", "/docs/", "/reports/")


def _is_code(files):
    """Commit có sửa file KHÔNG-phải-tài-liệu nào không? Commit docs-only (retro, ghi chú vận
    hành, runbook .proposed) hay ĐANG kể lại một sự cố hơn là sửa nó — nó vẫn đáng in ra, nhưng
    phải đứng SAU commit sửa thật. Đây là thuộc tính của CHÍNH commit, không phụ thuộc trạng thái
    bus (luật meta cũ `len(per_commit) != 1` thì có, và nó làm gợi ý duy nhất của ca 29/09 biến
    mất khi có thêm một câu hỏi họ hàng treo — arch-review 2026-09-29 NEEDS_CHANGES)."""
    for f in files.split("\n"):
        f = f.strip().lower()
        if not f or f.endswith(_DOC_EXT):
            continue
        if any(d in "/" + f for d in _DOC_DIRS):
            continue
        return True
    return False


def _commits(repo, days):
    """[(sha, subject, low, flat, is_code)] — QUÉT CẢ BODY, không chỉ subject: bằng chứng mạnh nhất
    (đường dẫn file incident, tên biến, slug câu hỏi) hầu như luôn nằm trong body, còn subject
    thì viết bằng tiếng Việt tự nhiên và gần như không bao giờ chứa slug topic."""
    r = subprocess.run(
        ["git", "-C", repo, "log", f"--since={days}.days", "--no-merges", "--name-only",
         "--format=%x1e%h%x1f%s%x1f%B%x1f"],
        capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return []
    out = []
    for rec in r.stdout.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split("\x1f")
        if len(parts) < 4:
            continue
        sha, subj, body, files = parts[0], parts[1], parts[2], parts[3]
        # TỰ LOẠI TRỪ: commit sửa chính công cụ này tất nhiên có message nói về những câu hỏi
        # nó lấy làm ví dụ ⇒ nó tự nhận là resolver của chính các câu hỏi đó (đã xảy ra ngay
        # với commit giới thiệu, a9c4a421).
        if os.path.basename(os.path.abspath(__file__)).split(".")[0] in files:
            continue
        # Bản DẸT (bỏ mọi ký tự không chữ-số) để token "closerepair" của topic khớp được
        # "close_repair"/"close-repair" trong commit. Giữ CẢ bản gốc để phép so nguyên-topic
        # (mức "CHẮC" của _matches, có dấu gạch) vẫn còn cửa khớp.
        low = body.lower()
        flat = "".join(c for c in low if c.isalnum())
        out.append((sha, subj, low, flat, _is_code(files)))
    return out


_MIN_SCORE = 4          # tổng điểm token khớp
_MIN_SPECIFIC = 2       # số token ĐẶC THÙ (đủ dài) phải khớp
_SPECIFIC_LEN = 7
_FLAT_LEN = 7           # chỉ token đủ dài mới được khớp trên bản DẸT
_META_MATCHES = 3       # khớp từ bấy nhiêu câu hỏi trở lên ⇒ commit META, bỏ
_MAX_PER_Q = 2          # in tối đa bấy nhiêu commit cho mỗi câu hỏi


_DATE_RE = re.compile(r"^\d{2,4}-\d{2}(-\d{2})?$")

# Câu hỏi escalation do retro_escalate.py sinh ra: nó nói về một PATTERN LẶP LẠI, không về một
# bug cụ thể ⇒ theo định nghĩa không có commit nào "đã xử lý xong" nó, chỉ user chốt A/B/C mới
# đóng được. Đo thật 2026-09-30: 2/2 gợi ý live đều thuộc lớp này và đều SAI — slug của chúng
# chứa sẵn 6+ token dài generic (pattern, recurring, question, closure, answer, event) nên mọi
# commit nói về bus đều dư điểm. Loại hẳn lớp này thay vì siết ngưỡng chung (siết chung sẽ giết
# luôn ca hồi quy thật d51c735e).
_META_Q_PREFIX = "retro-pattern-recurring-"


def _hit(t, low, flat):
    if re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", low):
        return True
    return len(t) >= _FLAT_LEN and t in flat


def _score(tokens, low, flat, subj=""):
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
        if _hit(t, low, flat):
            hits[t] = pt
    if sum(hits.values()) < _MIN_SCORE:
        return 0
    if sum(1 for t in hits if len(t) >= _SPECIFIC_LEN) < _MIN_SPECIFIC:
        return 0
    # THƯỞNG DÒNG SUBJECT. Ngưỡng ĐẬU/RỚT ở trên chỉ tính trên toàn văn (body) — không đổi.
    # Nhưng mọi token nặng đúng 1 điểm nên điểm BÃO HOÀ: đo thật 2026-09-30, cả 7 ứng viên của
    # câu hỏi sell-loanpackage đều đúng 5 điểm, và commit sửa thật d51c735e xếp 5/7 rồi bị cap
    # cắt (arch-review vòng 2). Body nhắc tới sự cố thì commit NÀO CŨNG nhắc (link incident,
    # "đi kèm ..."); còn SUBJECT thì chỉ commit nói về ĐÚNG việc đó mới chứa token của nó —
    # d51c735e có "deal" trong subject, e6fac527 ("fix(heartbeat): PLACE_FAIL_STOPPED ...")
    # không có token nào. Thưởng ở subject là tín hiệu phân biệt, không phải tie-break thứ tự.
    sflat = "".join(c for c in subj if c.isalnum())
    return sum(hits.values()) + sum(1 for t in hits if _hit(t, subj, sflat))


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

    # key câu hỏi -> [(lvl, sc, is_code, sha, subj, repo)] — CHÙM commit khớp, không chọn 1.
    # arch-review 2026-09-29: chọn 1 kéo theo bài toán tie-break, và với lớp ca Pattern B phổ
    # biến nhất (fix nằm ở WorkingClaude, ghi chú chatty hơn nằm ở mike) nó luôn chọn nhầm sang
    # commit ghi chú. In cả chùm thì người đọc thấy cả fix lẫn ghi chú, hết bài toán đó.
    matches = {}
    for repo in REPOS:
        name = os.path.basename(repo)
        for sha, subj, low, flat, is_code in _commits(repo, days):
            per_commit = []
            for q in pending:
                topic = str(q.get("topic") or "")
                if not topic or topic.lower().startswith(_META_Q_PREFIX):
                    continue
                sc = _score(hint._tokens(topic), low, flat, subj.lower())
                lvl = 2 if topic.lower() in low else (1 if sc else 0)
                if not lvl:
                    continue
                per_commit.append((lvl, sc, q))
            # Commit khớp TỪ 3 CÂU HỎI trở lên là commit META (retro liệt kê nhiều topic, tài
            # liệu tổng hợp) — bỏ cả cụm. Ngưỡng cũ là "khớp != 1 câu hỏi", quá chặt: một fix
            # thật rất hay khớp 2 câu hỏi họ hàng của cùng sự cố, và khi đó gợi ý ĐÚNG cũng bị
            # xoá theo (đo thật trên ca 29/09). Commit sửa chính công cụ này đã bị loại ở nguồn.
            if len(per_commit) >= _META_MATCHES:
                continue
            for lvl, sc, q in per_commit:
                key = (q.get("agent", "?"), str(q.get("topic") or ""))
                matches.setdefault(key, (q, []))[1].append((lvl, sc, is_code, sha, subj, name))
    if not matches:
        return 0

    rows = []
    for q, cands in matches.values():
        # git log trả mới-nhất-trước ⇒ sort ỔN ĐỊNH giữ commit mới nhất lên trên trong các ca hoà.
        cands.sort(key=lambda c: (-c[0], -int(c[2]), -c[1]))
        rows.append((cands[0][0], q, cands[:_MAX_PER_Q], len(cands) - _MAX_PER_Q))
    rows.sort(key=lambda x: (-x[0], -int(x[1].get("age_days") or 0)))
    rows = rows[:limit]

    print("[Có commit TRÔNG NHƯ đã xử lý câu hỏi treo — CHỈ LÀ GỢI Ý theo từ khoá, phải tự đọc "
          "commit xem có đúng cùng việc không. Nếu ĐÚNG là đã xong mà chỉ thiếu event `answer` "
          "(Pattern B) thì đóng vòng bằng close_bus_question.py, đừng sửa lại lần nữa:]")
    for _lvl, q, cands, extra in rows:
        agent, topic, age = q.get("agent", "?"), q.get("topic", "?"), q.get("age_days", "?")
        print(f"  · {agent}/{topic} ({age}d treo) ←")
        for lvl, sc, is_code, sha, subj, repo in cands:
            mark = "CHẮC" if lvl == 2 else "có thể"
            kind = "code" if is_code else "docs"
            print(f"      [{mark}/{kind}/{sc}đ] {repo}@{sha}: {subj}")
        if extra > 0:
            # NÓI RA phần bị cắt: cap 2 mà im lặng thì người đọc tưởng chỉ có 2 ứng viên, còn
            # commit đúng có thể nằm ở phần bị cắt (đúng ca d51c735e, arch-review vòng 2).
            print(f"      … còn {extra} ứng viên khác — xem đầy đủ: git log --grep / "
                  f"question_commit_hint.py --max 1 sau khi các câu hỏi khác được đóng")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Im lặng CÓ CHỦ ĐÍCH, giống dispatch_question_hint.py: đây là nhắc phụ trợ, không phải
        # đường escalation. Hỏng ⇒ hành vi như trước khi có nó.
        sys.exit(0)
