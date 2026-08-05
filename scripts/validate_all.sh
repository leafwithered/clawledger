#!/usr/bin/env bash
set -euo pipefail

zero_claw_exe="zeroclaw"
skip_network="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --zero-claw)
      zero_claw_exe="$2"
      shift 2
      ;;
    --skip-network)
      skip_network="true"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/clawledger-validation.XXXXXX")"
trap 'rm -rf -- "$validation_dir"' EXIT

cd "$repo_root"
export PYTHONPATH="$repo_root/src"

python -m compileall -q src tests scripts plugins
python -m unittest discover -s tests -v

if [[ "$skip_network" != "true" ]]; then
  python scripts/live_action_smoke.py
fi

"$zero_claw_exe" --version
"$zero_claw_exe" skills audit "$repo_root/zeroclaw/skills/clawledger"
"$zero_claw_exe" --config-dir "$validation_dir" config set sop.sops_dir "$repo_root/zeroclaw/sops"
"$zero_claw_exe" --config-dir "$validation_dir" sop validate clawledger-anchor

echo "ALL VALIDATIONS PASSED"
