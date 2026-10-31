"""report_v2.vocab — MỘT nguồn cho từ cấm, dùng chung bởi narrative.py (chặn sớm, rc=2) và
artifact_lint.py (chặn ở cổng gửi). Trước 31/10 r3 hai bên giữ hai danh sách riêng và đã trôi
(narrative thiếu dnse_raw/Traceback, lint thiếu BAL/SIGNAL_V) — arch-review N2.

  • INTERNAL_RE — tên nội bộ cấm trong báo cáo nhà đầu tư. Tên riêng (người/agent/tài khoản)
    không phân biệt hoa/thường ("livermore", "zalopay"); viết tắt chiến lược (LAG/BAL/PARK…)
    phân biệt hoa/thường để không bắt nhầm chữ thường.
  • RAW_MD — markdown thô / giá trị rỗng. `nan`/`NaN`/`None`/`NaT` chỉ bị chặn khi đứng như
    TOKEN DỮ LIỆU (cuối ô/dòng, trước `%`, trước đơn vị) — không chặn "nan giải".
"""
import re

_NAMES = (r"Livermore|Taylor|Bobby|Winston|Wendy|Spyros|Mafee|DollarBill|Mike|ZaloPay|liên tài khoản|"
          r"BigQuery|Traceback")
_CODES = (r"0001743768|LAG|PARK|DT5G|DT4|PEAD|BAL|CAPIT|custom30V?|tav2_\w+|universe_pit|SIGNAL_V\d+|"
          r"dnse_raw\w*|nav_history\w*|[\w-]+\.(?:jsonl|csv|py|pkl)")
INTERNAL_RE = re.compile(rf"\b(?:(?i:{_NAMES})|{_CODES})\b")

# token dữ liệu rỗng: KHÔNG chặn khi theo sau là một từ chữ thường (ngoại trừ đơn vị số liệu).
_UNIT = r"(?:VND|đ|tr|điểm|lần|phiên|mã|trang)\b"
DATA_NULL = rf"(?<![\w.])(?:nan|NaN|None|NaT)\b(?!\s+(?!{_UNIT})[^\W\d_])"
RAW_MD = [r"\['\|", r"\*\*", r"^\s*\|[-:| ]+\|\s*$", r"^#{1,4} ", r"\\n\|", r"!\[", DATA_NULL]
