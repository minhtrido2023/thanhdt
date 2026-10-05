"""Guard cho custom30_history.py: bộ ba (TABLE, CSV, BASKET_SELECT) phải nhất quán.

Sự cố 2026-09-30 23:36 ICT: data/custom30v_8l_publish.csv (CSV rổ park PRODUCTION) bị ghi đè bằng
nội dung blend vì custom30_history.py chạy với CUSTOM30_CSV=custom30v_* nhưng BASKET_SELECT!=yieldcombo
(arch-review coord-2026-10-01). Quy ước duy nhất đúng (papertrade_daily.sh [6]/[6b]):
  custom30V : BASKET_SELECT=yieldcombo + TABLE chứa 'custom30v' + CSV chứa 'custom30v'
  blend     : BASKET_SELECT!=yieldcombo + TABLE/CSV KHÔNG chứa 'custom30v'
Lệch ⇒ từ chối chạy (fail-closed) TRƯỚC khi chạm BQ/ghi file.
"""
import os


def inconsistencies(table, csv, select):
    v_tab = "custom30v" in str(table).lower()
    v_csv = "custom30v" in str(csv).lower()
    v_sel = str(select).lower() == "yieldcombo"   # CHỈ .lower(), y hệt custom_basket.py:794 (strip ⇒ lệch consumer)
    if v_tab == v_csv == v_sel:
        return []
    return [f"TABLE={table!r} (custom30V={v_tab}), CSV={csv!r} (custom30V={v_csv}), "
            f"BASKET_SELECT={select!r} (yieldcombo={v_sel}) — ba biến phải CÙNG là custom30V hoặc CÙNG là blend"]


def enforce(environ=None):
    e = os.environ if environ is None else environ
    probs = inconsistencies(e.get("CUSTOM30_TABLE", "lithe-record-440915-m9:tav2_bq.custom30_8l"),
                            e.get("CUSTOM30_CSV", "custom30_8l_publish.csv"),
                            e.get("BASKET_SELECT", "blend"))
    if probs:
        raise SystemExit("custom30_history TỪ CHỐI CHẠY — env không nhất quán, sẽ ghi đè CSV/bảng sai:\n  "
                         + "\n  ".join(probs))
