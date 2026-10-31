"""report_v2.narrative — nạp + KIỂM narrative.json (phần chữ duy nhất agent được viết).

Luật (REPORT_STYLE_V2 §2, §7, §8; user chốt 31/10):
  • headline ≤ 25 từ; mỗi mục ≤ 3 gạch, mỗi gạch ≤ 25 từ; outlook = bảng kịch bản ≤ 4 hàng.
  • KHÔNG tự viết số: mọi token số trong narrative phải có NGUYÊN VĂN trong tập số builder đã
    in từ pipeline (bảng/KPI/footnote) — trừ số nguyên 0..12 đứng trơn (KHÔNG kèm %/điểm %/thập
    phân) và năm 20xx. Sai ⇒ NarrativeError.
  • DẤU/HƯỚNG (r3 N1): số có dấu viết tay (−/+) hoặc số % đứng sau từ chỉ hướng (tăng/lãi ↔
    giảm/lỗ/sụt/mất/âm) phải khớp DẤU của chính số đó trong pipeline. "tăng 1,89%" khi pipeline
    in "−1,89%" ⇒ từ chối. Có "từ/còn/xuống/lên/về/đến…" chen giữa ⇒ không suy hướng (mô tả mức).
  • Chặn sớm markdown thô / token rỗng (nan/None/**…) — CÙNG danh sách với artifact_lint (vocab.py).
  • Không tên nội bộ (INTERNAL_RE). File nhà đầu tư (SpaceX) cấm thêm từ vận hành (OPS_RE).
  • Mục `internal` (CHỈ ZaloPay — kênh nội bộ): ≤ 6 khối × ≤ 5 gạch × ≤ 40 từ; số được phép
    (chép từ script nội bộ như intraday_oos_monthly.py) nhưng được in dưới nhãn "nội bộ".
Builder TỪ CHỐI narrative vi phạm (raise) — người gọi phải sửa narrative, không được nới luật.
"""
import json
import re
import unicodedata

MAX_WORDS, MAX_ITEMS = 25, 3
SECTIONS = ("bridge", "performance", "risk", "attribution", "trades", "portfolio", "market", "costs")
try:
    from .vocab import INTERNAL_RE, RAW_MD  # noqa: E402 (một nguồn với artifact_lint.py)
except ImportError:
    from vocab import INTERNAL_RE, RAW_MD  # noqa: E402
OPS_RE = re.compile(r"\b(job|dispatch|gate|cron|bug|selfcheck|circuit breaker|lỗi hệ thống|bot chết)\b", re.I)
NUM_RE = re.compile(r"\d[\d.,/]*\d|\d")
SIGNED_RE = re.compile(r"([−+-]?)(\d[\d.,/]*\d|\d)(\s*(?:%|điểm %))?")
POS_W, NEG_W = {"tăng", "lãi", "lời", "dương"}, {"giảm", "lỗ", "sụt", "mất", "âm"}
LEVEL_W = {"từ", "còn", "xuống", "lên", "về", "đến", "tới", "ở", "mức", "quanh", "khoảng"}


class NarrativeError(ValueError):
    pass


def nfc(s):
    return unicodedata.normalize("NFC", str(s))


def words(s):
    return len(re.sub(r"<[^>]+>", "", s).split())


def num_tokens(s):
    return [t.rstrip(".,") for t in NUM_RE.findall(nfc(s))]


def signed_tokens(s):
    """→ [(token, dấu '+'/'-'/'', là_phần_trăm, chữ_đứng_trước)] theo thứ tự xuất hiện."""
    s = nfc(s)
    out = []
    for m in SIGNED_RE.finditer(s):
        if m.start() and (s[m.start() - 1].isdigit() or s[m.start() - 1] in ".,"):
            continue
        sign = {"−": "-", "-": "-", "+": "+"}.get(m.group(1), "")
        if sign == "-" and m.start() and s[m.start() - 1].isalnum():
            sign = ""  # gạch nối trong từ (vd "T-1"), không phải dấu trừ
        out.append((m.group(2).rstrip(".,"), sign, bool(m.group(3)), s[:m.start()]))
    return out


def fact_signs(facts_text):
    """token → tập dấu pipeline đã in: '-' nếu có '−'/'-' ngay trước, ngược lại '+'."""
    d = {}
    for t, sign, _, _ in signed_tokens(facts_text):
        d.setdefault(t, set()).add("-" if sign == "-" else "+")
    return d


def implied_sign(sign, is_pct, before):
    if sign:
        return sign
    if not is_pct:
        return ""
    for w in reversed(re.findall(r"[^\W\d_]+", before.lower())[-3:]):
        if w in LEVEL_W:
            return ""
        if w in POS_W:
            return "+"
        if w in NEG_W:
            return "-"
    return ""


def _free_number(t):
    if re.fullmatch(r"\d{1,2}", t) and int(t) <= 12:
        return True
    return bool(re.fullmatch(r"20\d\d", t))


def load(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate(nar, facts_text, *, investor_facing, allow_internal):
    """nar: dict | None. facts_text: toàn bộ chữ số builder đã in. → nar đã chuẩn hoá (NFC).
    Raise NarrativeError liệt kê MỌI vi phạm (không dừng ở lỗi đầu)."""
    if nar is None:
        return None
    errs = []
    facts = set(num_tokens(facts_text))
    signs = fact_signs(facts_text)
    out = {"headline": nfc(nar.get("headline", "")).strip(), "key_points": [], "sections": {},
           "outlook": [], "internal": []}

    def check_text(where, s, max_words=MAX_WORDS, numbers=True, internal_ok=False):
        s = nfc(s).strip()
        if not s:
            errs.append(f"{where}: rỗng")
        if words(s) > max_words:
            errs.append(f"{where}: {words(s)} từ > {max_words}")
        m = None if internal_ok else INTERNAL_RE.search(s)
        if m:
            errs.append(f"{where}: tên nội bộ '{m.group(0)}'")
        if investor_facing:
            m = OPS_RE.search(s)
            if m:
                errs.append(f"{where}: từ vận hành '{m.group(0)}' trong báo cáo nhà đầu tư")
        for pat in RAW_MD:
            m = re.search(pat, s, flags=re.M)
            if m:
                errs.append(f"{where}: markdown thô/giá trị rỗng ({pat}) gần {s[max(0, m.start() - 20):m.end() + 20]!r}")
        if numbers:
            toks = signed_tokens(s)
            bad = [t for t, sg, is_pct, _ in toks if t not in facts and not (_free_number(t) and not is_pct and not sg)]
            if bad:
                errs.append(f"{where}: số không có trong số liệu pipeline đã in {bad} — narrative KHÔNG được tự viết số")
            for t, sg, is_pct, before in toks:
                want = implied_sign(sg, is_pct, before)
                if want and t in signs and want not in signs[t]:
                    got = "âm" if signs[t] == {"-"} else "dương"
                    errs.append(f"{where}: sai DẤU/hướng — narrative ngụ ý {'âm' if want == '-' else 'dương'} cho {t} nhưng pipeline in {got}")
        return s

    if out["headline"]:
        check_text("headline", out["headline"])
    kp = nar.get("key_points") or []
    if len(kp) > MAX_ITEMS:
        errs.append(f"key_points: {len(kp)} gạch > {MAX_ITEMS}")
    out["key_points"] = [check_text(f"key_points[{i}]", s) for i, s in enumerate(kp[:MAX_ITEMS])]
    for k, items in (nar.get("sections") or {}).items():
        if k not in SECTIONS:
            errs.append(f"sections.{k}: mục không có trong khung ({', '.join(SECTIONS)})")
            continue
        if len(items) > MAX_ITEMS:
            errs.append(f"sections.{k}: {len(items)} gạch > {MAX_ITEMS}")
        out["sections"][k] = [check_text(f"sections.{k}[{i}]", s) for i, s in enumerate(items[:MAX_ITEMS])]
    ol = nar.get("outlook") or []
    if len(ol) > 4:
        errs.append(f"outlook: {len(ol)} kịch bản > 4")
    for i, r in enumerate(ol[:4]):
        row = {}
        for f in ("scenario", "condition", "invalidation"):
            row[f] = check_text(f"outlook[{i}].{f}", r.get(f, ""), max_words=20)
        row["prob"] = nfc(r.get("prob", "")).strip()
        if row["prob"]:
            check_text(f"outlook[{i}].prob", row["prob"], max_words=6, numbers=False)
        out["outlook"].append(row)
    internal = nar.get("internal") or []
    if internal and not allow_internal:
        errs.append("internal: chỉ báo cáo nội bộ (ZaloPay) được có mục nội bộ")
    if len(internal) > 6:
        errs.append(f"internal: {len(internal)} khối > 6")
    for i, blk in enumerate(internal[:6]):
        its = blk.get("bullets") or []
        if len(its) > 5:
            errs.append(f"internal[{i}]: {len(its)} gạch > 5")
        out["internal"].append({"title": check_text(f"internal[{i}].title", blk.get("title", ""), numbers=False, internal_ok=True),
                                "bullets": [check_text(f"internal[{i}].bullets[{j}]", s, max_words=40, numbers=False, internal_ok=True)
                                            for j, s in enumerate(its[:5])]})
    if errs:
        raise NarrativeError("narrative bị TỪ CHỐI:\n  - " + "\n  - ".join(errs))
    return out
