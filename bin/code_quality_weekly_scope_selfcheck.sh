#!/usr/bin/env bash
# code_quality_weekly_scope_selfcheck.sh — scope code_quality_weekly.sh lấy từ production manifest.
#
# Việc J review ARIA (job Wags_20260913_075550). Sandbox hoàn toàn, dựng ĐÚNG hình dạng thật:
# repo ngoài (toplevel) ⊃ thư mục WC (không phải repo riêng) ⊃ repo mike lồng; commit lùi ngày thật
# (git log thật, không mock), manifest giả, generator `--check` giả + crontab giả + claude giả +
# stub bus/Discord/email. Không chạm repo/log/bus/LLM thật.
#   H* = bin/code_quality_scope.py trực tiếp: đúng tầng, cửa sổ 7 ngày, trần + ưu tiên T0, pin
#        hot-core, T3/T? bị loại, map path WC-là-thư-mục-con, manifest/git hỏng ⇒ exit 3.
#   E* = bản sao code_quality_weekly.sh: --check khớp ⇒ nguồn manifest (+hot-core); lệch (kể cả
#        WARN in trước DRIFT)/crontab lỗi/HEAD thiếu/HEAD hỏng ⇒ WARN + fallback danh sách cũ; scope
#        rỗng hợp lệ; chạy thật nhánh fallback ⇒ dòng Discord gắn cờ FALLBACK (kể cả khi file cuối
#        theo sort đã bị xoá / diff 1 repo toàn file loại trừ); dry-run không ghi bus.
# Tự chứng minh harness còn sống (bài học 2026-08-29): bản sao phải trùng byte bản thật, generator
# giả phải thật sự được gọi, nới cửa sổ thì file cũ PHẢI xuất hiện, claude giả phải được gọi ở ca
# chạy thật (và KHÔNG ở ca scope rỗng).
# shellcheck disable=SC2015  # mẫu `cond && ok || bad`: ok() chỉ echo, luôn trả 0
set -uo pipefail
MIKE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT
OUT="$SB/outer"; WC="$OUT/WC"; M="$WC/mike"; FB="$SB/fakebin"
fail=0
ok()  { echo "PASS $1"; }
bad() { echo "FAIL $1"; fail=1; }

g() { git -C "$1" -c user.name=sc -c user.email=sc@local "${@:2}" >/dev/null; }
commit_at() {  # commit_at <repo> <ngày-lùi> <msg>
  local d; d="$(date -u -d "$2 days ago" +%Y-%m-%dT%H:%M:%SZ)"
  GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d" g "$1" commit -q -m "$3"
}

# --- dựng sandbox: outer (toplevel) / WC (thư mục con) / mike (repo lồng) ---
mkdir -p "$WC/trading_bot" "$M/bin" "$M/kb" "$M/logs" "$M/state" "$FB"
git init -q "$OUT"; git init -q "$M"
echo "WC/mike/" >"$OUT/.gitignore"
echo x >"$WC/old_t0.py"; echo x >"$WC/trading_bot/plan.py"
g "$OUT" add -A; commit_at "$OUT" 10 old
for f in a_t0.py z_t0.py b_t1.py c_t2.sh d_selfcheck.py e_unk.py research_x.py; do echo x >"$WC/$f"; done
echo x >"$OUT/outside_wc.py"   # commit mới NGOÀI WC — không được lọt scope
g "$OUT" add -A; commit_at "$OUT" 1 recent
# file đứng CUỐI theo sort có commit trong cửa sổ nhưng đã bị xoá — ca A arch-review vòng 2: nhánh
# fallback cũ chết im dưới set -e (`[ -f ] && echo` là lệnh cuối vòng). Mọi lượt fallback đi qua ca này.
echo x >"$WC/zzz_gone.py"; g "$OUT" add -A; commit_at "$OUT" 1 gone-add
g "$OUT" rm -q WC/zzz_gone.py; commit_at "$OUT" 1 gone-rm

cp "$MIKE/bin/code_quality_weekly.sh" "$MIKE/bin/code_quality_scope.py" "$M/bin/"
# generator giả chỉ đóng vai `--check`, điều khiển bằng $M/sc_mode: pass=khớp; fail=WARN in TRƯỚC khối
# DRIFT (đúng thứ tự generator thật); warnonly=toàn WARN rc 1
cat >"$M/bin/production_manifest.py" <<'EOF'
import os, sys
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
open(os.path.join(d, "sc_calls"), "a").write("called %s\n" % " ".join(sys.argv[1:]))
mode = open(os.path.join(d, "sc_mode")).read().strip()
if mode in ("fail", "warnonly"):
    print("WARN 1 selfcheck T3 vào/rời — tái sinh khi tiện:"); print("WARN + mike/bin/y_selfcheck.sh [T3]")
    if mode == "fail":
        print("DRIFT 1 dòng — manifest commit lệch thực tế."); print("+ x.py [T0] (mới vào production)")
    sys.exit(1)
EOF
# shellcheck disable=SC2016  # $(…)/$* phải nằm nguyên văn trong script giả, chỉ %s được thay
{
  printf '#!/usr/bin/env bash\n[ "$(cat "%s/sc_mode")" = skip ] && exit 1\necho "0 3 * * 0 x"\n' "$M" >"$FB/crontab"
  printf '#!/usr/bin/env bash\necho "$*" >>"%s/bus_calls"\n' "$M" >"$M/bin/append_event.sh"
  printf '#!/usr/bin/env bash\necho 4242\n' >"$M/bin/discord_channel.sh"
  printf '#!/usr/bin/env bash\necho "$*" >>"%s/discord_calls"\n' "$M" >"$M/bin/notify_thread.sh"
  printf '#!/usr/bin/env bash\necho called >>"%s/claude_calls"\necho "<<<FINDINGS_JSON>>>{\\"findings\\": [], \\"files_reviewed\\": 1, \\"files_clean\\": []}<<<END_FINDINGS>>>"\n' "$M" >"$FB/claude"
}
chmod +x "$M/bin/"*.sh "$FB/"*
cat >"$M/kb/production_manifest.json" <<'EOF'
{"files": {"a_t0.py": {"tier": "T0"}, "z_t0.py": {"tier": "T0"}, "old_t0.py": {"tier": "T0"},
 "b_t1.py": {"tier": "T1"}, "c_t2.sh": {"tier": "T2"}, "d_selfcheck.py": {"tier": "T3"},
 "e_unk.py": {"tier": "T?"}, "mike/bin/g_t0.sh": {"tier": "T0"}, "missing_t0.py": {"tier": "T0"},
 "trading_bot/plan.py": {"tier": "T0"}}}
EOF
g "$M" add -A; commit_at "$M" 10 base
MBASE="$(git -C "$M" rev-parse HEAD)"
echo x >"$M/bin/g_t0.sh"; g "$M" add -A; commit_at "$M" 1 recent

cmp -s "$M/bin/code_quality_weekly.sh" "$MIKE/bin/code_quality_weekly.sh" \
  && cmp -s "$M/bin/code_quality_scope.py" "$MIKE/bin/code_quality_scope.py" \
  || bad "harness: bản sao sandbox lệch bản thật"
[ "$(git -C "$WC" rev-parse --show-toplevel)" = "$OUT" ] || bad "harness: WC không phải thư mục con của toplevel ngoài"
# các lượt chạy THẬT (E5/E7/E8) chỉ an toàn nhờ override CQ_CLAUDE — mất nó thì selfcheck chạy tự động
# hằng ngày sẽ gọi LLM thật ⇒ dừng hẳn trước mọi lượt chạy
# shellcheck disable=SC2016  # chuỗi nguyên văn cần tìm
grep -qF 'CLAUDE="${CQ_CLAUDE:-' "$M/bin/code_quality_weekly.sh" \
  || { bad "harness: code_quality_weekly.sh mất override CQ_CLAUDE — DỪNG, không chạy thật với claude thật"; exit 1; }

scope() {  # scope <max> <since> [manifest] [repo2] [pin] — stdout = scope, $SB/dropped, rc
  python3 "$M/bin/code_quality_scope.py" --manifest "${3:-$M/kb/production_manifest.json}" \
    --wc-root "$WC" --repo "$WC" --repo "${4:-$M}" --since "$2" --max-files "$1" \
    --dropped-out "$SB/dropped" --pin "${5:-}" 2>"$SB/scope.err"
}
rel() { sed "s|^$WC/||" | paste -sd' ' -; }
BASE="a_t0.py mike/bin/g_t0.sh z_t0.py b_t1.py c_t2.sh"

# H1 đúng tầng + cửa sổ + map path (WC là thư mục con của toplevel): T0 trước (theo path), rồi T1, T2;
# loại T3, T?, ngoài manifest, ngoài WC, cũ >7 ngày, file manifest không tồn tại.
got="$(scope 25 "7 days ago" | rel)"
[ "$got" = "$BASE" ] && ok "H1 tầng/thứ tự/loại T3-T?-R&D/ngoài-WC/cửa sổ: $got" || bad "H1 được '$got' mong '$BASE'"
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

# H6 pin hot-core: đứng đầu + tính vào trần dù không đổi 7 ngày; pin trùng file đủ điều kiện không
# nhân đôi; pin không tồn tại bị bỏ qua
got="$(scope 3 "7 days ago" "" "" "$WC/trading_bot/plan.py" | rel)"; dr="$(rel <"$SB/dropped")"
[ "$got" = "trading_bot/plan.py a_t0.py mike/bin/g_t0.sh" ] && [ "$dr" = "z_t0.py b_t1.py c_t2.sh" ] \
  && ok "H6a pin đầu danh sách, tính vào trần" || bad "H6a giữ '$got' rớt '$dr'"
got="$(scope 25 "7 days ago" "" "" "$WC/z_t0.py" | rel)"
[ "$got" = "z_t0.py a_t0.py mike/bin/g_t0.sh b_t1.py c_t2.sh" ] && ok "H6b pin trùng không nhân đôi" || bad "H6b '$got'"
got="$(scope 25 "7 days ago" "" "" "$WC/trading_bot/khong_co.py" | rel)"
[ "$got" = "$BASE" ] && ok "H6c pin không tồn tại bị bỏ qua" || bad "H6c '$got'"

# --- E*: bản sao script thật, env -u TZ (§16), PATH có crontab giả, CQ_CLAUDE = claude giả ---
wk() { env -u TZ PATH="$FB:$PATH" CQ_CLAUDE="$FB/claude" bash "$M/bin/code_quality_weekly.sh" "$@" >"$SB/out" 2>&1; }
run() {  # run <sc_mode> — dry-run, stdout = scope (tương đối WC)
  echo "$1" >"$M/sc_mode"; wk --dry-run
  awk '/^=== SCOPE/{f=1;next} /^=== PROMPT/{f=0} f' "$SB/out" | rel
}
: >"$M/sc_calls"
got="$(run pass)"
if [ "$got" = "trading_bot/plan.py $BASE" ] && grep -q "Nguồn scope: MANIFEST" "$SB/out" \
   && ! grep -q "WARN: nguồn scope" "$SB/out"; then ok "E1 manifest HEAD khớp ⇒ scope manifest, hot-core đầu"
else bad "E1 scope '$got'"; tail -5 "$SB/out"; fi
grep -Eq '^called --crontab .* --check .*production_manifest\.json$' "$M/sc_calls" && [ "$(grep -c . "$M/sc_calls")" = 1 ] \
  && ok "E1b generator --check (crontab + HEAD manifest) thật sự được gọi" || bad "E1b generator giả: $(cat "$M/sc_calls")"

# E1c manifest working-copy lệch HEAD (chưa commit thêm research_x.py T0) ⇒ vẫn đọc bản HEAD
python3 -c 'import json,sys; p=sys.argv[1]; m=json.load(open(p)); m["files"]["research_x.py"]={"tier":"T0"}; json.dump(m,open(p,"w"))' \
  "$M/kb/production_manifest.json"
got="$(run pass)"
[ "$got" = "trading_bot/plan.py $BASE" ] && ok "E1c đọc manifest HEAD, bỏ qua working-copy chưa commit" \
  || bad "E1c scope '$got' (đọc nhầm working-copy?)"
g "$M" checkout -- kb/production_manifest.json

for mode in fail warnonly skip; do
  got="$(run "$mode")"
  case "$mode" in
    fail) why="manifest HEAD lệch thực tế.*DRIFT 1 dòng.*+ x.py";;
    warnonly) why="manifest HEAD lệch thực tế.*chỉ có dòng WARN";;
    skip) why="không đọc được crontab -l";;
  esac
  # fallback = danh sách cũ: hot-core round-robin + file R&D ngoài manifest (research_x.py)
  if [[ " $got " == *" trading_bot/plan.py "* && " $got " == *" research_x.py "* ]]; then
    grep -q "WARN: nguồn scope = FALLBACK.*$why" "$SB/out" && ! grep -q "FALLBACK.*y_selfcheck" "$SB/out" \
      && ok "E2-$mode ⇒ WARN nêu đúng nguyên nhân + fallback (hot-core + diff cũ)" \
      || bad "E2-$mode lý do sai: $(grep -m1 'WARN: nguồn' "$SB/out")"
  else bad "E2-$mode không fallback: '$got' $(grep -m1 -i 'error\|lỗi' "$SB/out")"; fi
done

# E7 chạy THẬT nhánh fallback (claude giả): claude giả được gọi, dòng Discord gắn cờ SCOPE FALLBACK
echo fail >"$M/sc_mode"; : >"$M/claude_calls"; wk
if [ -s "$M/claude_calls" ] && grep -q "SCOPE FALLBACK.*DRIFT 1 dòng" "$M/discord_calls" 2>/dev/null; then
  ok "E7 chạy thật fallback: Discord gắn cờ SCOPE FALLBACK + lý do"
else bad "E7 claude_calls=$(grep -c . "$M/claude_calls") discord=$(cat "$M/discord_calls" 2>/dev/null) $(tail -3 "$SB/out")"; fi
: >"$M/discord_calls"; : >"$M/bus_calls"; : >"$M/claude_calls"

# E5 manifest hợp lệ, tuần không có commit T0-T2, hot-core tuần này (idx 1 = executor.py) không tồn
# tại ⇒ scope rỗng hợp lệ: dry-run im bus; chạy thật ghi status đúng nguồn, KHÔNG gọi claude
echo '{"files": {"old_t0.py": {"tier": "T0"}}}' >"$M/kb/production_manifest.json"; g "$M" add -A; commit_at "$M" 0 quiet
echo '{"next_idx": 1}' >"$M/state/code_quality_weekly_rotation.json"
run pass >/dev/null
if grep -q "0 file trong scope (nguồn manifest" "$SB/out" && [ ! -s "$M/bus_calls" ]; then
  echo '{"next_idx": 1}' >"$M/state/code_quality_weekly_rotation.json"; wk
  grep -q "không có file T0-T2 nào có commit" "$M/bus_calls" 2>/dev/null && [ ! -s "$M/claude_calls" ] \
    && ok "E5 scope manifest rỗng: dry-run im bus, chạy thật ghi status đúng nguồn, không gọi claude" \
    || bad "E5 chạy thật bus=$(cat "$M/bus_calls" 2>/dev/null) claude=$(grep -c . "$M/claude_calls")"
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

# E8 ca B arch-review vòng 2: repo mike có commit 7 ngày nhưng TOÀN file bị loại trừ (research) ⇒
# nhánh fallback vẫn phải chạy tới claude + Discord, không chết im vì grep rc=1
g "$M" reset -q --hard "$MBASE"
mkdir -p "$M/agents/X/research"; echo x >"$M/agents/X/research/r.py"; g "$M" add -A; commit_at "$M" 1 research-only
echo fail >"$M/sc_mode"; : >"$M/claude_calls"; : >"$M/discord_calls"; wk
if [ -s "$M/claude_calls" ] && grep -q "SCOPE FALLBACK" "$M/discord_calls" 2>/dev/null; then
  ok "E8 fallback sống khi diff 1 repo toàn file loại trừ"
else bad "E8 claude_calls=$(grep -c . "$M/claude_calls") $(tail -3 "$SB/out")"; fi

[ "$fail" -eq 0 ] && echo "PASS code_quality_weekly_scope_selfcheck" || echo "FAIL code_quality_weekly_scope_selfcheck"
exit "$fail"
