#!/usr/bin/env bash
# cli_provider_selfcheck.sh — self-check ARGV cua bin/dispatch.sh sau khi them lop provider
# (kb/cli_providers.json + bin/cli_provider.sh + _build_argv), 2026-08-03.
#
# VI SAO CAN (arch-reviewer required_change #10):
#   Pha 0 cua thiet ke tuyen bo "argv sinh ra GIONG HET chuoi cu, 0 thay doi hanh vi".
#   Do la mot tuyen bo KHONG THE kiem bang doc code: chuoi cu dung $MODEL_FLAG/$EFFORT_FLAG
#   KHONG QUOTE (co y — word-split thanh 2 word, hoac 0 word khi rong), nen "nhin thay giong"
#   va "argv thuc su giong" la hai chuyen khac nhau. Selfcheck co san
#   (dispatch_discord_topic_selfcheck.sh, 42/42) KHONG assert argv nao ca — no chi do dinh
#   tuyen topic. Neu khong co file nay, khong co gi giu loi hua Pha 0 khoi muc.
#
# CACH TEST: dung ROOT mike GIA trong tmpdir, bin/ la SYMLINK toi file THAT (dispatch.sh,
# cli_provider.sh, mike_json.py...) => chay dung code production. `claude`/`opencode` duoc
# thay bang STUB qua bin_env_override (DISPATCH_CLAUDE_BIN / DISPATCH_OPENCODE_BIN) — stub
# dump nguyen van argv ra file dang NUL-separated, nen so sanh la BYTE-FOR-BYTE, khong qua
# lop tach tu nao cua shell.
#
# ⚠️ Ke thua canh bao tu dispatch_discord_topic_selfcheck.sh: PHAI `rm -f` symlink truoc khi
#    ghi stub — `cat > <symlink>` di theo symlink va CAT CUT FILE THAT trong bin/.
#
# MUTATION TEST (bat buoc, ky luat vong 3): MUTATE=1 bash bin/cli_provider_selfcheck.sh
#    => sua 1 co trong _build_argv cua BAN SAO dispatch.sh, cac ca argv PHAI FAIL.
#    Bo test nao PASS ca o che do binh thuong lan che do mutation = khong test gi ca.
#
# Usage: bash mike/bin/cli_provider_selfcheck.sh        (exit 0 = tat ca PASS)
set -uo pipefail

REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
MK="$SB/mike"
PASS=0; FAIL=0

mkdir -p "$MK/bin" "$MK/kb" "$MK/bus/jobs" "$MK/logs" "$MK/state/circuit" "$MK/agents/Taylor"
for f in "$REAL/bin"/*; do [ -f "$f" ] && ln -s "$f" "$MK/bin/$(basename "$f")"; done
cp "$REAL/kb/discord_channels.json" "$MK/kb/discord_channels.json"
cp "$REAL/kb/cli_providers.json"    "$MK/kb/cli_providers.json"
printf '# Taylor test\n' > "$MK/agents/Taylor/CLAUDE.md"

_stub() {  # _stub <ten file trong bin> <noi dung>   (rm -f TRUOC — xem canh bao o header)
  rm -f "$MK/bin/$1"
  [ -e "$MK/bin/$1" ] && { echo "FATAL: khong go duoc $MK/bin/$1"; exit 1; }
  printf '%s\n' "$2" > "$MK/bin/$1"; chmod +x "$MK/bin/$1"
  [ -L "$MK/bin/$1" ] && { echo "FATAL: $MK/bin/$1 van la symlink"; exit 1; }
  return 0
}
_stub notify.sh          '#!/usr/bin/env bash'$'\n''exit 0'
_stub notify_thread.sh   '#!/usr/bin/env bash'$'\n''exit 0'
_stub consolidate.sh     '#!/usr/bin/env bash'$'\n''exit 0'
_stub append_event.sh    '#!/usr/bin/env bash'$'\n''exit 0'
_stub discord_channel.sh '#!/usr/bin/env bash'$'\n''exit 1'

# Stub CLI: dump argv NUL-separated => so sanh byte-for-byte, khong qua tach tu cua shell.
# Ghi CA stdin (2026-08-10): tu khi codex nhan prompt qua `codex exec -` (bat buoc — profile
# prompt-inline vuot tran MAX_ARG_STRLEN 128KiB neu de trong argv), khoi identity KHONG con
# nam trong argv. Test chi soi argv se bao "mat identity" trong khi thuc te van du.
cat > "$SB/cli_stub.sh" <<EOF
#!/usr/bin/env bash
for a in "\$@"; do printf '%s\0' "\$a"; done > "$SB/argv.bin"
cat > "$SB/stdin.bin" 2>/dev/null || : > "$SB/stdin.bin"
echo "STUB-OK"
exit 0
EOF
chmod +x "$SB/cli_stub.sh"

# MUTATE=1: thay symlink dispatch.sh bang BAN SAO da sua 1 co trong _build_argv.
if [ "${MUTATE:-0}" = "1" ]; then
  rm -f "$MK/bin/dispatch.sh"
  sed 's/--permission-mode auto --max-turns/--permission-mode-MUTATED auto --max-turns/' \
      "$REAL/bin/dispatch.sh" > "$MK/bin/dispatch.sh"
  chmod +x "$MK/bin/dispatch.sh"
  echo "### CHE DO MUTATION — cac ca argv claude PHAI FAIL ###"
fi

# run <dispatch args...> — chay dong bo, roi doc argv.bin
run() {
  rm -f "$SB/argv.bin" "$SB/stdin.bin"
  ( cd "$MK" && env DISPATCH_CGROUP_DETACH=0 \
      DISPATCH_CLAUDE_BIN="$SB/cli_stub.sh" DISPATCH_OPENCODE_BIN="$SB/cli_stub.sh" \
      DISPATCH_FROM=Mike \
      bash "$MK/bin/dispatch.sh" "$@" ) > "$SB/out" 2> "$SB/err"
  return $?
}

# argv_is <mo ta> <expected args...> — so khop TOAN BO argv, tru phan tu prompt (kiem rieng).
# Prompt bi dispatch boc them tien to "[DISPATCH tu ...]" + huong dan bus, nen o day ta thay
# no bang token <PROMPT> roi so; noi dung prompt duoc kiem boi ca rieng ben duoi.
argv_is() {
  local desc="$1"; shift
  local got
  got="$(python3 -c '
import sys
raw = open(sys.argv[1], "rb").read().split(b"\0")[:-1]
args = [a.decode("utf-8", "replace") for a in raw]
# phan tu nao chua marker dispatch = prompt -> thay bang <PROMPT>
out = ["<PROMPT>" if "[DISPATCH" in a else a for a in args]
print("".join(out))
' "$SB/argv.bin" 2>/dev/null)"
  local want; want="$(printf '%s\001' "$@")"; want="${want%$'\001'}"
  if [ "$got" = "$want" ]; then
    printf '    ok   %s\n' "$desc"; PASS=$((PASS+1))
  else
    printf '    FAIL %s\n         want: %s\n         got : %s\n' \
      "$desc" "$(printf '%s' "$want" | tr '\001' ' ')" "$(printf '%s' "$got" | tr '\001' ' ')"
    FAIL=$((FAIL+1))
  fi
}
chk() {  # chk <mo ta> <gia tri thuc> <gia tri mong doi>
  if [ "$2" = "$3" ]; then printf '    ok   %s = %s\n' "$1" "$2"; PASS=$((PASS+1))
  else printf '    FAIL %s: want=%s got=%s\n' "$1" "$3" "$2"; FAIL=$((FAIL+1)); fi
}

echo "== CA 1: claude mac dinh (khong --model, khong --effort)"
echo "   chuoi cu: -p P --permission-mode auto --max-turns 50 \$MODEL_FLAG(rong) --effort medium"
run Taylor "viec test"
argv_is "argv claude mac dinh" -p "<PROMPT>" --permission-mode auto --max-turns 50 --effort medium

echo "== CA 2: --model opus --effort high (MAX_TURNS scale theo effort = 80)"
run Taylor "viec test" --model opus --effort high
argv_is "argv co --model" -p "<PROMPT>" --permission-mode auto --max-turns 80 --model opus --effort high

echo "== CA 3: --model fable --effort max  ⇒ CLAMP effort=high (chinh sach user 07-14)"
run Taylor "viec test" --model fable --effort max
argv_is "argv fable bi clamp" -p "<PROMPT>" --permission-mode auto --max-turns 80 --model fable --effort high

echo "== CA 4: --effort xhigh ⇒ MAX_TURNS=120"
run Taylor "viec test" --effort xhigh
argv_is "argv xhigh" -p "<PROMPT>" --permission-mode auto --max-turns 120 --effort xhigh

echo "== CA 5: --max-turns 33 tuong minh de len scale"
run Taylor "viec test" --effort high --max-turns 33
argv_is "argv max-turns tuong minh" -p "<PROMPT>" --permission-mode auto --max-turns 33 --effort high

echo "== CA 6: prompt tieng Viet co dau \" va backtick ⇒ toi nguyen ven trong DUNG 1 argv"
VNP='Kiem tra "bao cao" va `filter.json` — dung de vo'
run Taylor "$VNP"
_np="$(python3 -c '
import sys
raw = open(sys.argv[1],"rb").read().split(b"\0")[:-1]
args=[a.decode("utf-8","replace") for a in raw]
hits=[a for a in args if "[DISPATCH" in a]
print(len(hits))' "$SB/argv.bin")"
chk "so argv chua prompt (phai la 1, khong bi tach tu)" "$_np" "1"
_intact="$(python3 -c '
import sys
raw = open(sys.argv[1],"rb").read().split(b"\0")[:-1]
args=[a.decode("utf-8","replace") for a in raw]
p=[a for a in args if "[DISPATCH" in a][0]
print("yes" if sys.argv[2] in p else "no")' "$SB/argv.bin" "$VNP")"
chk "prompt giu nguyen van ca \" lan backtick" "$_intact" "yes"

echo "== CA 7: provider opencode ⇒ run --dir --auto, prompt POSITIONAL o cuoi"
run Taylor "viec test" --provider opencode --model opencode/deepseek-v4-flash-free --effort high
argv_is "argv opencode" run --dir "$MK/agents/Taylor" --auto -m opencode/deepseek-v4-flash-free --variant high "<PROMPT>"

echo "== CA 8: cong provider — agent ngoai allow_agents ⇒ HUY, CLI khong duoc chay"
rm -f "$SB/argv.bin"
mkdir -p "$MK/agents/Mafee"; printf '# Mafee\n' > "$MK/agents/Mafee/CLAUDE.md"
run Mafee "viec test" --provider opencode; _rc=$?
chk "exit code khac 0" "$([ "$_rc" -ne 0 ] && echo yes || echo no)" "yes"
chk "CLI KHONG duoc goi" "$([ -f "$SB/argv.bin" ] && echo goi || echo khong-goi)" "khong-goi"

echo "== CA 9: provider dang tat ⇒ HUY, khong am tham roi ve claude"
# TAT TUONG MINH trong registry sandbox (sua 2026-08-10). Truoc day ca nay muon codex dang
# enabled=false o registry THAT — mot anh chup cau hinh, khong phai tien de. Khi user bat codex
# (2026-08-10) ca nay khong con test "provider tat" nua, va te hon: bin cua codex luc do la
# `codex` THAT chu khong phai stub, nen selfcheck GOI CLI THAT. Giờ tự dựng điều kiện rồi khôi phục.
rm -f "$SB/argv.bin"
cp "$MK/kb/cli_providers.json" "$SB/reg_before_ca9.json"
python3 -c 'import json,sys
p=sys.argv[1]; r=json.load(open(p,encoding="utf-8"))
r["providers"]["codex"]["enabled"]=False
json.dump(r,open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=2)' "$MK/kb/cli_providers.json"
run Taylor "viec test" --provider codex; _rc=$?
cp "$SB/reg_before_ca9.json" "$MK/kb/cli_providers.json"
chk "exit code khac 0" "$([ "$_rc" -ne 0 ] && echo yes || echo no)" "yes"
chk "CLI KHONG duoc goi" "$([ -f "$SB/argv.bin" ] && echo goi || echo khong-goi)" "khong-goi"

echo "== CA 10: model cua provider khac ⇒ HUY (khong tu dich tier — su co model-drift 07-17)"
rm -f "$SB/argv.bin"
run Taylor "viec test" --provider opencode --model opus; _rc=$?
chk "exit code khac 0" "$([ "$_rc" -ne 0 ] && echo yes || echo no)" "yes"
chk "CLI KHONG duoc goi" "$([ -f "$SB/argv.bin" ] && echo goi || echo khong-goi)" "khong-goi"

echo "== CA 11: job record ghi lai provider + turn_cap (triage doc duoc, khong doan)"
run Taylor "viec test" --provider opencode --model opencode/deepseek-v4-flash-free
_jf="$(find "$MK/bus/jobs" -name '*.json' | sort | tail -1)"
_pv="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("provider",""))' "$_jf" 2>/dev/null)"
_tc="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("turn_cap",""))' "$_jf" 2>/dev/null)"
chk "job.provider" "$_pv" "opencode"
chk "job.turn_cap (opencode khong co turn-cap)" "$_tc" "unsupported"

echo "== CA 12: profile=prompt-inline ⇒ identity+context ĐƯỢC BƠM VÀO PROMPT"
echo "   (provider khong doc duoc CLAUDE.md/AGENTS.md cua fleet — vd codex, agy)"
# Bat codex trong registry SANDBOX + tro bin sang stub. Khong dung registry that.
python3 - "$MK/kb/cli_providers.json" "$SB/cli_stub.sh" <<'PY'
import json, sys
p, stub = sys.argv[1], sys.argv[2]
reg = json.load(open(p, encoding="utf-8"))
c = reg["providers"]["codex"]
c["enabled"] = True
c["bin"] = stub
c["env"] = {}
json.dump(reg, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
printf '# Taylor test\n@%s/kb/context_ops_mini.md\n' "$REAL" > "$MK/agents/Taylor/CLAUDE.md"
run Taylor "viec test" --provider codex
# Prompt co the o ARGV (claude/opencode/agy) hoac STDIN (codex). Ghep ca hai roi moi soi —
# dung cho ca hai duong van chuyen, khong phai sua test moi lan doi provider.
_pin="$(python3 -c '
import sys, os
raw = open(sys.argv[1],"rb").read().split(b"\0")[:-1]
args=[a.decode("utf-8","replace") for a in raw]
sin = sys.argv[2]
if os.path.exists(sin):
    args.append(open(sin,"rb").read().decode("utf-8","replace"))
hits=[a for a in args if "[DISPATCH" in a]
p = hits[0] if hits else ""
print("yes" if "BOI CANH THUONG TRUC" in p else "no")
print("yes" if "Taylor test" in p else "no")
print("yes" if "ROOT" in p and "context ops-mini" in p else "no")
' "$SB/argv.bin" "$SB/stdin.bin" 2>/dev/null)"
chk "prompt co khoi identity"       "$(echo "$_pin"|sed -n 1p)" "yes"
chk "prompt co CLAUDE.md cua agent"  "$(echo "$_pin"|sed -n 2p)" "yes"
chk "prompt co @import DA EXPAND"    "$(echo "$_pin"|sed -n 3p)" "yes"

echo "== CA 13: provider antigravity (agy) — argv + prompt-inline"
python3 - "$MK/kb/cli_providers.json" "$SB/cli_stub.sh" <<'PY'
import json, sys
p, stub = sys.argv[1], sys.argv[2]
reg = json.load(open(p, encoding="utf-8"))
a = reg["providers"]["antigravity"]
a["enabled"] = True
a["bin"] = stub
json.dump(reg, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
run Taylor "viec test" --provider antigravity
argv_is "argv agy (--add-dir, -p o cuoi)" --add-dir "$MK/agents/Taylor" -p "<PROMPT>"
_agyp="$(python3 -c '
import sys
raw = open(sys.argv[1],"rb").read().split(b"\0")[:-1]
args=[a.decode("utf-8","replace") for a in raw]
hits=[a for a in args if "[DISPATCH" in a]
print("yes" if hits and "BOI CANH THUONG TRUC" in hits[0] else "no")' "$SB/argv.bin" 2>/dev/null)"
chk "agy cung duoc bom identity (prompt-inline)" "$_agyp" "yes"

echo
if [ "$FAIL" -eq 0 ]; then
  echo "PASS — $PASS/$((PASS+FAIL)) assertion dung"
  [ "${MUTATE:-0}" = "1" ] && { echo "❌ NHUNG DANG O CHE DO MUTATION — dang le phai FAIL. Test khong canh gi ca."; exit 1; }
  exit 0
else
  echo "FAIL — $FAIL/$((PASS+FAIL)) assertion sai"
  [ "${MUTATE:-0}" = "1" ] && { echo "✅ Dung nhu mong doi o che do MUTATION (test that su canh argv)."; exit 0; }
  exit 1
fi
