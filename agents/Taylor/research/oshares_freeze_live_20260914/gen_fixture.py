"""Sinh WorkingClaude/oshares_selfcheck_fixture.py từ fixture_rows.json + windows.json (freeze.py)."""
import json, sys
out = sys.argv[1]
fx = json.load(open("fixture_rows.json")); win = json.load(open("windows.json"))
QC = ("time", "OShares")
CC = ("event_code", "exright_date", "effective_date", "listing_date", "exercise_ratio",
      "issue_volumn", "issue_method_name_vi", "shares_delta", "shares_total_after", "title")
L = ['''# -*- coding: utf-8 -*-
"""oshares_selfcheck_fixture.py — feed BigQuery ĐÓNG BĂNG cho selfcheck `oshares_live` / `oshares_pit`.

VÌ SAO (2026-09-14, user duyệt 23:43 ICT, job Taylor_20260914_164512). `corp_action_daily.py`
chạy `oshares_live.py --selfcheck` làm CỔNG trước khi publish. Các check đọc BQ SỐNG biến "feed
hôm nay trông y hệt hôm nghiệm thu" thành điều kiện publish: một dòng AIS mới của KHP về BQ tối
14/09 đã làm K1/K1b đỏ ⇒ sáng hôm sau không publish. Luật không được rot theo feed (§23 hệ luận 1,
`mike/kb/coding_guidelines_ext.md`).

NGUỒN. Từng dòng dưới đây là dòng `oshares_live._fetch` trả về NGUYÊN VĂN ngày 2026-09-14 (chuỗi
như bq CLI trả — '5.47292E7', '0.0' — không đổi kiểu, không làm tròn). Mỗi mã chỉ giữ một CỬA SỔ
LIỀN NGÀY: trần = asof lớn nhất selfcheck hỏi mã đó; sàn corp rồi sàn quý = ngày MUỘN NHẤT mà mọi
lời gọi tầng ngoài của selfcheck (oshares_at / _ais_verdicts / oshares_pit / oshares_reconciled,
kể cả các lượt vá cổng N3/F1c/N4/A6/A11/A13) vẫn ra output TRÙNG KHÍT từng field với feed BQ đầy
đủ. Không cắt tỉa lẻ từng dòng. Bằng chứng + script tái lập:
`mike/agents/Taylor/research/oshares_freeze_live_20260914/` (capture.py → freeze.py → gen_fixture.py).

ĐỪNG sửa tay một con số ở đây để check xanh lại: fixture là dữ liệu vendor đã chụp, không phải kỳ
vọng. Cần ca mới ⇒ chụp lại bằng capture.py/freeze.py và ghi cửa sổ mới vào docstring này.
"""

FROZEN_AT = "2026-09-14"
Q_COLS = ("time", "OShares")
C_COLS = ''' + repr(CC) + '''

# mã: (trần asof, sàn corp, sàn quý, số dòng quý giữ/đầy đủ, số dòng corp giữ/đầy đủ)
WINDOWS = {''']
for t in sorted(win):
    w = win[t]
    L.append(f'    {t!r}: ({w["hi"]!r}, {w["corp_from"]!r}, {w["q_from"]!r}, '
             f'"{w["n_q"]}/{w["n_q_full"]}", "{w["n_c"]}/{w["n_c_full"]}"),')
L.append("}\n\n_Q = {")
for t in sorted(fx["Q"]):
    if t not in win: continue
    L.append(f"    {t!r}: [")
    for r in fx["Q"][t]:
        L.append(f"        {tuple(r[k] for k in QC)!r},")
    L.append("    ],")
L.append("}\n\n_C = {")
for t in sorted(fx["C"]):
    if t not in win: continue
    L.append(f"    {t!r}: [")
    for r in fx["C"][t]:
        L.append(f"        {tuple(r[k] for k in CC)!r},")
    L.append("    ],")
L.append('''}


def frozen(tickers):
    """(quarters, corp) ĐÚNG hình dạng `oshares_live._fetch(tickers, until)` — dòng dict, sắp theo
    mã (ORDER BY ticker), dict MỚI mỗi lần gọi. Mã không có trong fixture ⇒ KeyError (không bao
    giờ âm thầm trả rỗng: rỗng là một câu trả lời hợp lệ của `oshares_at`, lỗi thì không)."""
    s = sorted(set([tickers] if isinstance(tickers, str) else tickers))
    missing = [t for t in s if t not in _Q]
    if missing:
        raise KeyError(f"mã chưa đóng băng trong oshares_selfcheck_fixture: {missing}")
    return ([dict(zip(("ticker",) + Q_COLS, (t,) + r)) for t in s for r in _Q[t]],
            [dict(zip(("ticker",) + C_COLS, (t,) + r)) for t in s for r in _C[t]])
''')
open(out, "w").write("\n".join(L))
print("wrote", out, len(L), "lines")
