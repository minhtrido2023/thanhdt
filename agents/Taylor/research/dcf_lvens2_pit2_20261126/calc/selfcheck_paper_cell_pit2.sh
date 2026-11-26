#!/usr/bin/env bash
# selfcheck sổ paper_cell_monthly_pit2.py + extract/wrapper (vòng 3). T1–T8 append-only/idempotent/đổi biến thể/sai file/sửa khối cũ; T9* cổng ĐỒNG BỘ cache;
# T10–T13 extract CA là dữ liệu (md5); T14* cổng chạy trễ; T15 cột ca_ratio + bản sao đầu vào; T16* wrapper run_monthly_pit2.sh trong repo git tạm.
# Cần parquet dựng bằng script HIỆN TẠI: F=out/r3_final (lvens2_pit2.py --mc-pit all cho 2026-07..10). Giờ giả PCM_NOW_ICT chỉ dùng được vì sổ test không mang tên sổ chính.
# Dùng: bash calc/selfcheck_paper_cell_pit2.sh [OUT_DIR]. rc = số ca sai.
set -u
cd "$(dirname "$0")/.." || exit 99
BASE=$PWD
export LVENS2_CA=$BASE/out/ca/ca_extract_202611.csv LVENS2_CA_MD5=${LVENS2_CA_MD5:-28418e9d4d91abfa8965ac756bb3d9c4}
export LVENS2_FROZEN=${LVENS2_FROZEN:-/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs/out} PYTHONHASHSEED=0
PY=${PY:-/home/trido/thanhdt/wc_venv/bin/python}; O=${1:-out/sc_ledger}; L=$O/led.csv; F=${F:-out/r3_final}; WC=/home/trido/thanhdt/WorkingClaude
rm -rf "$O"; mkdir -p "$O"; bad=0
declare -A NOW=([07]=2026-08-03T08:05 [08]=2026-09-01T08:05 [09]=2026-10-01T08:05 [10]=2026-11-02T08:05)
# run <mm> <args...>: ghi/kiểm sổ $L với giờ giả = lượt chạy đầu tháng sau
run() { local mm=$1; shift; PCM_NOW_ICT=${NOW[$mm]} "$PY" calc/paper_cell_monthly_pit2.py --ledger "$L" --asof-ym "2026-$mm" "$@" >"$O/last.txt" 2>&1; echo $?; }
pq() { echo "$F/lvens2_2026-$1_mc${2:-stepcar}.parquet"; }
chk() { local name=$1 want=$2 got=$3; if [ "$got" = "$want" ]; then echo "$name | PASS | rc=$got"; else echo "$name | FAIL | rc=$got want=$want"; tail -3 "$O/last.txt"; bad=$((bad+1)); fi; }
has() { if grep -q -- "$2" "$O/last.txt"; then echo "$1 | PASS | lý do khớp"; else echo "$1 | FAIL | không thấy '$2'"; tail -3 "$O/last.txt"; bad=$((bad+1)); fi; }
ok() { if eval "$2"; then echo "$1 | PASS"; else echo "$1 | FAIL"; bad=$((bad+1)); fi; }
chk "T1 ghi 2026-09" 0 "$(run 09 --lvens2-from "$(pq 09)")"
chk "T2 ghi 2026-10" 0 "$(run 10 --lvens2-from "$(pq 10)")"
chk "T3 chạy lại 2026-10 (SKIP idempotent)" 0 "$(run 10 --lvens2-from "$(pq 10)")"; has T3b SKIP
chk "T4 đổi biến thể giữa chừng (stepca)" 3 "$(run 08 --lvens2-from "$(pq 08 stepca)" --expect-mc stepca)"; has T4b "đổi biến thể"
chk "T5 file sai biến thể so với expect" 3 "$(run 08 --lvens2-from "$(pq 08 stepca)")"
chk "T6 file sai tháng" 3 "$(run 08 --lvens2-from "$(pq 07)")"
cp "$L" "$O/led.bak"; pre=$(md5sum < "$L"); sz=$(stat -c %s "$L")
sed -i '2s/RE_DUOC_THUA_NHAN\|RE_CHUA_THUA_NHAN\|DAT_CON_NEO\|DAT_DANG_NGUOI/XX/' "$L"
chk "T7 sửa 1 dòng cũ rồi ghi" 3 "$(run 08 --lvens2-from "$(pq 08)")"; has T7b "đã bị sửa"
cp "$O/led.bak" "$L"
chk "T8 khôi phục rồi ghi 2026-08" 0 "$(run 08 --lvens2-from "$(pq 08)")"
ok "T8b prefix byte cũ giữ nguyên" '[ "$(head -c "$sz" "$L" | md5sum)" = "$pre" ]'

# ---- T9: cổng ĐỒNG BỘ trên cây cache giả (symlink), từng marker một ----
mkfake() { rm -rf "$O/fakewc"; FK=$O/fakewc/data/bq_cache; mkdir -p "$FK"
  for d in "$WC"/data/bq_cache/*; do ln -s "$d" "$FK/$(basename "$d")"; done; rm "$FK/manifest.json"; cp -p "$WC/data/bq_cache/manifest.json" "$FK/manifest.json"; }
old_copy() { rm "$FK/$1"; cp "$WC/data/bq_cache/$1" "$FK/$1"; TZ=Asia/Ho_Chi_Minh touch -d "$2" "$FK/$1"; }
mani() { "$PY" -c "import json,sys;p=sys.argv[1];m=json.load(open(p));exec(sys.argv[2]);json.dump(m,open(p,'w'))" "$FK/manifest.json" "$1"; }
fk() { WC_ROOT=$O/fakewc PCM_NOW_ICT=${NOW[10]} "$PY" calc/paper_cell_monthly_pit2.py --asof-ym 2026-10 --ledger "$O/led9.csv" --lvens2-from "$(pq 10)" >"$O/last.txt" 2>&1; echo $?; }
mkfake; old_copy ticker_financial.parquet "2026-10-30 23:14"; chk "T9a ticker_financial sync 23:14 ngày cuối tháng (< T 23:15)" 3 "$(fk)"; has T9a2 "ticker_financial.mtime"
mkfake; old_copy ticker_financial.parquet "2026-10-30 23:16"; chk "T9b ticker_financial sync 23:16 (>= T) ⇒ ghi được" 0 "$(fk)"; rm -f "$O"/led9.csv*
mkfake; old_copy fa_ratings_8l.parquet "2026-10-29 23:50"; chk "T9c fa_ratings_8l sync thiếu đêm cuối tháng" 3 "$(fk)"; has T9c2 "fa_ratings_8l.mtime"
mkfake; mani "m['verified']=False"; chk "T9d manifest verified=false" 3 "$(fk)"; has T9d2 "verified=False"
mkfake; mani "m['tables']['ticker']['max_time']='2026-10-29'"; chk "T9e ticker max_time < D" 3 "$(fk)"; has T9e2 "ticker.max_time"
mkfake; mani "m['verified_at_epoch']=1793300000"; chk "T9f verified_at trước T" 3 "$(fk)"; has T9f2 "verified_at"
mkfake; rm "$FK/universe_pit"; mkdir "$FK/universe_pit"; cp "$WC/data/bq_cache/universe_pit/2026.parquet" "$FK/universe_pit/"; TZ=Asia/Ho_Chi_Minh touch -d "2026-10-29 23:50" "$FK/universe_pit/2026.parquet"
chk "T9g universe_pit chưa sync đêm cuối tháng" 3 "$(fk)"; has T9g2 "universe_pit.mtime"
mkfake; old_copy ticker_financial.parquet "2026-10-29 23:50"
chk "T9h lvens2 DỰNG trên cache chưa sync" 3 "$("$PY" calc/lvens2_pit2.py --asof-ym 2026-10 --mc-pit stepcar --out-dir "$O/stale" --cache-root "$FK" >"$O/last.txt" 2>&1; echo $?)"; has T9h2 "chưa đồng bộ"
ok "T9i không sinh parquet khi fail" '! ls "$O"/stale/*.parquet >/dev/null 2>&1'
cp "$(pq 10)" "$O/nofresh.parquet"; "$PY" -c "import json,sys;m=json.load(open(sys.argv[1]));m['freshness']={'ticker_financial':'2026-10-30'};json.dump(m,open(sys.argv[2],'w'))" "$F/lvens2_2026-10_mcstepcar.json" "$O/nofresh.json"
chk "T9j parquet dựng bởi cổng cũ (không sync-v2)" 3 "$(run 07 --lvens2-from "$O/nofresh.parquet")"

# ---- T10–T13 (B1): extract CA là DỮ LIỆU ----
CA2=$O/ca_extract_new.csv; cp out/ca/ca_extract_202611.csv "$CA2"; echo >> "$CA2"; M2=$(md5sum < "$CA2" | cut -d' ' -f1)
lv() { "$PY" calc/lvens2_pit2.py --asof-ym 2026-07 --mc-pit stepcar --out-dir "$O/new" >"$O/last.txt" 2>&1; echo $?; }
chk "T10a dựng lvens2 với extract MỚI (md5 mới)" 0 "$(LVENS2_CA=$CA2 LVENS2_CA_MD5=$M2 lv)"
ok "T10b script_md5 sidecar = md5 file script" '[ "$(md5sum < calc/lvens2_pit2.py | cut -d" " -f1)" = "$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1]))[\"script_md5\"])" "$O/new/lvens2_2026-07_mcstepcar.json")" ]'
chk "T13 sổ dùng extract KHÁC extract đã dựng lvens2" 3 "$(run 07 --lvens2-from "$O/new/lvens2_2026-07_mcstepcar.parquet")"; has T13b "extract CA"
chk "T10c sổ đã có khối ca_md5 cũ, ghi khối extract mới" 0 "$(LVENS2_CA=$CA2 LVENS2_CA_MD5=$M2 run 07 --lvens2-from "$O/new/lvens2_2026-07_mcstepcar.parquet")"
ok "T10d sổ chứa 2 ca_md5 khác nhau" '[ "$("$PY" -c "import pandas as pd,sys;print(pd.read_csv(sys.argv[1]).ca_md5.nunique())" "$L")" = 2 ]'
chk "T11 extract md5 SAI" 3 "$(LVENS2_CA=$CA2 LVENS2_CA_MD5=0123456789abcdef0123456789abcdef lv)"
chk "T12 thiếu LVENS2_CA_MD5" 3 "$(LVENS2_CA=$CA2 LVENS2_CA_MD5='' lv)"

# ---- T14: cổng chạy trễ (cuối tháng 2026-10 = 10-31) ----
late() { PCM_NOW_ICT=$1 "$PY" calc/paper_cell_monthly_pit2.py --asof-ym 2026-10 --ledger "$O/late_$2.csv" --lvens2-from "$(pq 10)" >"$O/last.txt" 2>&1; echo $?; }
chk "T14a +5 ngày (11-05 23:59) ⇒ ghi" 0 "$(late 2026-11-05T23:59 a)"
chk "T14b +6 ngày (11-06 00:01) ⇒ chặn" 3 "$(late 2026-11-06T00:01 b)"; has T14b2 "chỉ ghi khi"
chk "T14c trong tháng as-of (10-31) ⇒ chặn" 3 "$(late 2026-10-31T08:05 c)"
chk "T14d giờ thật (không env), as-of 2026-09 ⇒ chặn" 3 "$("$PY" calc/paper_cell_monthly_pit2.py --asof-ym 2026-09 --ledger "$O/late_d.csv" --lvens2-from "$(pq 09)" >"$O/last.txt" 2>&1; echo $?)"; has T14d2 "chỉ ghi khi"
chk "T14e giờ giả với tên sổ chính ⇒ chặn" 3 "$(PCM_NOW_ICT=${NOW[10]} "$PY" calc/paper_cell_monthly_pit2.py --asof-ym 2026-10 --ledger "$O/paper_cell_ledger_pit2.csv" --lvens2-from "$(pq 10)" >"$O/last.txt" 2>&1; echo $?)"; has T14e2 "không được dùng với sổ chính"
ok "T14f ca bị chặn không tạo file sổ" '[ ! -e "$O/late_b.csv" ] && [ ! -e "$O/late_c.csv" ] && [ ! -e "$O/paper_cell_ledger_pit2.csv" ]'
ok "T14g computed_at_ict là giờ thật, không phải giờ giả" '"$PY" -c "import pandas as pd,sys,datetime as d,zoneinfo as z;x=pd.read_csv(sys.argv[1]).computed_at_ict.iloc[0];sys.exit(0 if x[:10]==d.datetime.now(z.ZoneInfo(\"Asia/Ho_Chi_Minh\")).strftime(\"%Y-%m-%d\") else 1)" "$O/late_a.csv"'

# ---- T15: cột mới + bản sao đầu vào ----
ok "T15a ca_ratio_stepcar/stepca có mặt, >= 1, stepcar >= stepca" '"$PY" -c "import pandas as pd,sys;d=pd.read_csv(sys.argv[1]);sys.exit(0 if (d.ca_ratio_stepca>=1).all() and (d.ca_ratio_stepcar>=d.ca_ratio_stepca-1e-12).all() and (d.ca_ratio_stepcar>1).any() else 1)" "$L"'
ok "T15b mỗi tháng trong sổ có bản sao parquet đúng md5" '"$PY" -c "import pandas as pd,sys,hashlib,os;d=pd.read_csv(sys.argv[1]);k=os.path.join(os.path.dirname(sys.argv[1]),\"ledger_inputs\");sys.exit(0 if all(hashlib.md5(open(f\"{k}/lvens2_{y}_{m[:8]}.parquet\",\"rb\").read()).hexdigest()==m for y,m in set(zip(d.asof_ym,d.lvens2_md5))) else 1)" "$L"'

# ---- T16: wrapper trong repo git tạm (không đụng repo thật) ----
R=$(mktemp -d /tmp/lv2wrap.XXXXXX); mkdir -p "$R/out/ca"; cp -r calc "$R/calc"; cp out/ca/ca_extract_202611.csv* "$R/out/ca/"
git -C "$R" init -q; git -C "$R" config user.email sc@localhost; git -C "$R" config user.name selfcheck
printf '#!/usr/bin/env bash\nprintf "%%s\\n" "$1" >> "%s/alerts.txt"\n' "$R" > "$R/alert.sh"; chmod +x "$R/alert.sh"
wrap() { env -u LVENS2_CA -u LVENS2_CA_MD5 ALERT_CMD="${AC-$R/alert.sh}" PCM_LEDGER=out/test_ledger.csv ASOF_YM=2026-10 CA_YM=202611 PCM_NOW_ICT=${NOW[10]} bash "$R/calc/run_monthly_pit2.sh" >"$BASE/$O/last.txt" 2>&1; echo $?; }
chk "T16a wrapper end-to-end ghi + commit" 0 "$(wrap)"; has T16a2 "ĐÃ COMMIT"
ok "T16b sổ + sidecar + inputs + extract đã vào git, cây sạch cho các file đó" '[ "$(git -C "$R" ls-files | grep -cE "test_ledger.csv|ledger_inputs/|ca_extract_202611.csv")" -ge 5 ] && git -C "$R" diff --quiet HEAD -- out'
m1=$(md5sum < "$R/out/monthly/lvens2_2026-10_mcstepcar.parquet"); t1=$(stat -c %y "$R/out/monthly/lvens2_2026-10_mcstepcar.parquet")
ok "T17a lượt thành công không cảnh báo" '[ ! -e "$R/alerts.txt" ]'
chk "T16c chạy lại ⇒ SKIP, không dựng lại" 0 "$(wrap)"; has T16c2 SKIP
ok "T16d parquet không bị ghi đè" '[ "$(stat -c %y "$R/out/monthly/lvens2_2026-10_mcstepcar.parquet")" = "$t1" ] && [ "$(md5sum < "$R/out/monthly/lvens2_2026-10_mcstepcar.parquet")" = "$m1" ]'
sed -i '2s/2026-10/2026-1O/' "$R/out/test_ledger.csv"; "$PY" - "$R/out/test_ledger.csv" <<'PY'
import sys, hashlib, json
p = sys.argv[1]; lines = open(p).read().splitlines(keepends=True)      # kẻ sửa lén: sửa sổ RỒI vá luôn md5 trong sidecar
lines[1] = lines[1].replace("2026-1O", "2026-10", 1).replace(",stepcar,", ",stepcar ,", 1); open(p, "w").write("".join(lines))
s = json.loads(open(p + ".blocks.jsonl").readline()); s["block_md5"] = hashlib.md5("".join(lines[1:]).encode()).hexdigest()
open(p + ".blocks.jsonl", "w").write(json.dumps(s) + "\n")
PY
chk "T16e sửa lén sổ + sidecar ⇒ git chặn" 3 "$(wrap)"; has T16e2 "khác bản đã commit"
ok "T17b lỗi ⇒ đúng 1 cảnh báo, có rc và dòng lỗi thật" '[ "$(grep -c "LỖI rc=3" "$R/alerts.txt")" = 1 ] && grep -q "khác bản đã commit" "$R/alerts.txt"'
chk "T17c lượt thử không khai ALERT_CMD: giữ rc, không gửi thật" 3 "$(AC='' wrap)"; has T17c2 ALERT_SKIPPED
printf '#!/usr/bin/env bash\nexit 1\n' > "$R/alert_bad.sh"; chmod +x "$R/alert_bad.sh"
chk "T17d lệnh cảnh báo hỏng không đổi rc" 3 "$(AC=$R/alert_bad.sh wrap)"; has T17d2 ALERT_FAILED
rm -rf "$R"
echo "TZ=${TZ-<unset>} RESULT: $([ $bad = 0 ] && echo PASS || echo "FAIL $bad")"; exit $bad
