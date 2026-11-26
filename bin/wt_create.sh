#!/usr/bin/env bash
# wt_create.sh — create a lightweight SPARSE git worktree instead of checking out
# multi-GB research/archive directories for small code/config edits.
#
# Usage:
#   bin/wt_create.sh <wt_path> [branch_name] [--repo PATH] [--include SUBPATH ...]
#
# Examples:
#   bin/wt_create.sh ../wt-123456 session/123456
#   bin/wt_create.sh ../wt-123456 session/123456 --include agents/Taylor/research/dd_POW_20261118
set -euo pipefail

DEFAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
wt_path=""
branch=""
repo=""
includes=()

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)
      repo="${2:?--repo requires a path}"
      shift 2
      ;;
    --repo=*)
      repo="${1#*=}"
      shift
      ;;
    --include)
      includes+=("${2:?--include requires a subpath}")
      shift 2
      ;;
    --include=*)
      includes+=("${1#*=}")
      shift
      ;;
    -h|--help)
      sed -n '2,12p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    -*)
      echo "wt_create: unknown option '$1'" >&2
      exit 2
      ;;
    *)
      if [ -z "$wt_path" ]; then
        wt_path="$1"
      elif [ -z "$branch" ]; then
        branch="$1"
      else
        echo "wt_create: unexpected extra positional argument '$1'" >&2
        exit 2
      fi
      shift
      ;;
  esac
done

if [ -z "$wt_path" ]; then
  echo "usage: wt_create.sh <wt_path> [branch_name] [--repo PATH] [--include SUBPATH ...]" >&2
  exit 2
fi

if [ -z "$repo" ]; then
  repo="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "$DEFAULT_ROOT")"
fi
repo="$(cd "$repo" && pwd)"

if [ -z "$branch" ]; then
  base="$(basename "$wt_path")"
  base="${base#wt-}"
  branch="session/${base}"
fi

if [ -e "$wt_path" ]; then
  echo "wt_create: target path already exists: $wt_path" >&2
  exit 1
fi

mkdir -p "$(dirname "$wt_path")"
if git -C "$repo" show-ref --verify --quiet "refs/heads/$branch"; then
  git -C "$repo" worktree add --no-checkout "$wt_path" "$branch"
else
  git -C "$repo" worktree add --no-checkout "$wt_path" -b "$branch"
fi

patterns=(
  "/*"
  "!/agents/Taylor/research/"
  "!/agents/Taylor/exp_*/"
  "!/agents/Taylor/probe_*/"
  "!/reports/"
  "!/kb/archive/"
)
for inc in "${includes[@]}"; do
  inc="${inc#/}"
  inc="${inc%/}"
  [ -n "$inc" ] || continue
  patterns+=("/${inc}" "/${inc}/*")
done

git -C "$wt_path" sparse-checkout init --no-cone
git -C "$wt_path" sparse-checkout set --no-cone "${patterns[@]}"
git -C "$wt_path" checkout -q

echo "SPARSE WORKTREE READY: $wt_path [$branch] (excluded heavy research/reports/archive)"
