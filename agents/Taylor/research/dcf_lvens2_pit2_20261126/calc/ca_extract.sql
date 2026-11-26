-- Extract corporate_action cho lvens2 pit2. Chạy qua calc/make_ca_extract.py (điền {snapshot_date}). Nguồn = vintage append-only
-- tav2_mike.corporate_action_snapshots (CANONICAL) nên chạy lại cùng snapshot_date cho đúng byte cũ. Cột và thứ tự dòng KHÔNG đổi (md5 phụ thuộc).
SELECT ticker, event_code, exright_date, public_date, effective_date, event_status, value_per_share, exercise_ratio, issue_method_name_vi,
       shares_delta, shares_total_after, CAST(ingested_at AS STRING) AS ingested_at, id
FROM tav2_mike.corporate_action_snapshots
WHERE snapshot_date = DATE '{snapshot_date}' AND event_code IN ('AIS', 'DIV', 'ISS')
ORDER BY ticker, exright_date, id
