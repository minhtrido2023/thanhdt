#!/usr/bin/env bash
# code_quality_weekly_scope_selfcheck.sh — scope code_quality_weekly.sh lấy từ production manifest.
#
# Việc J review ARIA (job Wags_20260913_075550). Sandbox hoàn toàn: repo WorkingClaude giả + repo
# mike lồng giả, commit lùi ngày thật (git log thật, không mock), manifest giả, generator `--check` giả
# + crontab giả điều khiển bằng file. Không chạm repo/log/bus thật.
#   H* = bin/code_quality_scope.py trực tiếp: đúng tầng, cửa sổ 7 ngày, trần + ưu tiên T0,
#        T3/T? bị loại, manifest/git hỏng ⇒ exit 3.
#   E* = bản sao code_quality_weekly.sh --dry-run: --check khớp ⇒ nguồn manifest; lệch/crontab lỗi/HEAD
#        thiếu/HEAD hỏng ⇒ WARN + fallback danh sách cũ (có hot-core); scope rỗng hợp lệ; dry-run không ghi bus.
# Tự chứng minh harness còn sống (bài học 2026-08-29): bản sao phải trùng byte bản thật, generator
# giả phải thật sự được gọi, và nới cửa sổ thì file cũ PHẢI xuất hiện (ca cửa sổ không rỗng suông).
# shellcheck disable=SC2015  # mẫu `cond && ok || bad`: ok() chỉ echo, luôn trả 0
set -uo pipefail
MIKE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT
WC="$SB/WC"; M="$WC/mike"
fail=0
ok()  { echo "PASS $1"; }
bad() { echo "FAIL $1"; fail=1; }

g() { git -C "$1" -c user.name=sc -c user.email=sc@local "${@:2}" >/dev/null; }
commit_at() {  # commit_at <repo> <ngày-lùi> <msg>
  local d; d="$(date -u -d "$2 days ago" +%Y-%m-%dT%H:%M:%SZ)"
  GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d" g "$1" commit -q -m "$3"
}

# --- dựng sandbox ---
mkdir -p "$WC/trading_bot" "$M/bin" "$M/kb" "$M/logs"
git init -q "$WC"; git init -q "$M"
echo "mike/" >"$WC/.gitignore"
echo x >"$WC/old_t0.py"
g "$WC" add -A; commit_at "$WC" 10 old
for f in a_t0.py z_t0.py b_t1.py c_t2.sh d_selfcheck.py e_unk.py research_x.py; do echo x >"$WC/$f"; done
g "$WC" add -A; commit_at "$WC" 1 recent

cp "$MIKE/bin/code_quality_weekly.sh" "$MIKE/bin/code_quality_scope.py" "$M/bin/"
# generator giả chỉ đóng vai `--check` (khớp=0 / lệch=1) + crontab giả trên PATH (ca skip = không
# đọc được crontab), cả hai điều khiển bằng $M/sc_mode
cat >"$M/bin/production_manifest.py" <<'EOF'
import os, sys
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
open(os.path.join(d, "sc_calls"), "a").write("called %s\n" % " ".join(sys.argv[1:]))
if open(os.path.join(d, "sc_mode")).read().strip() == "fail":
    print("DRIFT 1 dòng — manifest commit lệch thực tế."); print("+ x.py [T0]"); sys.exit(1)
EOF
mkdir -p "$SB/fakebin"
# shellcheck disable=SC2016  # $(…) phải nằm nguyên văn trong script giả, chỉ %s được thay
printf '#!/usr/bin/env bash\n[ "$(cat "%s/sc_mode")" = skip ] && exit 1\necho "0 3 * * 0 x"\n' "$M" >"$SB/fakebin/crontab"
chmod +x "$SB/fakebin/crontab"
printf '#!/usr/bin/env bash\necho "$*" >>"%s/bus_calls"\n' "$M" >"$M/bin/append_event.sh"
chmod +x "$M/bin/"*.sh
cat >"$M/kb/production_manifest.json" <<'EOF'
{"files": {"a_t0.py": {"tier": "T0"}, "z_t0.py": {"tier": "T0"}, "old_t0.py": {"tier": "T0"},
 "b_t1.py": {"tier": "T1"}, "c_t2.sh": {"tier": "T2"}, "d_selfcheck.py": {"tier": "T3"},
 "e_unk.py": {"tier": "T?"}, "mike/bin/g_t0.sh": {"tier": "T0"}, "missing_t0.py": {"tier": "T0"}}}
EOF
g "$M" add -A; commit_at "$M" 10 base
echo x >"$M/bin/g_t0.sh"; g "$M" add -A; commit_at "$M" 1 recent

cmp -s "$M/bin/code_quality_weekly.sh" "$MIKE/bin/code_quality_weekly.sh" \
  && cmp -s "$M/bin/code_quality_scope.py" "$MIKE/bin/code_quality_scope.py" \
  || bad "harness: bản sao sandbox lệch bản thật"

scope() {  # scope <max> <since> [manifest] [repo2] — stdout = scope, $SB/dropped, rc
  python3 "$M/bin/code_quality_scope.py" --manifest "${3:-$M/kb/production_manifest.json}" \
    --wc-root "$WC" --repo "$WC" --repo "${4:-$M}" --since "$2" --max-files "$1" \
    --dropped-out "$SB/dropped" 2>"$SB/scope.err"
}
rel() { sed "s|^$WC/||" | paste -sd' ' -; }

# H1 đúng tầng + cửa sổ: T0 trước (theo path), rồi T1, T2; loại T3, T?, ngoài manifest, cũ >7 ngày,
# file manifest không tồn tại.
got="$(scope 25 "7 days ago" | rel)"
want="a_t0.py mike/bin/g_t0.sh z_t0.py b_t1.py c_t2.sh"
[ "$got" = "$want" ] && ok "H1 tầng/thứ tự/loại T3-T?-R&D/cửa sổ: $got" || bad "H1 được '$got' mong '$want'"
grep -q "loại 2 file T3/T?" "$SB/scope.err" && ok "H1b tóm tắt đếm T3/T? bị loại" || bad "H1b stderr: $(cat "$SB/scope.err")"

# H2 harness sống: nới cửa sổ 30 ngày ⇒ old_t0.py PHẢI vào (ca cửa sổ ở H1 không rỗng suông)
got="$(scope 25 "30 days ago" | rel)"
case " $got " in *" old_t0.py "*) ok "H2 cửa sổ 30 ngày thấy old_t0.py (commit 10 ngày trước)";;
  *) bad "H2 nới cửa sổ vẫn không thấy old_t0.py: '$got' — git log/commit lùi ngày hỏng";; esac

# H3 trần 3: giữ 3 file T0 (z_t0 thắng b_t1 dù path sau) — T1/T2 bị rớt, ghi vào dropped
got="$(scope 3 "7 days ago" | rel)"; dr="$(rel <"$SB/dropped")"
[ "$got" = "a_t0.py mike/bin/g_t0.sh z_t0.py" ] && [ "$dr" = "b_t1.py c_t2.sh" ] \
  && ok "H3 trần 3 ưu tiên T0, rớt: $dr" || bad "H3 giữ '$got' rớt '$dr'"

# H4 manifest hỏng ⇒ exit 3
scope 25 "7 days ago" "$SB/khong_co.json" >/dev/null; r1=$?
echo '{"files": {' >"$SB/broken.json"; scope 25 "7 days ago" "$SB/broken.json" >/dev/null; r2=$?
echo '{"files": {"d_selfcheck.py": {"tier": "T3"}}}' >"$SB/t3only.json"; scope 25 "7 days ago" "$SB/t3only.json" >/dev/null; r3=$?
[ "$r1$r2$r3" = "333" ] && ok "H4 manifest thiếu/JSON hỏng/chỉ T3 ⇒ exit 3" || bad "H4 rc thiếu=$r1 hỏng=$r2 chỉT3=$r3"

# H5 git hỏng (repo không phải git) ⇒ exit 3, không trả scope thiếu im lặng
mkdir -p "$SB/notgit"; scope 25 "7 days ago" "" "$SB/notgit" >/dev/null; r=$?
[ "$r" = 3 ] && ok "H5 git log lỗi ⇒ exit 3" || bad "H5 rc=$r"

# --- E*: bản sao script thật, --dry-run, env -u TZ (§16) ---
run() {  # run <sc_mode> — stdout script; $SB/out
  echo "$1" >"$M/sc_mode"
  env -u TZ PATH="$SB/fakebin:$PATH" bash "$M/bin/code_quality_weekly.sh" --dry-run >"$SB/out" 2>&1
  awk '/^=== SCOPE/{f=1;next} /^=== PROMPT/{f=0} f' "$SB/out" | rel
}
: >"$M/sc_calls"
got="$(run pass)"
if [ "$got" = "a_t0.py mike/bin/g_t0.sh z_t0.py b_t1.py c_t2.sh" ] && grep -q "Nguồn scope: MANIFEST" "$SB/out" \
   && ! grep -q "WARN: nguồn scope" "$SB/out"; then ok "E1 manifest HEAD khớp ⇒ scope manifest"
else bad "E1 scope '$got'"; tail -5 "$SB/out"; fi
grep -Eq '^called --crontab .* --check .*production_manifest\.json$' "$M/sc_calls" && [ "$(grep -c . "$M/sc_calls")" = 1 ] \
  && ok "E1b generator --check (crontab + HEAD manifest) thật sự được gọi" || bad "E1b generator giả: $(cat "$M/sc_calls")"

# E1c manifest working-copy lệch HEAD (chưa commit thêm research_x.py T0) ⇒ vẫn đọc bản HEAD
python3 - "$M/kb/production_manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1])); m["files"]["research_x.py"] = {"tier": "T0"}; json.dump(m, open(sys.argv[1], "w"))
PY
got="$(run pass)"
[ "$got" = "a_t0.py mike/bin/g_t0.sh z_t0.py b_t1.py c_t2.sh" ] && ok "E1c đọc manifest HEAD, bỏ qua working-copy chưa commit" \
  || bad "E1c scope '$got' (đọc nhầm working-copy?)"
g "$M" checkout -- kb/production_manifest.json

for mode in fail skip; do
  got="$(run "$mode")"
  # fallback = danh sách cũ: có hot-core round-robin (trading_bot/plan.py, idx 0) + file R&D ngoài manifest
  why="không đọc được crontab -l"; [ "$mode" = fail ] && why="manifest HEAD lệch thực tế.*DRIFT 1 dòng"
  if [[ " $got " == *" trading_bot/plan.py "* && " $got " == *" research_x.py "* ]]; then
    grep -q "WARN: nguồn scope = FALLBACK.*$why" "$SB/out" \
      && ok "E2-$mode $mode ⇒ WARN + fallback (hot-core + diff cũ)" || bad "E2-$mode thiếu WARN nêu nguồn"
  else bad "E2-$mode không fallback: '$got'"; fi
done

# E5 manifest hợp lệ nhưng tuần không có commit T0-T2 ⇒ scope rỗng hợp lệ: dry-run không ghi bus,
# chạy thật ghi status với note đúng nguồn (thoát trước khi gọi claude)
echo '{"files": {"old_t0.py": {"tier": "T0"}}}' >"$M/kb/production_manifest.json"; g "$M" add -A; commit_at "$M" 0 quiet
run pass >/dev/null
if grep -q "0 file trong scope (nguồn manifest" "$SB/out" && [ ! -s "$M/bus_calls" ]; then
  env -u TZ PATH="$SB/fakebin:$PATH" bash "$M/bin/code_quality_weekly.sh" >"$SB/out" 2>&1
  grep -q "không có file T0-T2 nào có commit" "$M/bus_calls" 2>/dev/null \
    && ok "E5 scope manifest rỗng: dry-run im bus, chạy thật ghi status đúng nguồn" || bad "E5 chạy thật bus_calls: $(cat "$M/bus_calls" 2>/dev/null)"
else bad "E5 dry-run scope rỗng: $(grep -m1 'Scope\|0 file' "$SB/out") bus=$(cat "$M/bus_calls" 2>/dev/null)"; fi
: >"$M/bus_calls"

echo '{"files": ' >"$M/kb/production_manifest.json"; g "$M" add -A; commit_at "$M" 0 broken
run pass >/dev/null
grep -q "WARN: nguồn scope = FALLBACK.*code_quality_scope.py lỗi" "$SB/out" \
  && ok "E3 HEAD manifest hỏng ⇒ WARN + fallback" || bad "E3: $(grep -m1 'scope' "$SB/out")"
g "$M" rm -q kb/production_manifest.json; commit_at "$M" 0 rm
run pass >/dev/null
grep -q "WARN: nguồn scope = FALLBACK.*không đọc được HEAD:kb/production_manifest.json" "$SB/out" \
  && ok "E4 HEAD thiếu manifest ⇒ WARN + fallback" || bad "E4: $(grep -m1 'scope' "$SB/out")"

[ ! -s "$M/bus_calls" ] && ok "E6 các lượt dry-run E3/E4 không ghi bus" || bad "E6 dry-run gọi append_event: $(cat "$M/bus_calls")"

[ "$fail" -eq 0 ] && echo "PASS code_quality_weekly_scope_selfcheck" || echo "FAIL code_quality_weekly_scope_selfcheck"
exit "$fail"
