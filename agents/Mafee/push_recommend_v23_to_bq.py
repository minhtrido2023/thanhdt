"""
push_recommend_v23_to_bq.py  —  Mafee / paper-trading daily push

Đọc output của golive_recommend_v23.py và push lên BigQuery dataset `recommend_v23`.

Sources:
  - $WORKDIR/data/golive_v23_status.json        (status JSON, viết bởi golive_recommend_v23.py)
  - $WORKDIR/deploy_golive_dt5g_v4/out/golive_v23_recommendations_<DATE>.csv
  - $WORKDIR/deploy_golive_dt5g_v4/out/golive_v23_recommendations_<DATE>.md  (fallback for status)

Targets:
  - recommend_v23.recommendations   (partitioned by signal_date)
  - recommend_v23.status            (partitioned by signal_date)

Idempotent: mỗi lần chạy sẽ REPLACE toàn bộ partition của signal_date đó.

Usage:
  python3 push_recommend_v23_to_bq.py [YYYY-MM-DD]        # push 1 ngày
  python3 push_recommend_v23_to_bq.py --backfill           # push tất cả CSV có sẵn
  (không có arg → dùng signal_date trong status JSON hiện tại)
"""

import os, sys, json, datetime
import warnings
warnings.filterwarnings("ignore")

from google.cloud import bigquery
from google.cloud.bigquery import SchemaField, TimePartitioning, TimePartitioningType

# ── config ──────────────────────────────────────────────────────────────────
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
ADC_PATH = "/home/trido/thanhdt/gcloud_dtienthanh/application_default_credentials.json"
PROJECT  = "lithe-record-440915-m9"
DATASET  = "recommend_v23"
LOCATION = "asia-southeast1"

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ADC_PATH)

# ── known status JSON fields (schema order) ─────────────────────────────────
STATUS_KNOWN_FIELDS = [
    "signal_date", "date", "state", "state_name", "source",
    "w_lag_target", "w_lag_current", "alloc_band", "band_breach", "alloc_note",
    "etf_park_frac", "breadth_oversold", "washout_gate",
    "capit_fired", "capit_size", "capit_grind",
    "dd52w", "vn_cooling",
    "n_bal", "n_lag_upcoming", "n_lag_recent", "n_capit_basket",
]

# ── BQ schemas ───────────────────────────────────────────────────────────────
RECOMMENDATIONS_SCHEMA = [
    SchemaField("signal_date",  "DATE",    mode="REQUIRED"),
    SchemaField("book",         "STRING",  mode="REQUIRED"),
    SchemaField("ticker",       "STRING",  mode="REQUIRED"),
    SchemaField("play_type",    "STRING",  mode="NULLABLE"),
    SchemaField("ta",           "FLOAT64", mode="NULLABLE"),
    SchemaField("close",        "FLOAT64", mode="NULLABLE"),
    SchemaField("sector",       "INT64",   mode="NULLABLE"),
    SchemaField("weight_pct",   "FLOAT64", mode="REQUIRED"),
    SchemaField("status",       "STRING",  mode="REQUIRED"),
    SchemaField("extra",        "JSON",    mode="NULLABLE"),
]

STATUS_SCHEMA = [
    SchemaField("signal_date",       "DATE",    mode="REQUIRED"),
    SchemaField("date",              "DATE",    mode="NULLABLE"),
    SchemaField("state",             "INT64",   mode="NULLABLE"),
    SchemaField("state_name",        "STRING",  mode="NULLABLE"),
    SchemaField("source",            "STRING",  mode="NULLABLE"),
    SchemaField("w_lag_target",      "FLOAT64", mode="NULLABLE"),
    SchemaField("w_lag_current",     "FLOAT64", mode="NULLABLE"),
    SchemaField("alloc_band",        "FLOAT64", mode="NULLABLE"),
    SchemaField("band_breach",       "BOOL",    mode="NULLABLE"),
    SchemaField("alloc_note",        "STRING",  mode="NULLABLE"),
    SchemaField("etf_park_frac",     "FLOAT64", mode="NULLABLE"),
    SchemaField("breadth_oversold",  "FLOAT64", mode="NULLABLE"),
    SchemaField("washout_gate",      "FLOAT64", mode="NULLABLE"),
    SchemaField("capit_fired",       "BOOL",    mode="NULLABLE"),
    SchemaField("capit_size",        "FLOAT64", mode="NULLABLE"),
    SchemaField("capit_grind",       "BOOL",    mode="NULLABLE"),
    SchemaField("dd52w",             "FLOAT64", mode="NULLABLE"),
    SchemaField("vn_cooling",        "BOOL",    mode="NULLABLE"),
    SchemaField("n_bal",             "INT64",   mode="NULLABLE"),
    SchemaField("n_lag_upcoming",    "INT64",   mode="NULLABLE"),
    SchemaField("n_lag_recent",      "INT64",   mode="NULLABLE"),
    SchemaField("n_capit_basket",    "INT64",   mode="NULLABLE"),
    SchemaField("extra",             "JSON",    mode="NULLABLE"),
]


def get_client():
    return bigquery.Client(project=PROJECT)


def ensure_dataset(client):
    ds_ref = bigquery.DatasetReference(PROJECT, DATASET)
    try:
        client.get_dataset(ds_ref)
    except Exception:
        ds = bigquery.Dataset(ds_ref)
        ds.location = LOCATION
        ds.description = "Recommend V2.3 daily signal feed (paper-trading)"
        client.create_dataset(ds)
        print(f"  Created dataset {DATASET}")


def ensure_table(client, table_name, schema, cluster_fields=None):
    table_ref = f"{PROJECT}.{DATASET}.{table_name}"
    try:
        client.get_table(table_ref)
    except Exception:
        tbl = bigquery.Table(table_ref, schema=schema)
        tbl.time_partitioning = TimePartitioning(
            type_=TimePartitioningType.DAY,
            field="signal_date",
        )
        if cluster_fields:
            tbl.clustering_fields = cluster_fields
        client.create_table(tbl)
        print(f"  Created table {table_name}")


def replace_partition(client, table_name, rows_json, signal_date_str):
    """Delete existing partition then load new rows (idempotent)."""
    date_nodash = signal_date_str.replace("-", "")
    partition_id = f"{PROJECT}.{DATASET}.{table_name}${date_nodash}"

    # Delete existing partition rows (DML safer than truncate for partitioned tables)
    dml = (
        f"DELETE FROM `{PROJECT}.{DATASET}.{table_name}` "
        f"WHERE signal_date = DATE('{signal_date_str}')"
    )
    client.query(dml).result()

    if not rows_json:
        print(f"  {table_name}: 0 rows (empty signal day — partition cleared)")
        return 0

    schema = RECOMMENDATIONS_SCHEMA if table_name == "recommendations" else STATUS_SCHEMA
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    # target the specific partition via decorator
    job = client.load_table_from_json(rows_json, partition_id, job_config=job_config)
    job.result()
    if job.errors:
        raise RuntimeError(f"Load errors for {table_name}: {job.errors}")
    print(f"  {table_name}: {len(rows_json)} row(s) → partition {signal_date_str}")
    return len(rows_json)


def parse_status_from_md(signal_date_str):
    """Reconstruct a best-effort status row by parsing the MD report for a date."""
    import re, csv
    md_path = os.path.join(
        WORKDIR, "deploy_golive_dt5g_v4", "out",
        f"golive_v23_recommendations_{signal_date_str}.md"
    )
    if not os.path.exists(md_path):
        return None
    text = open(md_path, encoding="utf-8").read()

    row = {"signal_date": signal_date_str, "date": signal_date_str}

    # state + state_name + source
    m = re.search(r'\*\*Market state \(gated\):\*\*\s*(\d+)\s*=\s*\*\*(\w+)\*\*.*\(source:\s*([\w_]+)\)', text)
    if m:
        row["state"] = int(m.group(1))
        row["state_name"] = m.group(2)
        row["source"] = m.group(3)

    # w_lag_target
    m = re.search(r'target\s+\*\*(\d+)%\*\*', text)
    if m:
        row["w_lag_target"] = round(int(m.group(1)) / 100, 4)

    # w_lag_current + alloc_note
    m = re.search(r'current\s+(\d+)%\s+\(as of ([\d-]+)\)', text)
    if m:
        row["w_lag_current"] = round(int(m.group(1)) / 100, 4)
        row["alloc_note"] = f"as of {m.group(2)}"

    # band_breach + alloc_band
    m = re.search(r'±(\d+)pp breached', text)
    if m:
        row["band_breach"] = True
        row["alloc_band"] = round(int(m.group(1)) / 100, 4)
    else:
        row["band_breach"] = False
        m2 = re.search(r'trong band\s+±(\d+)pp', text)
        if m2:
            row["alloc_band"] = round(int(m2.group(1)) / 100, 4)

    # etf_park_frac
    m = re.search(r'park\s+\*\*(\d+)%\*\*\s+cash', text)
    if m:
        row["etf_park_frac"] = round(int(m.group(1)) / 100, 4)

    # breadth_oversold
    m = re.search(r'Oversold breadth.*?:\s+\*\*([\d.]+)%\*\*', text)
    if m:
        row["breadth_oversold"] = round(float(m.group(1)) / 100, 6)

    # capit_fired / capit_size
    row["capit_fired"] = bool(re.search(r'WASHOUT GATE FIRED', text))
    if row["capit_fired"]:
        m = re.search(r'size = \*\*([\d.]+)\*\*', text)
        row["capit_size"] = float(m.group(1)) if m else None
    else:
        row["capit_size"] = 0.0

    # counts from CSV
    csv_path = os.path.join(
        WORKDIR, "deploy_golive_dt5g_v4", "out",
        f"golive_v23_recommendations_{signal_date_str}.csv"
    )
    n_bal = n_lag_up = n_lag_recent = n_capit = 0
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                b = r.get("book", "")
                s = r.get("status", "")
                if b == "BAL":
                    n_bal += 1
                elif b == "LAG" and s.startswith("UPCOMING"):
                    n_lag_up += 1
                elif b == "LAG":
                    n_lag_recent += 1
                elif b == "CAPIT":
                    n_capit += 1
    row["n_bal"] = n_bal
    row["n_lag_upcoming"] = n_lag_up
    row["n_lag_recent"] = n_lag_recent
    row["n_capit_basket"] = n_capit
    row["extra"] = json.dumps({"_status_source": "parsed_from_md"})
    return row


def load_status(signal_date_str):
    path = os.path.join(WORKDIR, "data", "golive_v23_status.json")
    # Use the live JSON only when it matches the requested signal_date
    json_matches = False
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            raw_check = json.load(f)
        if raw_check.get("signal_date") == signal_date_str:
            json_matches = True

    if not json_matches:
        # Fall back to parsing the MD report for this date
        row = parse_status_from_md(signal_date_str)
        if row is None:
            print(f"  WARNING: no status JSON or MD for {signal_date_str} — skipping status push")
            return []
        print(f"  status source: parsed from MD (no status JSON for {signal_date_str})")
        return [row]
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    # Separate known fields from extra
    extra = {k: v for k, v in raw.items() if k not in STATUS_KNOWN_FIELDS}
    row = {}
    for field in STATUS_KNOWN_FIELDS:
        row[field] = raw.get(field)
    row["signal_date"] = signal_date_str
    if extra:
        row["extra"] = json.dumps(extra, ensure_ascii=False)
    else:
        row["extra"] = None

    # Coerce types for BQ JSON serialization
    for f in ["date", "signal_date"]:
        if row.get(f) and not isinstance(row[f], str):
            row[f] = str(row[f])

    return [row]


def load_recommendations(signal_date_str):
    # Find CSV for this date
    csv_path = os.path.join(
        WORKDIR, "deploy_golive_dt5g_v4", "out",
        f"golive_v23_recommendations_{signal_date_str}.csv"
    )
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"recommendations CSV not found: {csv_path}")

    import csv
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            row = {
                "signal_date": signal_date_str,
                "book":       r["book"],
                "ticker":     r["ticker"],
                "play_type":  r.get("play_type") or None,
                "ta":         float(r["ta"]) if r.get("ta") not in (None, "", "None") else None,
                "close":      float(r["close"]) if r.get("close") not in (None, "", "None") else None,
                "sector":     int(float(r["sector"])) if r.get("sector") not in (None, "", "None") else None,
                "weight_pct": float(r["weight_pct"]),
                "status":     r["status"],
                "extra":      None,
            }
            # capture any unknown CSV columns into extra
            known_csv = {"book","ticker","play_type","ta","close","sector","weight_pct","status"}
            xtra = {k: v for k, v in r.items() if k not in known_csv and v not in (None, "")}
            if xtra:
                row["extra"] = json.dumps(xtra, ensure_ascii=False)
            rows.append(row)
    return rows


def push_one_date(client, signal_date_str):
    print(f"  [push] signal_date={signal_date_str}")
    rec_rows    = load_recommendations(signal_date_str)
    status_rows = load_status(signal_date_str)
    replace_partition(client, "recommendations", rec_rows, signal_date_str)
    replace_partition(client, "status", status_rows, signal_date_str)
    return len(rec_rows), len(status_rows)


def backfill_all(client):
    import glob
    pattern = os.path.join(
        WORKDIR, "deploy_golive_dt5g_v4", "out",
        "golive_v23_recommendations_*.csv"
    )
    dates = sorted(
        os.path.basename(p).replace("golive_v23_recommendations_", "").replace(".csv", "")
        for p in glob.glob(pattern)
    )
    print(f"[push_recommend_v23_to_bq] backfill — {len(dates)} date(s): {dates}")
    for d in dates:
        push_one_date(client, d)
    print(f"[push_recommend_v23_to_bq] backfill DONE")


def main():
    client = get_client()

    print("  Ensuring dataset + tables …")
    ensure_dataset(client)
    ensure_table(client, "recommendations", RECOMMENDATIONS_SCHEMA,
                 cluster_fields=["book", "ticker"])
    ensure_table(client, "status", STATUS_SCHEMA)

    if len(sys.argv) > 1 and sys.argv[1] == "--backfill":
        backfill_all(client)
        return

    # Determine signal_date for single-date push
    if len(sys.argv) > 1:
        signal_date_str = sys.argv[1]
    else:
        status_path = os.path.join(WORKDIR, "data", "golive_v23_status.json")
        with open(status_path, encoding="utf-8") as f:
            signal_date_str = json.load(f)["signal_date"]

    print(f"[push_recommend_v23_to_bq] signal_date={signal_date_str}")
    n_rec, n_st = push_one_date(client, signal_date_str)
    print(f"[push_recommend_v23_to_bq] DONE — {signal_date_str} (recs={n_rec}, status={n_st})")
    return signal_date_str, n_rec


if __name__ == "__main__":
    main()
