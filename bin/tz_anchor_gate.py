#!/usr/bin/env python3
"""tz_anchor_gate.py <file.py> [...]   |   --scan   |   --seed-baseline   |   --update-baseline <file.py>

Pre-commit gate — CHẶN `datetime.now()` TRẦN và `date.today()` (không neo timezone), tức
coding_guidelines.md §16 biến thành điều kiện CƠ HỌC để commit.

WHY (không phải một đoạn văn nữa — §16 đã có từ 2026-07 và VẪN lọt):
code-quality-weekly 2026-08-30 tìm ra **5 finding cùng một lớp lỗi trong 1 tuần**, ở 2 repo:
  - WorkingClaude `20bf2f20`: golive_recommend_v23.py:85 (END/START/START_BR/START_VNI) +
    :1216 (`Generated {datetime.now():…}`) + dna_report.py:69 (`date.today()` tính stale-flag DT5G).
  - mike `b26008a6`: agents/Taylor/anomaly_scan.py:379 + insider_flags.py:231 (default `asof`).
Cả 5 đều LATENT trên host này (host ở +07 và crontab có `TZ=Asia/Ho_Chi_Minh` che mất), chỉ nổ
khi chạy tay/dispatch dưới env khác — đúng cái mà §16 dặn và đúng cái mà con-người-phải-nhớ
không chặn được. User duyệt biến thành lint rule 2026-08-30.

CHỮ KÝ (AST, không regex — `datetime.now(tz)` và `datetime.now()` chỉ khác nhau ở số ARG, thứ
regex không đếm được qua xuống dòng):
  một `ast.Call` là VI PHẠM khi ĐỦ 3 điều kiện —
    (a) `func` là Attribute có `attr` ∈ {`now`, `today`};
    (b) receiver render ra tên có thành phần CUỐI ∈ {`datetime`, `date`} — bắt mọi cách import
        đang dùng thật trong 2 repo: `datetime.now`, `datetime.datetime.now`, `dt.datetime.now`,
        `_dt.datetime.now`, `_d.datetime.now`, `date.today`, `datetime.date.today`,
        `dt.date.today`, `_dt.date.today`. Điều kiện này là cái tách khỏi `okf.today()`,
        `pd.Timestamp.now()` (xem CÒN HỞ) và mọi `.now()` của thư viện khác;
    (c) KHÔNG có argument nào (`len(args) == 0 and len(keywords) == 0`).
  (c) chính là điều CHO PHÉP: `datetime.now(_ICT)`, `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))`,
  `datetime.now(tz=...)`, và `datetime.now(timezone.utc)` — bước đầu của ICT-anchor pattern
  `datetime.now(timezone.utc) + timedelta(hours=7)` mà chính 2 commit fix hôm nay đã dùng.

RATCHET, không phải chặn tuyệt đối (cùng khuôn bin/code_quality_gate.sh): chỉ BLOCK khi số vi
phạm của CHÍNH file đó TĂNG so với kb/tz_anchor_baseline.json. File không có trong baseline →
baseline ngầm định 0. Nợ cũ (đã kiểm kê, xem baseline) không bị bắt sửa ngay.

HAI RULE = HAI NAMESPACE ĐỘC LẬP trong CÙNG file baseline — `"files"` (rule 1, datetime.now()
trần) và `"tdays_files"` (rule 2, tdays() thiếu vn_holidays). Ratchet per-file TÁCH RIÊNG cho
từng rule: 1 file có thể tăng nợ rule 1 mà rule 2 không đổi và ngược lại — KHÔNG cộng gộp 2 con
số khác BẢN CHẤT lỗi vào chung 1 ngưỡng (tăng thật của rule này có thể bị nợ cũ của rule kia che
mất nếu gộp). `RULES` (danh sách rule + detector + label) là điểm mở rộng duy nhất nếu có rule 3.

BASELINE-KEY: chuẩn hoá về đường dẫn tương đối so với `/home/trido/thanhdt/WorkingClaude` —
"mike/bin/x.py", "dna_report.py", "trading_bot/y.py". Đúng quy ước kb/code_quality_baseline.json
đang dùng, và ổn định qua mọi worktree của mike (mike/agents/wt-<thread>/... map về "mike/...").

HAI REPO, MỘT BASELINE: gate được wire vào cả `mike/.pre-commit-config.yaml` (repo mike) lẫn
`/home/trido/thanhdt/.pre-commit-config.yaml` (repo ngoài, chứa WorkingClaude/) vì lớp lỗi này
đã nổ ở CẢ HAI. Baseline sống trong repo mike (kb/). Auto-update baseline (+ `git add` để nó
nằm cùng commit) CHỈ chạy khi đang commit TRONG repo mike — commit từ repo ngoài không được
phép ghi vào repo lồng rồi bỏ đó unstaged. Từ repo ngoài gate chỉ CƯỠNG CHẾ (đọc baseline), và
in ra lệnh `--update-baseline` nếu cần siết lại bằng tay.

ESCAPE HATCH — 3 đường, cố ý khác nhau về HỆ QUẢ:
  - `SKIP=tz-anchor-gate git commit …` — pre-commit hỗ trợ sẵn; dùng khi bị chặn vì LỆCH NHÁNH
    (baseline neo theo checkout canonical; worktree đang ở commit cũ có thể đếm ra nhiều hơn ở
    file mình không hề sửa — arch-review 2026-08-30 F6).
  - `MIKE_TZ_GATE=warn` — qua ĐÚNG lần này, và cố ý **KHÔNG nâng baseline** (khác
    bin/code_quality_gate.sh, nơi warn ghi nợ mới thành hợp lệ vĩnh viễn). Lần commit sau vẫn
    chặn. Lách không được phép âm thầm biến thành chấp nhận (F3).
  - `--update-baseline` — mặc định CHỈ hạ được baseline (siết). Nâng phải nói ra bằng
    `--accept-new-debt` (F4).
  - `MIKE_TZ_GATE=off` — tắt hẳn. Thắng MỌI thứ khác, kể cả guard env knob ở dưới.

RULE 2 (thêm 2026-09-05, user duyệt qua Discord cùng ngày) — `tdays()` THIẾU vn_holidays, tức
"pattern đếm ngày lịch không biết lễ VN" bị escalate `retro-pattern-recurring-tdays-holiday-2days`
sau 3 lần va chạm CÙNG lớp lỗi trong 2 ngày (`0b83f507`, `81cc0428` ở `mike/bin/`, rồi
`96ebd124` ở `WorkingClaude/macro_healthcheck.py` — call-site thứ 3 lọt vì 2 bản vá trước không
phủ tới repo ngoài). Xem `kb/incidents/2026-09/2026-09-04-macro-health-failed-holiday-tdays.md`.

CHỮ KÝ RULE 2 (hẹp có chủ đích — KHÔNG quét mù mọi `np.busday_count`/date-diff, đó chính là rủi
ro false-positive Mike cảnh báo user trước khi duyệt): một `ast.Call` là VI PHẠM khi ĐỦ 2 điều —
  (a) tên hàm được gọi (Name.id hoặc Attribute.attr) TRÙNG KHỚP TUYỆT ĐỐI (không phân biệt
      hoa/thường) với `"tdays"` — đúng quy ước đặt tên đã dùng thật (`def tdays(...)`), KHÔNG bắt
      `np.busday_count` trần, biến đổi ngày kiểu khác, hay biến thể tên như `get_tdays`/
      `calc_tdays_age` (đo thật 2026-09-05: bản đầu dùng "chứa chuỗi con" tự bắt NHẦM chính
      `tdays_violations()`/`test_*_tdays()` của module gate/selfcheck — khớp tuyệt đối loại bỏ
      hẳn lớp false-positive này, đổi lấy việc không tự mở rộng sang tên hàm tương lai chưa tồn
      tại; xem KHÔNG LÀM và KHÔNG LÀM CÒN HỞ bên dưới cho lựa chọn có chủ đích này);
  (b) KHÔNG đủ MỘT TRONG BA lối thoát sau (đầu tiên xét PER-CALL, hai lối còn lại xét theo SCOPE):
      (b1) CHÍNH lệnh gọi đó có keyword argument tên `vn_holidays` — ân xá CHỈ lệnh gọi này, không
           lan sang lệnh `tdays()` khác trong cùng hàm (arch-review vòng 1 RULE-2, F1: bản đầu ân
           xá theo SCOPE cho `vn_holidays=` khiến CẢ HÀM được miễn trừ vĩnh viễn chỉ vì MỘT lệnh
           gọi có kwarg đó — đo được: revert `add_source()` dòng 100 về đúng bug SEV1 gốc
           `tdays(as_of)` trần vẫn lọt vì marker khác trong cùng scope còn sống; per-call sửa
           đúng lỗ này);
      (b2) hàm BAO QUANH lệnh gọi (nearest enclosing `def`/`async def`, hoặc top-level module nếu
           không nằm trong `def` nào) có tham chiếu `is_holiday` ở đâu đó trong CHÍNH phạm vi của
           nó (không tính xuống `def` lồng bên trong — scope khác) — khớp TUYỆT ĐỐI trên cả
           `ast.Attribute.attr` lẫn `ast.Name.id` (không phải substring — bản đầu dùng substring
           trên Name, cùng họ lỗi F1: identifier chỉ CHỨA "is_holiday" như `_vn_is_holiday` không
           còn được tính là marker thật);
      (b3) chữ ký của `def` bao quanh có tham số tên `vn_holidays` (bắt ca chuyển tiếp THẬT bằng
           VỊ TRÍ `tdays(a, vn_holidays)` — chuyển tiếp bằng KEYWORD đã đi qua (b1) rồi, không
           cần (b3) — CHỈ kiểm khai báo, KHÔNG kiểm có thật sự dùng tham số đó hay không, xem
           `_scope_has_vn_holidays_param`).
  Ca thật `add_source()` (macro_healthcheck.py:93-100) chỉ có 1 câu
  `tdays(as_of, vn_holidays=(kind == "trading_vn"))` phục vụ CẢ nhánh Mỹ (`kind="trading"` →
  `vn_holidays=False`) lẫn nhánh VN (`kind="trading_vn"` → `True`) — PASS qua (b1) vì `vn_holidays=`
  nằm ngay trên CHÍNH lệnh gọi đó. Đây chính là điểm Mike lưu ý: KHÔNG được hiểu nhầm
  "kind=='trading'" (lịch Mỹ, cố ý Mon-Fri thuần, us_market_history.csv) là một nhánh cần sửa.

KHÔNG LÀM (phạm vi bị THU HẸP có chủ đích theo user 2026-09-05, không phải thiếu sót) — Mike đề
xuất thêm "hoặc đối số/biến `kind` mang giá trị KHÔNG PHẢI marker lịch nước ngoài" làm tín hiệu
nhận-diện thứ 2; KHÔNG hiện thực hoá tín hiệu đó thành rule AST vì `kind` là tên tham số CỰC
PHỔ BIẾN trong codebase (dùng cho nhiều mục đích không liên quan ngày tháng) — biến nó thành
điều kiện AST sẽ tự sinh false-positive trên diện rộng, đúng thứ user đã cảnh báo trước khi
duyệt. Nếu tương lai xuất hiện call-site cùng lớp lỗi mà rule (a) bỏ lọt, xử lý bằng sweep thủ
công (grep) một lần rồi mở rộng rule có chủ đích, không nới điều kiện (a) một cách mù quáng.

CÒN HỞ CHUNG (cả 2 rule, ghi ở đây, đừng để ai tưởng gate phủ cả họ lỗi):
  - `pd.Timestamp.now()` / `pd.Timestamp.today()` naive-host-local Y HỆT về ngữ nghĩa (đo được
    75 + 46 call trong WorkingClaude hôm nay) nhưng KHÔNG bị chặn — phạm vi user duyệt là
    `datetime.now()`/`date.today()`. Muốn mở rộng thì phải rebuild baseline trước, không chỉ
    nới điều kiện (b).
  - `datetime.utcnow()` (288 call) cũng trả naive nhưng là naive-UTC, không phụ thuộc TZ host ⇒
    KHÔNG thuộc lớp lỗi §16 này. Cố ý không chặn.
  - `datetime.fromtimestamp(t)` / `date.fromtimestamp(t)` không có tz — naive-host-local y hệt,
    CHƯA canh (arch-review 2026-08-30 F8).
  - Dạng tham chiếu rồi gọi: `n = datetime.now; n()` — AST không nối được 2 câu lệnh. CHƯA canh
    (áp dụng cho CẢ rule 2: `f = tdays; f(x)` cũng không bắt được); selfcheck ghi nó ở mục KNOWN
    GAP chứ KHÔNG phải control "đúng".
  - `datetime.now(*args)` / `now(**kw)` — có argument nên qua điều kiện (c). CHƯA canh.
  - Rule 2 dùng KHỚP TUYỆT ĐỐI `fname.lower() == "tdays"`, KHÔNG phải "chứa chuỗi con" — bản đầu
    dùng substring và TỰ BẮT NHẦM `tdays_violations()`/`test_detector_tdays()`/`test_historical_
    tdays()` của chính module gate/selfcheck khi chạy `--scan` thật lần đầu (đo được, không phải
    giả định). Hệ quả: biến thể tên như `get_tdays`/`calc_tdays_age` KHÔNG bị bắt — CHƯA canh,
    chấp nhận đổi lấy loại bỏ lớp false-positive tự-tham-chiếu; nếu tương lai xuất hiện call-site
    thật với tên biến thể, mở rộng bằng allowlist tên cụ thể (không quay lại substring mù).
  - Rule 2 KHÔNG resolve alias import kiểu `from macro_healthcheck import tdays as t; t(x)` — tên
    hàm sau alias không còn khớp `"tdays"` nên trượt điều kiện (a). Đo hôm nay: 0 ca sống trong 2
    repo (không ai import lại `tdays`), nên chưa cần bịt như rule 1 đã bịt alias `datetime`
    (`_alias_receivers`) — CHƯA canh, ghi nhận known-gap.
  - `_scope_has_vn_holidays_param` (b3) chỉ kiểm hàm bao quanh có KHAI BÁO tham số `vn_holidays`
    trong chữ ký, KHÔNG kiểm tham số đó có thật sự được CHUYỂN TIẾP vào lệnh gọi `tdays()` hay
    không: `def f(a, vn_holidays=False): return tdays(a)` (khai báo rồi bỏ xó, không dùng ở đâu
    cả) vẫn PASS qua (b3) dù `tdays(a)` bên trong trần hoàn toàn. CHƯA canh — chấp nhận vì (b3)
    chỉ cần cho ca chuyển tiếp THẬT bằng VỊ TRÍ (chuyển tiếp bằng keyword đã đi qua (b1) per-call
    rồi, xem docstring `_scope_has_vn_holidays_param`). Cũng KHÔNG bắt được `**kwargs` mù
    (`def f(a, **kw): return tdays(a, **kw)` bị FLAG OAN vì tên tham số thật là `kw` chứ không
    phải `vn_holidays`) — chấp nhận vì flag oan an toàn hơn bỏ sót.
  - Rule 2 KHÔNG kiểm tra interprocedural: call-site GỌI `add_source(..., kind="trading_vn")`
    không tự nó bị xét — chỉ có ĐỊNH NGHĨA `add_source` (nơi `tdays()` thực sự được gọi) mới nằm
    trong phạm vi rule. Nếu tương lai một wrapper mới gọi `tdays()`-tương-tự qua nhiều lớp hàm mà
    không lộ ra tên "tdays" ở lớp ngoài cùng, rule không bắt được — chấp nhận theo phạm vi đã duyệt.
  - Bash `date` không neo TZ: ngoài phạm vi (bin/utc_text_gate.sh canh nửa văn bản gửi người).
  - ⚠️ Rule 2 chỉ soi được file `.py` — **2/3 sự cố trích dẫn ở trên (`0b83f507`, `81cc0428`) nằm
    trong `mike/bin/preflight_check.sh` (bash, gọi Python qua heredoc)**, cấu trúc mà gate AST
    Python KHÔNG BAO GIỜ đọc được. Rule 2 hiện chỉ phủ 1/3 sự cố gốc (call-site thứ 3,
    `WorkingClaude/macro_healthcheck.py`) — tính đến 2026-09-05, TOÀN BỘ 2 repo chỉ có 2 call-site
    `tdays()` sống, cả hai đều ở file đó. Một regression tương tự lặp lại TRONG `preflight_check.sh`
    sẽ KHÔNG bị gate này chặn — biết trước, chấp nhận theo phạm vi user đã duyệt (Python-only).
  - File .py NGOÀI `WC_ROOT` và ngoài mọi checkout mike (vd 20 worktree của repo ngoài ở
    /home/trido/thanhdt/wt-*) không có baseline-key ⇒ KHÔNG gate được. Từ 2026-08-30 gate KÊU
    ra stderr thay vì im (F2), nhưng vẫn không chặn. `WorkingClaude/macro_healthcheck.py` (call-site
    thứ 3 của sự cố gốc) ĐÃ nằm trong TRACKED_ROOTS hiện có (`WorkingClaude/*.py`) — không phải
    known-gap, xác nhận lại 2026-09-05.

⚠️ `pre-commit run --all-files` TRONG repo mike sẽ chạy tới nhánh auto-update và GHI + `git add`
baseline production NGOÀI mọi commit (không có cơ chế stash của commit thật che). Không script
nào trong fleet làm việc này hôm nay; nếu chạy tay thì kiểm `git status kb/` sau đó.

Escape hatch (cùng khuôn MIKE_CQ_GATE / MIKE_DIAG_GATE / MIKE_COMMIT_GATE):
env MIKE_TZ_GATE=warn hạ BLOCK xuống cảnh báo không chặn; =off tắt hẳn.
"""
import ast
import json
import os
import subprocess
import sys

MIKE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# MIKE_TZ_GATE_ROOT / _BASELINE / _ROOTS: override CHỈ dành cho sandbox của
# bin/tz_anchor_gate_selfcheck.py. CHỈ có hiệu lực khi ĐI KÈM MIKE_TZ_GATE_SELFCHECK=1 — một
# biến sót lại trong môi trường (shell còn export, cron kế thừa, wrapper quên unset) mà đổi được
# WC_ROOT là đủ biến gate production thành no-op im lặng: mọi file thành "ngoài WC_ROOT" ⇒
# không có baseline-key ⇒ rc=0 (đã repro, arch-review vòng 2 R4). Cùng khuôn với
# `_resolve_target()` ở phía selfcheck, vốn đã từ chối MIKE_TZ_GATE_TARGET không có cờ.
_SELFCHECK = os.environ.get("MIKE_TZ_GATE_SELFCHECK") == "1"
# CHỈ TÍNH ở module scope, KHÔNG raise ở đây: `MIKE_TZ_GATE=off` là công tắc tắt hẳn được
# docstring và tz_anchor_gate_shim.sh quảng cáo là lối thoát cuối; raise ở module scope chạy
# TRƯỚC khi main() đọc `mode` ⇒ một biến sót lại làm rc=1 trên file SẠCH mà KHÔNG lối thoát nào
# gỡ được — đúng hình dạng F1 mà cả bản vá này sinh ra để diệt (arch-review vòng 3).
_STRAY = [
    k for k in ("MIKE_TZ_GATE_ROOT", "MIKE_TZ_GATE_BASELINE", "MIKE_TZ_GATE_ROOTS")
    if os.environ.get(k) and not _SELFCHECK
]

WC_ROOT = (os.environ.get("MIKE_TZ_GATE_ROOT") if _SELFCHECK else None) or "/home/trido/thanhdt/WorkingClaude"
BASELINE = (os.environ.get("MIKE_TZ_GATE_BASELINE") if _SELFCHECK else None) or os.path.join(
    MIKE_ROOT, "kb", "tz_anchor_baseline.json"
)

BAD_ATTRS = {"now", "today"}
DATETIME_RECEIVERS = {"datetime", "date"}


def _render(node):
    """Attribute/Name chain -> dotted string; '?' cho mắt xích không phải tên."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _render(node.value) + "." + node.attr
    return "?"


def _alias_receivers(tree):
    """Tên cục bộ trỏ tới `datetime.datetime` / `datetime.date` trong CHÍNH file này.

    `from datetime import datetime as dtm` rồi `dtm.now()` là cùng một lỗi nhưng receiver không
    còn tên `datetime` ⇒ điều kiện (b) trượt. Đọc import của file thì bịt được, không cần đoán.
    (arch-review 2026-08-30 F8 — đo được 0 ca sống trong 2 repo, nhưng bịt là MIỄN PHÍ.)
    """
    names = set(DATETIME_RECEIVERS)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "datetime":
            for a in node.names:
                if a.name in DATETIME_RECEIVERS and a.asname:
                    names.add(a.asname)
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "datetime" and a.asname:
                    names.add(a.asname)  # `import datetime as dt` -> dt.datetime.now / dt.date.today
    return names


_PARSE_ERR = {}   # abspath -> nguyên văn exception, để người gọi in ra được


def _parse_file(path):
    """-> ast.Module, hoặc **None** nếu KHÔNG parse được (lỗi ghi vào _PARSE_ERR).

    ⚠️ None ≠ [] và đây là khác biệt SỐNG CÒN (arch-review vòng 5, killer — xem docstring cũ của
    `violations()`, nguyên nhân giữ nguyên). KHÔNG cache theo path: `violations()` và
    `tdays_violations()` parse lại file riêng — tốn thêm 1 lần đọc/file (rẻ, gate chạy one-shot
    trên vài trăm file), đổi lấy loại bỏ hẳn một lớp bug cache-cũ — selfcheck ghi CÙNG 1 đường
    dẫn tạm với NỘI DUNG khác nhau cho từng ca test trong CÙNG process; một bản v1 của hàm này
    cache theo abspath và trả TREE CŨ cho ca thứ 2 trở đi ⇒ 9 ca CONTROL báo sai (bắt được bởi
    chính selfcheck ngay lần chạy đầu — không phải giả định, đã đo).
    """
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError) as e:
        _PARSE_ERR[os.path.abspath(path)] = f"{type(e).__name__}: {e}"
        return None
    return tree


def _tz_arg_is_none(node):
    """`datetime.now(None)` / `datetime.now(tz=None)` — CÓ argument nhưng vô hiệu, naive y hệt."""
    for a in list(node.args) + [k.value for k in node.keywords]:
        if not (isinstance(a, ast.Constant) and a.value is None):
            return False
    return bool(node.args or node.keywords)


def violations(path):
    """-> [(lineno, 'datetime.now()' | 'date.today()')], hoặc **None** nếu KHÔNG parse được.

    Người gọi PHẢI xử lý None: KÊU ra stderr rồi BỎ QUA file (không gate, không đụng baseline) —
    xem `_parse_file()` cho lý do None ≠ [].
    """
    tree = _parse_file(path)
    if tree is None:
        return None
    receivers = _alias_receivers(tree)
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in BAD_ATTRS:
            continue
        recv = _render(func.value)
        if recv.split(".")[-1] not in receivers:
            continue
        if (node.args or node.keywords) and not _tz_arg_is_none(node):
            continue
        hits.append((func.lineno, f"{recv}.{func.attr}()"))
    return sorted(hits)


TDAYS_MARKER = "tdays"

# Mọi node AST tự mở SCOPE RIÊNG trong Python — không chỉ def/async def. `_same_scope_nodes`
# phải dừng lại ở TẤT CẢ, không riêng FunctionDef/AsyncFunctionDef (arch-review vòng 3, B2): bỏ
# sót Lambda/ClassDef/comprehension nghĩa là `hols = [d for d in ds if is_holiday(d)]` rồi
# `age = tdays(as_of)` TRẦN ngay sau đó vẫn được ân xá — đúng hình dạng hàm mà rule này sinh ra
# để canh. Comprehension (ListComp/SetComp/DictComp/GeneratorExp) VÀ Lambda đều là EXPRESSION
# (không phải statement), nên không bao giờ xuất hiện làm `stmt` top-level của `scope.body` —
# chúng chỉ lộ ra qua `iter_child_nodes()` bên trong `walk()`; liệt ClassDef vào đây để class lồng
# bên trong 1 hàm cũng được coi là scope riêng, giống hệt cách nó đã được coi từ trước cho def lồng.
SCOPE_BOUNDARY_TYPES = (
    ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef,
    ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
)


def _same_scope_nodes(scope):
    """Mọi node con trong PHẠM VI RIÊNG của `scope` (Module hoặc FunctionDef/AsyncFunctionDef),
    KHÔNG đi xuống các node tự mở SCOPE RIÊNG khác (`SCOPE_BOUNDARY_TYPES` — def/async def lồng,
    lambda, class, comprehension) — đó là scope KHÁC, dấu hiệu nhận-biết-lễ trong đó không tính
    là "cùng hàm" với call-site đang xét (và ngược lại). Mở rộng khỏi chỉ FunctionDef/
    AsyncFunctionDef sau arch-review vòng 3 (B2): marker `is_holiday` trong 1 lambda/comprehension/
    class lồng bên trong hàm trước đây rò ra ngoài, ân xá SAI 1 call `tdays()` trần khác trong
    cùng hàm — đúng hình dạng thực tế `hols = [d for d in ds if is_holiday(d)]` rồi
    `age = tdays(as_of)` trần ngay sau.

    ⚠️ Bản đầu có 1 vòng lặp NGOÀI `for stmt in scope.body: yield stmt; yield from walk(stmt)`
    tách rời khỏi bộ lọc FunctionDef bên trong `walk()` — bộ lọc chỉ áp dụng khi `walk()` xét
    CHILD của một node, không áp dụng cho chính STATEMENT top-level của `scope.body`. Hệ quả:
    nếu `stmt` top-level CHÍNH LÀ một `def` lồng, nó vẫn được `walk(stmt)` đi xuống bình thường
    ⇒ marker `is_holiday` bên TRONG def lồng rò ra ngoài, ân xá được call ở scope CHA (arch-review
    vòng 1 RULE-2, hướng ngược của cùng lỗi qua mutation X1/M7; đo trực tiếp: `def outer():
    tdays(d); def inner(): is_holiday(d)` → outer's bare call KHÔNG bị bắt).

    Bản vá ĐẦU của lỗi này (`yield from walk(scope)` gọi thẳng trên `scope`) SAI THEO HƯỚNG
    KHÁC (arch-review vòng 2 RULE-2, R1): `iter_child_nodes(scope)` khi `scope` là FunctionDef
    còn trả về `decorator_list`/`args` (default value, annotation)/`returns` — những biểu thức
    này chạy trong scope BAO QUANH `def`, không phải bên TRONG thân hàm, nhưng lại bị tính là
    "cùng scope" ⇒ `@is_holiday\ndef f(a): return tdays(a)` bị ân xá SAI (đo được, 4 hình dạng:
    decorator/default/annotation/return-type). Cách đúng: seed walk từ CHÍNH `scope.body` (không
    phải `iter_child_nodes(scope)`) và áp DỤNG bộ lọc FunctionDef cho cả statement top-level lẫn
    mọi cấp con — vừa giữ được phạm vi "chỉ thân hàm" như bản gốc, vừa bịt lỗ def-lồng."""
    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, SCOPE_BOUNDARY_TYPES):
                continue
            yield child
            yield from walk(child)
    for stmt in scope.body:
        if isinstance(stmt, SCOPE_BOUNDARY_TYPES):
            continue
        yield stmt
        yield from walk(stmt)


def _contains_holiday_marker(scope):
    """True nếu scope có tham chiếu `is_holiday` (attribute hoặc tên đã import/alias từ
    trading_bot.vn_market, khớp TUYỆT ĐỐI — không phải substring) ở đâu đó trong CHÍNH phạm vi
    của nó (không tính def lồng bên trong, xem _same_scope_nodes).

    KHÔNG còn xét `vn_holidays=` ở đây (đã chuyển thành kiểm PER-CALL trong tdays_violations() —
    xem lý do ở đó): 1 lệnh gọi CÓ vn_holidays= chỉ nên ân xá CHÍNH nó, không phải mọi
    `tdays()` khác trong cùng scope (arch-review vòng 1 RULE-2, F1 — bản trước amnesty theo
    scope khiến `add_source()` thật ân xá vĩnh viễn: dòng 100 có `vn_holidays=` nhưng nếu dòng
    100 bị revert lại thành `tdays(as_of)` trần (đúng bug SEV1 gốc), gate vẫn im vì
    `is_holiday`/`vn_holidays=` KHÁC còn sống trong scope — no-op trên chính file gây sự cố).

    Chỉ tính `ctx=Load` (đang ĐỌC giá trị `is_holiday`, vd gọi nó hoặc truyền nó đi) — KHÔNG tính
    `Store`/`Del` (arch-review vòng 3, B3: `is_holiday = None` hay `del is_holiday` trước đây vẫn
    ân xá dù không hề tham chiếu THẬT tới `trading_bot.vn_market.is_holiday`; docstring này TRƯỚC
    đây cũng overclaim là có kiểm provenance import/alias — thật ra khớp bất kỳ `Name.id`/
    `Attribute.attr` nào trùng "is_holiday", ctx=Load chỉ thu hẹp bớt false-amnesty rẻ tiền nhất,
    KHÔNG phải resolve import thật; vẫn CHƯA canh ca đặt tên biến cục bộ khác trùng tên rồi ĐỌC nó,
    xem KNOWN GAP)."""
    for n in _same_scope_nodes(scope):
        if isinstance(n, ast.Attribute) and n.attr == "is_holiday" and isinstance(n.ctx, ast.Load):
            return True
        if isinstance(n, ast.Name) and n.id == "is_holiday" and isinstance(n.ctx, ast.Load):
            return True
    return False


def _scope_has_vn_holidays_param(scope):
    """True nếu `scope` là 1 def có tham số tên `vn_holidays` trong CHỮ KÝ.

    ⚠️ Chỉ kiểm tra KHAI BÁO, KHÔNG kiểm tra CHUYỂN TIẾP thật: `def f(a, vn_holidays=False):
    return tdays(a)` (tham số khai báo rồi KHÔNG BAO GIỜ dùng ở lệnh gọi) vẫn trả True — CHƯA
    canh, xem KNOWN GAP RULE 2 (`KNOWN_GAPS_TDAYS` trong selfcheck).

    Ca CHUYỂN TIẾP THẬT bằng KEYWORD (`tdays(a, vn_holidays=vn_holidays)`) đã được bắt bởi nhánh
    per-call `vn_holidays=` ở `tdays_violations()`, không cần hàm này. Hàm này chỉ còn cần thiết
    cho ca CHUYỂN TIẾP THẬT bằng VỊ TRÍ (`tdays(a, vn_holidays)` — không có keyword ở lệnh gọi
    nên per-call không thấy được, phải suy từ CHỮ KÝ). ⚠️ KHÔNG bắt được `**kwargs` mù dạng
    `def f(a, **kw): return tdays(a, **kw)` (đo được: BỊ FLAG oan, vì tên tham số thật trong chữ
    ký là `kw` chứ không phải `vn_holidays`) — CHƯA canh, chấp nhận vì đây là ca hiếm và flag oan
    (over-block) an toàn hơn bỏ sót (dưới KHÔNG PHẢI risk như F1)."""
    if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    a = scope.args
    names = {arg.arg for arg in (a.args + a.posonlyargs + a.kwonlyargs)}
    if a.vararg:
        names.add(a.vararg.arg)
    if a.kwarg:
        names.add(a.kwarg.arg)
    return "vn_holidays" in names


def tdays_violations(path):
    """-> [(lineno, 'tdays(...)')], hoặc **None** nếu KHÔNG parse được (cùng hợp đồng None ≠ []
    với `violations()` — xem `_parse_file()`).

    Chữ ký hẹp có chủ đích: chỉ bắt call tới hàm có TÊN KHỚP TUYỆT ĐỐI "tdays" (không phải chứa
    chuỗi con — xem `TDAYS_MARKER`/`fname.lower() != TDAYS_MARKER` bên dưới) mà hàm BAO QUANH lệnh gọi đó
    (nearest enclosing def, hoặc module top-level) không có dấu hiệu nhận-biết-lễ-VN nào trong
    CHÍNH phạm vi của nó. Xem docstring đầu file (RULE 2) cho lý do KHÔNG quét np.busday_count
    trần hay đối số `kind`.
    """
    tree = _parse_file(path)
    if tree is None:
        return None
    parent = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    def enclosing_scope(node):
        cur = parent.get(node)
        while cur is not None:
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return cur
            cur = parent.get(cur)
        return tree  # không nằm trong def nào -> scope = module top-level

    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            fname = func.id
        elif isinstance(func, ast.Attribute):
            fname = func.attr
        else:
            continue
        if fname.lower() != TDAYS_MARKER:
            continue
        if any(kw.arg == "vn_holidays" for kw in node.keywords):
            continue  # PER-CALL: ân xá đúng lệnh gọi này, không lan sang call khác cùng scope
        scope = enclosing_scope(node)
        if _contains_holiday_marker(scope) or _scope_has_vn_holidays_param(scope):
            continue
        hits.append((node.lineno, f"{fname}(...)"))
    return sorted(hits)


# Không phải code của fleet (thư viện vendor / bản sao repo cũ đã chết) hoặc là artifact R&D —
# không gate, không tính vào baseline. `mike_paseo/` là bản SAO cũ của repo mike (git repo riêng,
# worktree đã hỏng, không repo nào track); gate nó = nuôi vi phạm ma trong baseline.
EXCLUDED_DIRS = frozenset((
    "research", "archive", "wc_venv", "__pycache__", ".git", "node_modules", "site-packages",
    "vendor", "stockquery", "mike_paseo",
))
RND_PREFIXES = ("test_", "exp_", "probe_", "stress_")


def is_excluded(rel):
    """rel = baseline-key. Đồng bộ exclude của bin/code_quality_gate.sh, cộng 3 nhóm ở trên.

    Tiền tố R&D kiểm trên MỌI thành phần đường dẫn, không chỉ basename — repo có cả THƯ MỤC
    R&D (`agents/Taylor/probe_golive_live_20260715/`, 20 vi phạm) mà bản chỉ-xét-basename của
    code_quality_gate.sh bỏ lọt (ở đó vô hại vì scope regex hẹp hơn; ở đây thì không).
    """
    parts = rel.split("/")
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True
        if part.startswith(RND_PREFIXES):
            return True
    return False


_TOP_CACHE = {}


def _git_top(directory):
    """Toplevel của checkout chứa `directory` (cache theo thư mục). None nếu không phải git."""
    if directory not in _TOP_CACHE:
        try:
            out = subprocess.run(
                ["git", "-C", directory, "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=False,
            ).stdout.strip()
        except OSError:
            out = ""
        _TOP_CACHE[directory] = out or None
    return _TOP_CACHE[directory]


def baseline_key(path):
    """abs path -> key tương đối WC_ROOT.

    Worktree của mike (mike/agents/wt-<thread>/bin/x.py) PHẢI map về "mike/bin/x.py", nếu không
    cùng một file logic sẽ khớp 2 key khác nhau tuỳ commit từ checkout nào ⇒ baseline ngầm 0 ⇒
    hard-block oan (đã xảy ra thật với code_quality_gate.sh, arch-review Wags_20260823_071251).
    Vì vậy key suy từ `git rev-parse --show-toplevel` của CHÍNH file, KHÔNG cắt chuỗi đường dẫn.
    """
    abs_p = os.path.abspath(path)
    top = _git_top(os.path.dirname(abs_p) or ".")
    if top and os.path.isdir(os.path.join(top, "kb")) and os.path.isfile(os.path.join(top, "bin", "dispatch.sh")):
        return "mike/" + os.path.relpath(abs_p, top)
    if abs_p.startswith(WC_ROOT + "/"):
        return os.path.relpath(abs_p, WC_ROOT)
    return None


def _set_count(files_baseline, key, n):
    """Ghi số vi phạm; n == 0 thì XOÁ key thay vì lưu 0 — baseline ngầm định đã là 0, lưu vào
    chỉ phình file bằng rác (mọi file .py sạch từng đi qua gate sẽ nằm lại đó vĩnh viễn)."""
    if n:
        files_baseline[key] = n
    else:
        files_baseline.pop(key, None)


def load_baseline():
    """-> (baseline_dict, errmsg|None). errmsg != None ⇒ KHÔNG được coi baseline là rỗng.

    Bản trước nuốt ValueError rồi trả {"files": {}} ⇒ một baseline hỏng (rất dễ xảy ra: file
    này bị auto-ghi + `git add` MỖI commit nên là mồi xung đột merge) làm TOÀN BỘ 87 file mang
    nợ cũ hard-block cùng lúc, kèm chẩn đoán SAI "baseline 0" mà gate chưa từng kiểm chứng —
    đúng lớp lỗi §29 (arch-review vòng 5, R5-2). Luật của gate này là "KHÔNG GATE ĐƯỢC ≠ CHẶN".
    """
    try:
        with open(BASELINE, encoding="utf-8") as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return {"files": {}}, None      # chưa seed = nợ 0, đúng nghĩa, không phải lỗi
    except (OSError, ValueError) as e:
        return {"files": {}}, f"{type(e).__name__}: {e}"


def write_baseline(data):
    tmp = BASELINE + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, BASELINE)


# Hai checkout CANONICAL được gate phủ. Liệt kê file bằng `git ls-files` chứ KHÔNG đi bộ cây
# thư mục: repo này có **36 bản sao** của cùng một file logic (worktree `mike/agents/wt-*`,
# `WorkingClaude/wt-*`, `mike/.claude/worktrees/*`, cộng bản sao chết `mike_paseo/`) và
# baseline_key chuẩn hoá tất cả về CÙNG một key ⇒ đi bộ cây thì bản nào thắng là ngẫu nhiên
# theo thứ tự os.walk. Đã cắn thật lúc seed 2026-08-30: anomaly_scan.py vào baseline với 2 vi
# phạm — số của một worktree CŨ chưa có commit b26008a6 — trong khi canonical chỉ còn 1.
# git ls-files còn tự loại untracked/gitignored (mike_paseo là repo lồng, không repo nào track).
TRACKED_ROOTS = (
    ("/home/trido/thanhdt/WorkingClaude/mike", "*.py"),   # repo mike
    ("/home/trido/thanhdt", "WorkingClaude/*.py"),        # repo ngoài, chỉ phần WorkingClaude/
)
if _SELFCHECK and os.environ.get("MIKE_TZ_GATE_ROOTS"):  # selfcheck kiểm nhánh kiểm-kê-thiếu (F5)
    TRACKED_ROOTS = tuple(
        (spec.split("|", 1)[0], spec.split("|", 1)[1] if "|" in spec else "*.py")
        for spec in os.environ["MIKE_TZ_GATE_ROOTS"].split(":")
    )


def enumerate_tracked():
    """-> (paths, ok). ok=False khi BẤT KỲ root nào không đọc được — caller PHẢI không ghi đè
    baseline bằng một kiểm kê thiếu (arch-review 2026-08-30 F5: một root sai đường dẫn cho ra
    15 file/29 vi phạm thay vì 87/157, rc=0, commit được — 72 key biến mất thành ngầm-định-0 và
    mọi commit sau chạm chúng đều hard-block)."""
    paths = []
    ok = True
    for repo, pattern in TRACKED_ROOTS:
        r = subprocess.run(["git", "-C", repo, "ls-files", "-z", pattern],
                           capture_output=True, text=True, check=False)
        if r.returncode != 0:
            print(f"⚠️  không đọc được `git ls-files` ở {repo} — BỎ QUA cây này, kiểm kê sẽ THIẾU.",
                  file=sys.stderr)
            ok = False
            continue
        for rel in r.stdout.split("\0"):
            if rel.endswith(".py"):
                paths.append(os.path.join(repo, rel))
    return paths, ok


def scan_tree(detector=violations):
    """Kiểm kê toàn bộ vi phạm còn sót theo `detector` -> ({baseline_key: [(line, expr)]}, complete).

    `detector` mặc định `violations` (rule 1, tương thích ngược cho code/test gọi không tham số).
    Truyền `tdays_violations` để kiểm kê rule 2. Mỗi lần gọi enumerate lại cây (không cache paths
    giữa 2 rule) — chi phí chấp nhận được, đổi lấy 2 lời gọi độc lập đơn giản, dễ audit.
    """
    found = {}
    paths, complete = enumerate_tracked()
    for p in paths:
        key = baseline_key(p)
        if key is None or is_excluded(key) or not os.path.isfile(p):
            continue
        hits = detector(p)
        if hits is None:
            print(f"⚠️  {key}: KHÔNG parse được ({_PARSE_ERR.get(os.path.abspath(p), '?')}) — "
                  "bỏ qua, kiểm kê sẽ THIẾU.", file=sys.stderr)
            complete = False
            continue
        if hits:
            found[key] = hits
    return found, complete


# Điểm mở rộng duy nhất nếu có rule 3: thêm 1 dict vào đây, không đụng logic main() bên dưới.
RULES = (
    {"key": "files", "detector": violations,
     "label": "datetime.now()/date.today() trần (§16)"},
    {"key": "tdays_files", "detector": tdays_violations,
     "label": "tdays() thiếu vn_holidays trong hàm bao quanh (RULE 2, 2026-09-05)"},
)


def in_mike_repo():
    """Top của checkout đang commit, NẾU top ĐÚNG LÀ checkout sở hữu BASELINE đang dùng.

    ⚠️ Điều kiện phải là `samefile(top/kb/tz_anchor_baseline.json, BASELINE)`, KHÔNG được viết
    thành "BASELINE nằm dưới top": repo lồng nằm BÊN TRONG cây thư mục của repo ngoài, nên
    `abspath(BASELINE).startswith(top + "/")` ĐÚNG cho cả top=/home/trido/thanhdt ⇒ commit từ
    repo NGOÀI sẽ ghi vào baseline của repo lồng rồi `git add` thất bại (path bị gitignore ở đó)
    và để lại dirt trong cây mà consolidate cron `git add -A` mỗi ~15 phút. Đó chính là lỗi
    arch-review vòng 2 (R1) tìm ra trong bản vá F7 của tôi — bản vòng 1 không có lỗ này.

    Vẫn neo theo BASELINE (không phải một tên file cứng) để selfcheck dựng được sandbox repo
    thật mà kiểm nhánh auto-update; điều kiện samefile giữ đúng cả hai tính chất.
    """
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except OSError:
        return None
    if not top:
        return None
    cand = os.path.join(top, "kb", "tz_anchor_baseline.json")
    try:
        return top if os.path.isfile(cand) and os.path.samefile(cand, BASELINE) else None
    except OSError:
        return None


def main(argv):
    mode = os.environ.get("MIKE_TZ_GATE", "block")
    if mode == "off":
        # Quét MỌI phần tử argv, không chỉ argv[0]: logic parse cờ thật ở dưới cũng không phụ
        # thuộc vị trí (`"--update-baseline" in args`), nên chỉ nhìn argv[0] thì
        # `gate.py x.py --update-baseline` im lặng còn `gate.py --update-baseline x.py` thì kêu —
        # cùng một người, cùng một ý định (arch-review vòng 5, R5-5).
        manual = [a for a in argv if a in ("--scan", "--seed-baseline", "--update-baseline")]
        if manual:
            # Chạy TAY mà im hoàn toàn = người chạy tưởng đã re-seed/quét xong (arch-review vòng 4).
            print("⚠️  MIKE_TZ_GATE=off — KHÔNG chạy " + " ".join(manual) + ". Bỏ biến rồi chạy lại.",
                  file=sys.stderr)
        return 0

    if _STRAY:
        raise SystemExit(
            f"❌ tz_anchor_gate: {', '.join(_STRAY)} được đặt mà KHÔNG có MIKE_TZ_GATE_SELFCHECK=1 — "
            "biến này chỉ dành cho sandbox selfcheck; để nguyên sẽ gate SAI baseline hoặc no-op im "
            "lặng. Bỏ biến, chạy qua bin/tz_anchor_gate_selfcheck.py, hoặc MIKE_TZ_GATE=off."
        )

    args = list(argv)
    if args and args[0] == "--scan":
        for rule in RULES:
            found, _ = scan_tree(rule["detector"])
            total = sum(len(v) for v in found.values())
            print(f"\n=== {rule['label']} ===")
            for key in sorted(found):
                for line, expr in found[key]:
                    print(f"{key}:{line}: {expr}")
            print(f"{total} vi phạm / {len(found)} file", file=sys.stderr)
        return 0

    if args and args[0] == "--seed-baseline":
        # Kiểm kê lại toàn bộ nợ cũ (CẢ 2 rule) và GHI ĐÈ baseline. Chỉ chạy tay khi cố ý re-seed
        # (vd mở rộng phạm vi gate); vận hành thường ngày dùng ratchet auto-update ở cuối hàm này.
        # All-or-nothing: nếu MỘT rule kiểm kê thiếu thì KHÔNG ghi rule nào — tránh baseline lệch
        # nhau giữa 2 namespace trong cùng 1 lần seed.
        sections = {}
        for rule in RULES:
            found, complete = scan_tree(rule["detector"])
            if not complete:
                print(f"❌ kiểm kê KHÔNG đầy đủ cho rule '{rule['label']}' (xem cảnh báo ở trên) — "
                      "KHÔNG ghi đè baseline (cả 2 rule).", file=sys.stderr)
                return 1
            sections[rule["key"]] = {k: len(v) for k, v in found.items()}
        data = {
            "_note": "Kiểm kê 2 rule tại thời điểm bật bin/tz_anchor_gate.py — 'files': "
                     "`datetime.now()` trần / `date.today()` (coding_guidelines §16); "
                     "'tdays_files': tdays() thiếu vn_holidays (RULE 2, 2026-09-05). Ratchet "
                     "per-file, MỖI namespace ĐỘC LẬP: nợ cũ không bắt sửa ngay, chỉ không được "
                     "TĂNG. Re-seed: bin/tz_anchor_gate.py --seed-baseline",
        }
        data.update(sections)
        write_baseline(data)
        for rule in RULES:
            sect = sections[rule["key"]]
            print(f"✓ {rule['key']}: {sum(sect.values())} vi phạm / {len(sect)} file")
        return 0

    update_only = "--update-baseline" in args
    accept_new_debt = "--accept-new-debt" in args
    args = [a for a in args if not a.startswith("--")]

    baseline, bl_err = load_baseline()
    if bl_err:
        print(f"⚠️  tz_anchor_gate: KHÔNG đọc được {BASELINE} ({bl_err}) — sổ nợ không dùng "
              f"được thì KHÔNG GATE ĐƯỢC, không phải = CHẶN. {len(args)} file .py qua không "
              "gate. Sửa/khôi phục baseline rồi chạy lại; §16 vẫn áp dụng.", file=sys.stderr)
        return 0
    per_rule_baseline = {rule["key"]: baseline.setdefault(rule["key"], {}) for rule in RULES}

    # counts[rule_key][file_key] = n vi phạm; detail[rule_key][file_key] = [(line, expr)].
    # 1 file chỉ vào counts khi CẢ 2 rule parse được — file không parse được thì KHÔNG rule nào
    # được gate, KHÔNG rule nào đụng baseline (giữ đúng bất biến cũ, mở rộng cho rule 2).
    counts = {rule["key"]: {} for rule in RULES}
    detail = {rule["key"]: {} for rule in RULES}
    for f in args:
        if not os.path.isfile(f):
            continue
        key = baseline_key(f)
        if key is None:
            # KHÔNG được im (arch-review 2026-08-30 F2): 20 worktree của repo ngoài nằm ở
            # /home/trido/thanhdt/wt-*, ngoài WC_ROOT ⇒ trước bản này gate trả rc=0 không một
            # chữ, trong khi dna_report.py:69 `date.today()` vẫn sống nguyên ở đó. Cùng khuôn
            # cảnh báo với bin/code_quality_gate.sh:87.
            print(
                f"⚠️  tz_anchor_gate: {os.path.abspath(f)} nằm ngoài {WC_ROOT} và ngoài mọi "
                "checkout mike — KHÔNG có baseline-key, file này KHÔNG ĐƯỢC GATE.",
                file=sys.stderr,
            )
            continue
        if is_excluded(key):
            continue
        per_file_hits = {}
        parse_failed = False
        for rule in RULES:
            hits = rule["detector"](f)
            if hits is None:
                parse_failed = True
                break
            per_file_hits[rule["key"]] = hits
        if parse_failed:
            # KHÔNG được coi là "sạch": không gate CẢ 2 rule, KHÔNG đụng baseline của rule nào
            # (không vào counts nên nhánh auto-update ở cuối không thấy key này ⇒ không xoá/ghi).
            print(f"⚠️  tz_anchor_gate: {key}: KHÔNG parse được bằng {sys.executable} "
                  f"({_PARSE_ERR.get(os.path.abspath(f), '?')}) — file này KHÔNG ĐƯỢC GATE (cả 2 "
                  "rule) và baseline của nó KHÔNG bị đụng tới. §16 vẫn áp dụng, tự kiểm bằng tay.",
                  file=sys.stderr)
            continue
        for rule in RULES:
            counts[rule["key"]][key] = len(per_file_hits[rule["key"]])
            detail[rule["key"]][key] = per_file_hits[rule["key"]]

    if not any(counts[rule["key"]] for rule in RULES):
        return 0

    if update_only:
        # NÂNG baseline = chấp nhận nợ MỚI vĩnh viễn. Config repo ngoài quảng cáo cờ này là cách
        # "siết bằng tay", nên mặc định nó chỉ được phép SIẾT (hạ) — muốn nới phải nói ra
        # (arch-review 2026-08-30 F4). All-or-nothing CHO CẢ 2 rule: nếu rule nào NÂNG mà chưa
        # accept_new_debt thì KHÔNG ghi rule nào — tránh baseline nửa vời giữa 2 namespace.
        raises_by_rule = {}
        for rule in RULES:
            bl = per_rule_baseline[rule["key"]]
            raises = {k: n for k, n in counts[rule["key"]].items() if n > bl.get(k, 0)}
            if raises:
                raises_by_rule[rule["key"]] = raises
        if raises_by_rule and not accept_new_debt:
            for rule in RULES:
                raises = raises_by_rule.get(rule["key"])
                if not raises:
                    continue
                bl = per_rule_baseline[rule["key"]]
                print(f"  === {rule['label']} ===")
                for k, n in sorted(raises.items()):
                    print(f"  🔴 {k}: baseline {bl.get(k, 0)} → {n} là NÂNG, không phải siết")
            print("--update-baseline mặc định CHỈ siết (hạ) baseline. Chấp nhận nợ mới thì nói rõ:")
            print("  bin/tz_anchor_gate.py --update-baseline --accept-new-debt <file.py>")
            return 1
        changed = False
        for rule in RULES:
            bl = per_rule_baseline[rule["key"]]
            for key, n in counts[rule["key"]].items():
                if bl.get(key, 0) != n:
                    _set_count(bl, key, n)
                    changed = True
                    print(f"  baseline[{rule['key']}]: {key} -> {n}")
        if changed:
            write_baseline(baseline)
            print(f"  ✓ {BASELINE}")
        return 0

    blocked = []   # [(rule, key, old, new)]
    for rule in RULES:
        bl = per_rule_baseline[rule["key"]]
        for key, n in sorted(counts[rule["key"]].items()):
            old = bl.get(key, 0)
            if n > old:
                blocked.append((rule, key, old, n))

    if blocked:
        blocked_rule_keys = {rule["key"] for rule, _, _, _ in blocked}
        for rule, key, old, new in blocked:
            print(f"  🔴 [{rule['label']}] {key}: {new} vi phạm (baseline {old}) — TĂNG [HARD-BLOCK] (tz_anchor_gate.py)")
            for line, expr in detail[rule["key"]][key]:
                print(f"       {key}:{line}: {expr}")
        print()
        if "files" in blocked_rule_keys:
            print("coding_guidelines.md §16 — neo timezone tường minh, đừng tin TZ của host:")
            print('  datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))   # hoặc datetime.now(_ICT)')
            print("  (datetime.now(timezone.utc) + timedelta(hours=7)).date()   # thay date.today()")
        if "tdays_files" in blocked_rule_keys:
            print("RULE 2 (2026-09-05) — hàm đếm ngày kiểu tdays() phải khai báo rõ đã trừ lễ VN:")
            print('  tdays(asof, vn_holidays=True)   # nguồn theo lịch HOSE')
            print('  tdays(asof, vn_holidays=False)  # nguồn theo lịch nước ngoài (Mỹ...) - cố ý')
            print("  (hoặc tham chiếu trading_bot.vn_market.is_holiday ngay trong cùng hàm)")
        print("  Baseline neo theo checkout CANONICAL (master). Đang commit từ worktree/nhánh cũ và")
        print("  KHÔNG hề sửa chỗ đó? Đó là lệch nhánh, không phải nợ mới — rebase, hoặc")
        print("  SKIP=tz-anchor-gate git commit ... (bỏ qua đúng hook này, pre-commit hỗ trợ sẵn).")
        print("  Escape hatch: MIKE_TZ_GATE=warn git commit ...  (qua 1 lần, KHÔNG nâng baseline")
        print("  ⇒ lần commit sau vẫn chặn. Chấp nhận nợ mới thật thì:")
        print("  bin/tz_anchor_gate.py --update-baseline --accept-new-debt <file.py>)")
        if mode == "block":
            return 1
        # CỐ Ý KHÁC bin/code_quality_gate.sh: ở đó warn NÂNG baseline (nợ mới thành hợp lệ vĩnh
        # viễn chỉ vì một lần lách). Ở đây warn cho qua ĐÚNG lần này và dừng luôn — không ghi
        # baseline — nên "lách" không bao giờ âm thầm biến thành "chấp nhận"
        # (arch-review 2026-08-30 F3).
        print("⚠️  downgraded — MIKE_TZ_GATE=warn, commit vẫn qua. Baseline KHÔNG được nâng:")
        for rule, key, old, new in blocked:
            print(f"    [{rule['label']}] {key}: baseline giữ nguyên {old} (file đang {new}) ⇒ commit sau vẫn chặn.")
        return 0

    mike_top = in_mike_repo()
    if mike_top is None:
        # Commit từ repo NGOÀI: không ghi vào repo lồng rồi bỏ đó unstaged.
        return 0

    # Guard này chỉ có tác dụng khi chạy TAY: dưới pre-commit, staged_files_only.py (bản
    # ~/.local/lib/python3.10/site-packages/pre_commit/staged_files_only.py:80-82) đã stash mọi
    # thay đổi chưa stage + `git checkout -- .` TRƯỚC khi hook chạy, nên cây luôn sạch ở đó.
    # Giữ lại vì `--update-baseline`/chạy tay không đi qua cơ chế stash đó (arch-review F7).
    dirty = subprocess.run(
        ["git", "-C", mike_top, "diff", "--name-only", "--", BASELINE],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        print("⚠️  tz_anchor_gate: kb/tz_anchor_baseline.json có sửa đổi chưa stage — bỏ qua auto-update lần này.", file=sys.stderr)
        return 0

    changed = False
    for rule in RULES:
        bl = per_rule_baseline[rule["key"]]
        for key, n in counts[rule["key"]].items():
            if bl.get(key, 0) != n:
                _set_count(bl, key, n)
                changed = True
    if changed:
        write_baseline(baseline)
        print(f"  ✓ baseline updated: {BASELINE}")
        r = subprocess.run(["git", "-C", mike_top, "add", BASELINE], capture_output=True, text=True, check=False)
        if r.returncode != 0:
            print("⚠️  tz_anchor_gate: git add baseline thất bại — baseline đã ghi nhưng CHƯA stage.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
