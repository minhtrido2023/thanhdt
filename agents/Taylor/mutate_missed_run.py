#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutation test cho LỚP 7 (phiên bị lỡ + backfill) của corp_action_daily.py.

Mỗi mutation là một bug HỢP LÝ mà một người viết bản này rất dễ viết ra. Nếu bộ selfcheck không
ĐỎ khi mutation được áp, thì ca tương ứng chỉ đang khẳng định suông. Chạy tay, không phải cron.
"""
import os
import shutil
import subprocess
import sys
import tempfile

WC = "/home/trido/thanhdt/WorkingClaude"
SRC = f"{WC}/mike/bin/corp_action_daily.py"

MUTS = [
    ("M-A đếm bằng NGÀY LỊCH thay vì phiên giao dịch",
     "        d = prev_trading_day(dt.date.fromisoformat(asof))\n"
     "        while d > d_prev:\n"
     "            out.add(d.isoformat())\n"
     "            d = prev_trading_day(d)",
     "        d = dt.date.fromisoformat(asof) - dt.timedelta(days=1)\n"
     "        while d > d_prev:\n"
     "            out.add(d.isoformat())\n"
     "            d -= dt.timedelta(days=1)"),

    ("M-B backfill hỏi ngày HÔM NAY thay vì ngày bị lỡ (bug 'gọi đúng hàm, sai tham số')",
     '            events.append({**r, "event_date": d, "backfilled": True})',
     '            events.append({**r, "event_date": days[-1], "backfilled": True})'),

    ("M-C bỏ hàng HOÃN (ngày backfill lỗi/vượt trần mất luôn)",
     '    out |= {d for d in (deferred or []) if d and d < asof}',
     '    out |= set()'),

    ("M-D nạp backfill TRƯỚC hàng treo ⇒ dòng backfill n_checks=0 thắng, reset đồng hồ escalate",
     "    for p in (prev_snap or {}).get(\"pending_confirmations\") or []:\n"
     "        _add(p, p.get(\"event_date\") or prev_asof, p.get(\"first_seen_asof\") or prev_asof,\n"
     "             int(p.get(\"n_checks\") or 0))",
     "    for r in backfilled or []:\n"
     "        _add(r, r.get(\"event_date\") or asof or prev_asof, asof or prev_asof, 0, backfill=True)\n"
     "    for p in (prev_snap or {}).get(\"pending_confirmations\") or []:\n"
     "        _add(p, p.get(\"event_date\") or prev_asof, p.get(\"first_seen_asof\") or prev_asof,\n"
     "             int(p.get(\"n_checks\") or 0))"),

    ("M-E `first_seen_asof` lấy NGÀY SỰ KIỆN ⇒ món backfill cũ hết hạn kiểm ngay lượt đầu",
     "        _add(r, r.get(\"event_date\") or asof or prev_asof, asof or prev_asof, 0, backfill=True)",
     "        _add(r, r.get(\"event_date\") or asof or prev_asof, r.get(\"event_date\"), 0,\n"
     "             backfill=True)"),

    ("M-F bỏ trần ⇒ một lượt chạy bắn ra bao nhiêu truy vấn cũng được",
     "    over = days[:-max_days] if max_days and len(days) > max_days else []",
     "    over = []"),

    ("M-G lỗi truy vấn ném thẳng ra ngoài ⇒ mất luôn snapshot hôm nay vì một ngày quá khứ",
     "        except Exception as exc:                                    # noqa: BLE001\n"
     "            errors.append({\"date\": d, \"error\": f\"{type(exc).__name__}: {exc}\"})\n"
     "            deferred.append(d)\n"
     "            continue",
     "        except Exception:                                           # noqa: BLE001\n"
     "            raise"),

    ("M-H bỏ nhãn `backfilled` khỏi PENDING_FIELDS ⇒ carry-forward đánh mất nguồn gốc món treo",
     '                  "event_title_vi", "status_then", "event_date", "first_seen_asof", "n_checks",\n'
     '                  "backfilled")',
     '                  "event_title_vi", "status_then", "event_date", "first_seen_asof",\n'
     '                  "n_checks")'),
]


def main():
    orig = open(SRC, encoding="utf-8").read()
    bak = tempfile.mktemp(suffix=".py")
    shutil.copy(SRC, bak)
    rows = []
    try:
        for name, old, new in MUTS:
            if old not in orig:
                rows.append((name, "KHÔNG ÁP ĐƯỢC (mẫu không khớp — mutation này mốc rồi)", ""))
                continue
            with open(SRC, "w", encoding="utf-8") as f:
                f.write(orig.replace(old, new, 1))
            # ⚠️ BẪY THẬT, đã cắn ở chính bộ này (2026-08-13): pyc được coi là còn hợp lệ khi
            # (mtime giây, KÍCH THƯỚC) của nguồn không đổi. Mutation M-A và M-B tình cờ cho file
            # ĐÚNG BẰNG NHAU (78.290 byte) và được ghi trong CÙNG một giây ⇒ lượt M-B nạp lại
            # bytecode của M-A và harness chấm điểm nhầm mutation trước. Dọn cache + tắt hẳn việc
            # ghi pyc; và `inspect.getsource` KHÔNG phát hiện được (nó đọc file nguồn, không phải
            # code đang chạy) nên đừng dùng nó để "xác minh" mutation đã vào.
            shutil.rmtree(f"{WC}/mike/bin/__pycache__", ignore_errors=True)
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            r = subprocess.run([sys.executable, f"{WC}/mike/bin/corp_action_daily_selfcheck.py"],
                               capture_output=True, text=True, cwd=WC, timeout=900, env=env)
            failed = [ln[len("  FAIL  "):].split(".")[0] for ln in (r.stdout or "").splitlines()
                      if ln.startswith("  FAIL  ")]
            crash = "" if failed else f" [CRASH rc={r.returncode}: " \
                                      f"{(r.stderr or '').strip().splitlines()[-1:][0][:90]}]"
            rows.append((name, "GIẾT ĐƯỢC" if r.returncode != 0 else "❌ SỐNG SÓT",
                         ",".join(sorted(set(failed))) + crash))
    finally:
        shutil.copy(bak, SRC)
    print("\n== KẾT QUẢ MUTATION ==")
    for n, verdict, who in rows:
        print(f"  {verdict:12s} {n}\n               ca đỏ: {who}")
    alive = [n for n, v, _ in rows if v != "GIẾT ĐƯỢC"]
    print(f"\n{len(rows) - len(alive)}/{len(rows)} mutation bị giết")
    return 1 if alive else 0


if __name__ == "__main__":
    raise SystemExit(main())
