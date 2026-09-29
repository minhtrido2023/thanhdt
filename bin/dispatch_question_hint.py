#!/usr/bin/env python3
"""dispatch_question_hint.py — nhắc CƠ HỌC: dispatch này có đang xử lý một câu hỏi bus còn treo?

VẤN ĐỀ (root-cause-A, đã tái diễn ≥3 lần: coord-08-12 'lần thứ N', 3/6 câu hỏi cùng dạng).
Câu hỏi lên bus bằng event `question`. Nhưng người dùng quyết định qua DISCORD, Mike nghe rồi
DISPATCH thẳng cho agent thực thi — quyết định nằm trong prompt của dispatch, KHÔNG có event
`answer`/`decision` nào trên bus. Hệ quả: checker ops_health_check §5 vẫn thấy câu hỏi treo,
wags_autofix bị đánh thức, một job trọn vẹn bị đốt chỉ để kết luận "đã quyết rồi". Việc đóng
vòng đang phụ thuộc vào việc Mike NHỚ làm thủ công — không có cơ chế nào nhắc.

PHẠM VI (cố ý hẹp). Đây là NHẮC, không phải tự động đóng:
  · Tự động đóng theo suy đoán văn bản = đóng oan escalation tiền thật. Không làm.
  · Không đổi schema bus, không đổi thuật toán match của checker.
  · Nguồn "câu hỏi nào còn treo" DÙNG LẠI bin/bus_question_audit.py — matcher CHÍNH THỐNG
    (port đúng thuật toán check #5). Đây là bản sao thứ 4 nếu tự viết lại, nên không tự viết.

FAIL-OPEN TUYỆT ĐỐI: mọi lỗi ⇒ im lặng, exit 0. Dispatch KHÔNG BAO GIỜ được hỏng vì cái nhắc.

  echo "<prompt>" | dispatch_question_hint.py [--to <agent>] [--max N]
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Token quá phổ biến trong MỌI prompt điều phối ⇒ không mang thông tin phân biệt. Có tên các
# agent ở đây là CỐ Ý: prompt dispatch luôn nhắc tới agent nhận việc, để nó tính điểm thì mọi
# câu hỏi của agent đó đều khớp.
# CỐ Ý KHÔNG chặn các từ định-lớp như "confirmed"/"inconclusive"/"overdue": prompt nhắc đúng
# tên lớp câu hỏi là tín hiệu THẬT, chặn đi thì lớp wags-fix-not-confirmed không còn token nào.
_STOP = {
    "coord", "wags", "mike", "taylor", "winston", "spyros", "wendy", "mafee", "dollarbill",
    "question", "quyet", "user", "check", "checker", "selfcheck", "ops", "health", "bus",
    "event", "review", "pending", "agent", "dispatch",
    "job", "trong", "duoc", "khong", "phai", "cong", "tren", "dang", "cach", "viec", "nhung",
    "2026", "2025",
}
_MIN_TOKEN = 4
_MIN_SCORE = 2
_SPECIFIC_LEN = 6   # phải có ít nhất 1 token ĐỦ ĐẶC THÙ, xem _matches()


def _tokens(topic):
    """Token phân biệt của 1 topic → {token: điểm}.

    Ngày ĐẦY ĐỦ (2026-08-12) giữ nguyên khối và ăn 2 điểm: nó vừa là token đặc thù nhất, vừa
    là token DUY NHẤT của cả lớp `wags-fix-not-confirmed: coord-<ngày>` — tách thành 2026/08/12
    thì mất sạch (2026 là stopword, 08 và 12 dưới ngưỡng độ dài) và lớp tái diễn nhiều nhất
    lại thành lớp không bao giờ khớp được. Dạng VIẾT TẮT `MM-DD` (người hay gõ "coord-08-12")
    ăn 1 điểm: đủ để cộng với 1 token khác thành khớp, chưa đủ để tự nó khớp — "08-12" trần
    quá dễ trùng ngẫu nhiên."""
    scores = {}
    for d in re.findall(r"\d{4}-\d{2}-\d{2}", topic):
        scores[d] = 2
        scores.setdefault(d[5:], 1)          # "2026-08-12" → "08-12"
    rest = re.sub(r"\d{4}-\d{2}-\d{2}", " ", topic.lower())
    for w in re.split(r"[^a-z0-9]+", rest):
        if len(w) >= _MIN_TOKEN and w not in _STOP and not w.isdigit():
            scores.setdefault(w, 1)
    return scores


def _pending():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "bin", "bus_question_audit.py"),
                        "--json"], capture_output=True, text=True, timeout=20)
    return json.loads(r.stdout).get("pending", [])


def _matches(prompt, pending):
    """(mức, câu hỏi) cho các câu hỏi có vẻ liên quan. mức: 2=chắc (nguyên topic), 1=có thể."""
    low = prompt.lower()
    out = []
    for q in pending:
        topic = str(q.get("topic") or "")
        if not topic:
            continue
        if topic.lower() in low:
            out.append((2, q))
            continue
        hits = {t: p for t, p in _tokens(topic).items() if t.lower() in low}
        # Hai điều kiện ĐỘC LẬP, cố ý: đủ ĐIỂM (bao phủ) VÀ có ít nhất một token đủ ĐẶC THÙ.
        # Thiếu vế thứ hai thì 2 từ ngắn tầm thường ("plan"+"cash" — có mặt trong gần như mọi
        # prompt giao dịch của fleet) đủ khớp, và cái nhắc thành nhiễu nền. Nhắc bị phớt lờ
        # thì tệ hơn không có nhắc: nó tạo cảm giác đã có cơ chế trong khi không ai đọc.
        if (sum(hits.values()) >= _MIN_SCORE
                and any(len(t) >= _SPECIFIC_LEN for t in hits)):
            out.append((1, q))
    # Chắc trước, rồi CŨ trước — câu hỏi treo lâu là câu hỏi đang tốn job nhất.
    out.sort(key=lambda x: (-x[0], -int(x[1].get("age_days") or 0)))
    return out


def main():
    to_agent = ""
    limit = 3
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--to" and i + 1 < len(argv):
            to_agent = argv[i + 1]
        elif a == "--max" and i + 1 < len(argv):
            limit = int(argv[i + 1])
    prompt = sys.stdin.read()
    if not prompt.strip():
        return 0
    hits = _matches(prompt, _pending())
    if not hits:
        return 0
    shown, extra = hits[:limit], max(0, len(hits) - limit)
    print("  4) ⚠️ ĐÓNG VÒNG BUS — dispatch này chạm tới câu hỏi bus CÒN TREO. Nếu user đã "
          "quyết (kể cả khi họ chỉ nói qua Discord/chat, KHÔNG reply trên bus) thì báo miệng "
          "cho user KHÔNG đóng được câu hỏi: checker §5 chỉ đọc BUS. Post event đóng NGAY, "
          "đừng để lần sau một job wags_autofix bị đốt cho việc đã xong:")
    for lvl, q in shown:
        agent, topic, age = q.get("agent", "?"), q.get("topic", "?"), q.get("age_days", "?")
        mark = "CHẮC" if lvl == 2 else "có thể"
        print(f"       · [{mark}] {agent}/{topic} ({age}d treo)")
        print(f"         {ROOT}/bin/close_bus_question.py {json.dumps(agent + '/' + topic)} "
              "--resolution '<tóm tắt quyết định>' --evidence '<commit/file/log>' "
              "--decided-by-user")
    if extra:
        print(f"       · …và {extra} câu hỏi treo khác cũng khớp — "
              f"danh sách ĐẦY ĐỦ: {ROOT}/bin/bus_question_audit.py")
    print("       (Chỉ dùng `decided_by:user` khi user THẬT SỰ đã xác nhận — "
          "coding_guidelines §20. Tự quyết thì bỏ field đó, đừng khai khống.)")
    if to_agent:
        print(f"       (Không liên quan tới việc vừa giao {to_agent}? Bỏ qua dòng này — "
              "đây là nhắc theo từ khoá, không phải kết luận.)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Im lặng có CHỦ ĐÍCH và chỉ ở ĐÂY: đây là cái nhắc phụ trợ, không phải đường
        # escalation. Nó hỏng thì hành vi = như trước khi có nó. Đúng thứ NGƯỢC LẠI với
        # _post_q trong wags_autofix.sh (đường escalation duy nhất ⇒ phải kêu to).
        sys.exit(0)
