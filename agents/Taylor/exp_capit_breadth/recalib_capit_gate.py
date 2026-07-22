"""G4/P4 — CAPIT breadth re-hiệu-chuẩn (§4.4 ticker_prune_replacement_plan.md).

Câu hỏi DUY NHẤT: có tồn tại WASHOUT_GATE' trên mẫu số universe_pit_q sao cho tập ngày
fire lịch sử (br_old >= 0.30 trên ticker_prune) KHÔNG ĐỔI? Đây là re-hiệu-chuẩn bảo toàn
hành vi, KHÔNG phải tối ưu lại ngưỡng.

Input: breadth_both.csv, sinh bằng (bq query --use_legacy_sql=false --format=csv):

  WITH o AS (
    SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) br_old, COUNT(*) n_old
    FROM tav2_bq.ticker_prune p
    WHERE p.time >= DATE "2014-01-01" AND p.Close_T1>0 GROUP BY p.time),
  q AS (
    SELECT t.time, AVG(CASE WHEN t.D_RSI<0.3 THEN 1.0 ELSE 0 END) br_new, COUNT(*) n_new
    FROM tav2_bq.ticker t
    JOIN `lithe-record-440915-m9.tav2_mike.universe_pit_q` u
      ON u.ticker=t.ticker AND u.time=t.time AND u.in_universe
    WHERE t.time >= DATE "2014-01-01" AND t.Close_T1>0 GROUP BY t.time)
  SELECT COALESCE(o.time,q.time) time, o.br_old, o.n_old, q.br_new, q.n_new
  FROM o FULL OUTER JOIN q USING(time) ORDER BY 1

Kết luận đã ghi vào §4.4-KQ: KHÔNG tồn tại ngưỡng bảo toàn ⇒ ESCALATED, không cutover.
"""
import os
import numpy as np
import pandas as pd

GATE = 0.30
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, "breadth_both.csv"), parse_dates=["time"]).dropna().reset_index(drop=True)
fire = (d.br_old >= GATE).values

lo, hi = d.br_new[fire].min(), d.br_new[~fire].max()
print(f"ngay fire cu: {fire.sum()} / {len(d)} phien")
print(f"min br_new tren ngay FIRE      = {lo:.6f}")
print(f"max br_new tren ngay KHONG-fire = {hi:.6f}")
print(f"TACH DUOC (ton tai gate' bao toan)? {hi < lo}")

best = min(((g, int(((d.br_new >= g).values != fire).sum())) for g in np.arange(0.10, 0.60, 0.0005)),
           key=lambda x: x[1])
print(f"gate' sai it nhat = {best[0]:.4f} -> {best[1]} ngay lech")


def grind(mask):
    """Mirror golive_recommend_v23.py:511-516 — washout truoc do trong 20-90 phien => size /2."""
    idx = np.where(mask)[0]
    s = set(idx)
    return {d.time[i]: any((i - b) in s for b in range(20, 91)) for i in idx}


old_g = grind(fire)
for g in (0.30, best[0]):
    new_g = grind((d.br_new >= g).values)
    diff = [(k, old_g.get(k, "NOFIRE"), new_g.get(k, "NOFIRE"))
            for k in sorted(set(old_g) | set(new_g)) if old_g.get(k, "NOFIRE") != new_g.get(k, "NOFIRE")]
    print(f"\ngate'={g:.4f}: {len(diff)} su kien doi ket cuc SIZE (grind 0.75<->0.375)")
    for k, a, b in diff:
        print(f"   {k.date()}  cu={a}  moi={b}")
