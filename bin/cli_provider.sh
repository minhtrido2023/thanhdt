#!/usr/bin/env bash
# cli_provider.sh <subcommand> [args]
#
# Resolver cho kb/cli_providers.json — registry DUY NHAT khai bao CLI provider cua
# bin/dispatch.sh (claude / opencode / codex / ...). Cung pattern voi
# bin/discord_channel.sh: 1 registry + 1 resolver + FAIL LOUD, khong bao gio doan.
#
# ⚠️ RANH GIOI CUNG (arch-reviewer 2026-08-03, required_change #2):
#   Script nay chi TRA CUU FIELD. No KHONG BAO GIO in ra / van chuyen argv.
#   argv duoc dung bang ARRAY bash ngay trong _bg_wrapper cua dispatch.sh (_build_argv).
#   Ly do da do thuc nghiem:
#     - NUL khong song qua $( ):  x="$(printf 'a\0b\0c')" -> len=3 "abc"
#     - array bash khong vuot duoc `bash -c '_bg_wrapper'`: export arr -> declare: not found
#     - moi duong di qua `eval` chuoi tai sinh lop loi quoting §15 coding_guidelines (4 su co)
#   Neu ban dang dinh them subcommand `argv` vao day: DUNG LAI, doc lai doan tren.
#
# Subcommand:
#   field <provider> <key>   in gia tri 1 field. key phang (bin, enabled, profile,
#                            supports_turns, usage_probe, max_turns_pattern, label).
#                            List (models/efforts/allow_agents) in moi phan tu 1 dong.
#                            Provider khong ton tai / disabled / key thieu => exit 1 + stderr.
#   bin <provider>           in duong dan binary, DA ap dung bin_env_override neu bien do co set.
#   env-exports <provider>   in cac dong KEY=VALUE (da noi ${PATH}) de caller `export`.
#                            Khong co env => in rong, exit 0.
#   list                     in provider dang enabled (1 dong 1 ten).
#   check <provider>         chay `<bin> --version` VOI env da ap dung.
#                            exit 0 = provider chay duoc; exit 1 = PROVIDER HONG (khong phai
#                            loi task). Day la thu phan biet "CLI hong" voi "agent lam sai" —
#                            thieu no thi codex chet duoi PATH cron se trip circuit breaker
#                            cua AGENT, do oan (arch-reviewer required_change #3).
#   validate <provider> <agent> [model] [effort]
#                            kiem enabled + allow_agents + model thuoc danh sach + effort hop le.
#                            In effort DA CLAMP ra stdout (theo effort_caps). exit 1 neu sai.
#
# ⚠️ allow_agents CHI chan o tang dispatch.sh. Agent co Bash van goi thang binary duoc.
#    Cuong che THAT = `permission` trong agents/<id>/opencode.json (da kiem chung).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY="${CLI_PROVIDERS_REGISTRY:-$ROOT/kb/cli_providers.json}"

_py() { python3 - "$REGISTRY" "$@"; }

sub="${1:-}"
[ -n "$sub" ] || { echo "usage: cli_provider.sh {field|bin|env-exports|list|check|validate} ..." >&2; exit 2; }
shift || true

case "$sub" in
  list)
    _py <<'PY'
import json, sys
try:
    reg = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    print(f"cli_provider: khong doc duoc registry {sys.argv[1]}: {e}", file=sys.stderr); sys.exit(1)
for name, p in sorted(reg.get("providers", {}).items()):
    if p.get("enabled"):
        print(name)
PY
    ;;

  field)
    prov="${1:?usage: cli_provider.sh field <provider> <key>}"
    key="${2:?usage: cli_provider.sh field <provider> <key>}"
    _py "$prov" "$key" <<'PY'
import json, sys
reg_path, prov, key = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    reg = json.load(open(reg_path, encoding="utf-8"))
except Exception as e:
    print(f"cli_provider: khong doc duoc registry {reg_path}: {e}", file=sys.stderr); sys.exit(1)
providers = reg.get("providers", {})
p = providers.get(prov)
if p is None:
    print(f"cli_provider: KHONG CO provider '{prov}' trong {reg_path}", file=sys.stderr)
    print("  provider hop le: " + ", ".join(sorted(providers)), file=sys.stderr)
    sys.exit(1)
if key not in p:
    print(f"cli_provider: provider '{prov}' khong co field '{key}'", file=sys.stderr); sys.exit(1)
v = p[key]
if isinstance(v, bool):
    print("true" if v else "false")
elif isinstance(v, list):
    for item in v:
        print(item)
elif v is None:
    pass                      # null => in rong, exit 0 (khac voi "thieu field" = exit 1)
else:
    print(v)
PY
    ;;

  bin)
    prov="${1:?usage: cli_provider.sh bin <provider>}"
    ovr_name="$("$0" field "$prov" bin_env_override 2>/dev/null || true)"
    if [ -n "$ovr_name" ] && [ -n "${!ovr_name:-}" ]; then
      printf '%s\n' "${!ovr_name}"      # DISPATCH_CLAUDE_BIN etc — giu selfcheck song (F11)
    else
      "$0" field "$prov" bin
    fi
    ;;

  env-exports)
    prov="${1:?usage: cli_provider.sh env-exports <provider>}"
    _py "$prov" <<'PY'
import json, os, sys
reg_path, prov = sys.argv[1], sys.argv[2]
try:
    reg = json.load(open(reg_path, encoding="utf-8"))
except Exception as e:
    print(f"cli_provider: khong doc duoc registry {reg_path}: {e}", file=sys.stderr); sys.exit(1)
p = reg.get("providers", {}).get(prov)
if p is None:
    print(f"cli_provider: KHONG CO provider '{prov}'", file=sys.stderr); sys.exit(1)
for k, v in (p.get("env") or {}).items():
    # Ho tro ${PATH} de NOI CHUOI, khong phai thay the — pin interpreter cho CLI dang
    # shim `#!/usr/bin/env node` (codex). Xem _README cua registry.
    print(f"{k}={str(v).replace('${PATH}', os.environ.get('PATH', ''))}")
PY
    ;;

  check)
    prov="${1:?usage: cli_provider.sh check <provider>}"
    en="$("$0" field "$prov" enabled)" || exit 1
    if [ "$en" != "true" ]; then
      echo "cli_provider: provider '$prov' DANG TAT (enabled=false) trong $REGISTRY" >&2
      exit 1
    fi
    b="$("$0" bin "$prov")" || exit 1
    if [ ! -x "$b" ]; then
      echo "cli_provider: PROVIDER HONG — binary cua '$prov' khong ton tai/khong chay duoc: $b" >&2
      echo "  (day la loi PROVIDER, KHONG phai loi task — dung do cho agent)" >&2
      exit 1
    fi
    # Chay thu --version VOI env da ap dung. Bat duoc ca ca "bin dung nhung interpreter sai"
    # (codex duoi PATH cron: /usr/bin/node v12.22.9 < engines>=16 -> SyntaxError) — thu ma
    # kiem tra `-x` o tren KHONG bat duoc.
    _out="$(
      set -a
      while IFS= read -r line; do [ -n "$line" ] && export "${line?}"; done < <("$0" env-exports "$prov")
      set +a
      timeout 30 "$b" --version 2>&1
    )"; _rc=$?
    if [ "$_rc" -ne 0 ]; then
      echo "cli_provider: PROVIDER HONG — '$prov' chay '--version' that bai (rc=$_rc):" >&2
      printf '  %s\n' "$_out" | head -5 >&2
      echo "  (loi PROVIDER, KHONG phai loi task. Kiem env/interpreter trong $REGISTRY)" >&2
      exit 1
    fi
    printf '%s\n' "$_out" | head -1
    ;;

  validate)
    prov="${1:?usage: cli_provider.sh validate <provider> <agent> [model] [effort]}"
    agent="${2:?usage: cli_provider.sh validate <provider> <agent> [model] [effort]}"
    model="${3:-}"
    effort="${4:-}"
    _py "$prov" "$agent" "$model" "$effort" <<'PY'
import json, sys
reg_path, prov, agent, model, effort = sys.argv[1:6]
try:
    reg = json.load(open(reg_path, encoding="utf-8"))
except Exception as e:
    print(f"cli_provider: khong doc duoc registry {reg_path}: {e}", file=sys.stderr); sys.exit(1)
providers = reg.get("providers", {})
p = providers.get(prov)
if p is None:
    print(f"cli_provider: KHONG CO provider '{prov}'", file=sys.stderr)
    print("  provider hop le: " + ", ".join(sorted(providers)), file=sys.stderr); sys.exit(1)
if not p.get("enabled"):
    note = p.get("notes")
    print(f"cli_provider: provider '{prov}' DANG TAT (enabled=false).", file=sys.stderr)
    if note:
        for line in ([note] if isinstance(note, str) else note):
            print(f"    {line}", file=sys.stderr)
    sys.exit(1)
allow = p.get("allow_agents", "*")
if allow != "*" and agent not in allow:
    print(f"cli_provider: agent '{agent}' KHONG duoc phep chay tren provider '{prov}'.", file=sys.stderr)
    print(f"  allow_agents: {', '.join(allow)}", file=sys.stderr)
    print("  (day la DAI THU HAI o tang dispatch; cuong che that nam o `permission`", file=sys.stderr)
    print("   trong agents/<id>/opencode.json. Muon noi rong: sua kb/cli_providers.json)", file=sys.stderr)
    sys.exit(1)
models = p.get("models") or []
if model and models and model not in models:
    print(f"cli_provider: model '{model}' khong hop le cho provider '{prov}'.", file=sys.stderr)
    print("  model hop le: " + ", ".join(models), file=sys.stderr)
    print("  (KHONG tu dich tier giua provider — do la lop su co model-drift 07-17)", file=sys.stderr)
    sys.exit(1)
efforts = p.get("efforts") or []
if effort and efforts and effort not in efforts:
    print(f"cli_provider: effort '{effort}' khong hop le cho provider '{prov}'.", file=sys.stderr)
    print("  effort hop le: " + ", ".join(efforts), file=sys.stderr); sys.exit(1)
# Clamp theo effort_caps (vd chinh sach user: fable toi da 'high')
caps = p.get("effort_caps") or {}
if model in caps and effort:
    order = efforts or ["low", "medium", "high", "xhigh", "max"]
    cap = caps[model]
    if cap in order and effort in order and order.index(effort) > order.index(cap):
        print(f"cli_provider: WARN {prov}/{model} gioi han effort toi da '{cap}' "
              f"— ha '{effort}' -> '{cap}'.", file=sys.stderr)
        effort = cap
sys.stdout.write(effort)
PY
    ;;

  *)
    echo "cli_provider: subcommand khong hop le '$sub' (dung: field|bin|env-exports|list|check|validate)" >&2
    exit 2
    ;;
esac
