# -*- coding: utf-8 -*-
"""anomaly_gate.py — due-diligence gate DÙNG CHUNG cho mọi bước chọn mã ứng viên MUA.

Chỉ đạo user: MỌI cổ phiếu ứng viên mua — kể cả paper-trading — phải qua due-diligence
gate (loại các mã đang có cờ bất thường/khủng hoảng thật, vd case PNJ 07/2026 lãnh đạo
bị bắt, giá -32% từ đỉnh).

Đây LÀ nguồn sự thật duy nhất cho gate này. Từ 2026-07-21 (job Taylor_20260721_092529 +
Mike áp patch, user duyệt trực tiếp), `deploy_golive_dt5g_v4/golive_recommend_v23.py::
anomaly_excluded` (PRODUCTION) delegate thẳng vào đây (`from anomaly_gate import
anomaly_excluded as _anomaly_excluded_shared`) — không còn bản inline riêng. Consumers:
production (golive_recommend_v23.py) + 3 paper book (pt_capitulation_shadow.py,
pt_v22_dt5g.py, dc_book_waterfall_paper.py). Sửa logic ở đây là sửa cho TẤT CẢ cùng lúc —
đúng như thiết kế 1 nguồn sự thật, không còn nguy cơ 2 bản lệch nhau.
"""
import json
import os
from datetime import timedelta

import pandas as pd

WORKDIR = os.path.dirname(os.path.abspath(__file__))
ANOMALY_TTL_DAYS = 30   # cờ due-diligence còn hiệu lực bao lâu kể từ phiên alert cuối


def anomaly_excluded(asof, ttl_days=ANOMALY_TTL_DAYS, quiet=False):
    """Set ticker có cờ bất thường còn hiệu lực tại `asof`.

    Bước chọn mã cơ học (pb_z cực âm / rating / momentum) KHÔNG biết một cú sập giá là
    "rẻ đi" hay là khủng hoảng doanh nghiệp đang diễn ra — đúng cú sập khủng hoảng lại
    đẩy mã đó lên ĐẦU danh sách mua. Cờ do anomaly_scan.py ghi (data/anomaly_flags.json).

    FAIL-SAFE: file thiếu/hỏng → trả set rỗng + log warning, KHÔNG chặn pipeline.
    """
    p = os.path.join(WORKDIR, "data", "anomaly_flags.json")
    try:
        flags = json.load(open(p, encoding="utf-8"))
        # chuẩn hoá asof (date / Timestamp / str đều nhận) — sai kiểu ở caller mà rơi vào
        # except sẽ TẮT ÂM THẦM cả cái gate an toàn này, nên không để nó có cửa xảy ra.
        d = pd.Timestamp(asof).date()
        # CỬA SỔ HAI ĐẦU: cutoff <= last_alert <= asof. Chặn trên là chống look-ahead — nếu
        # chỉ so >= cutoff thì chạy lại cho một ngày quá khứ sẽ áp cả cờ của TƯƠNG LAI
        # (vd rerun 2025-12: cờ PNJ 07/2026 vẫn "active").
        lo, hi = str(d - timedelta(days=ttl_days)), str(d)
        return {t for t, f in flags.items() if lo <= str(f.get("last_alert", "")) <= hi}
    except Exception as ex:
        if not quiet:
            print(f"  WARNING: due-diligence flags không đọc được ({ex}) — chạy KHÔNG có gate")
        return set()
