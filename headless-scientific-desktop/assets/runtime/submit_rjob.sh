#!/usr/bin/env bash
# All cluster-specific values are runtime inputs; GPU allocation is always zero.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
RUN_ID=${CUA_RUN_ID:-desktop-$(date +%Y%m%d-%H%M%S)-$$}
JOB_NAME=${1:-$RUN_ID}
: "${CUA_NAMESPACE:?set CUA_NAMESPACE}"
: "${CUA_CHARGED_GROUP:?set CUA_CHARGED_GROUP}"
: "${CUA_IMAGE:?set CUA_IMAGE}"
: "${CUA_MOUNT:?set one explicit CUA_MOUNT supported by rjob}"
ARCHIVE=${SLICER_ARCHIVE:-${CUA_SOFTWARE_DIR:-$(dirname "$ROOT")/software}/Slicer-5.12.4-linux-amd64.tar.gz}
if [[ "${CUA_DRY_RUN:-0}" != 1 && ! -f "$ARCHIVE" && -z "${SLICER_APP_DIR:-}" ]]; then
  echo 'Missing Slicer archive; prepare software in a download job first.' >&2
  exit 1
fi
export KUBEBRAIN_NAMESPACE="$CUA_NAMESPACE"
env_values=("CUA_ROOT=$ROOT" "CUA_RUN_ID=$RUN_ID" "SLICER_ARCHIVE=$ARCHIVE"
  "CUA_SCREEN_WIDTH=${CUA_SCREEN_WIDTH:-1440}" "CUA_SCREEN_HEIGHT=${CUA_SCREEN_HEIGHT:-900}"
  "CUA_RECORD_SCREEN=${CUA_RECORD_SCREEN:-0}" "CUA_MAX_SECONDS=${CUA_MAX_SECONDS:-3600}"
  "CUA_OFFLINE=${CUA_OFFLINE:-1}")
for name in SLICER_APP_DIR CUA_SOFTWARE_DIR CUA_PACKAGE_CACHE CUA_ARTIFACT_DIR CUA_BRIDGE_HOST CUA_BRIDGE_PORT CUA_RECORD_FPS CUA_RECORD_MAX_BYTES CUA_INSTALL_RUNTIME CUA_PYTHON_LIB CUA_NO_PROXY_EXTRA; do
  if [[ -n "${!name:-}" ]]; then env_values+=("$name=${!name}"); fi
done
args=(submit --name "$JOB_NAME" --namespace="$CUA_NAMESPACE"
  --charged-group="$CUA_CHARGED_GROUP" --image "$CUA_IMAGE"
  --cpu "${CUA_CPU:-2}" --gpu 0 --memory "${CUA_MEMORY:-8000}" --replicas=1
  --host-network=false --mount "$CUA_MOUNT" --env "${env_values[@]}")
if [[ -n "${CUA_PRIVATE_MACHINE:-}" ]]; then args+=(--private-machine="$CUA_PRIVATE_MACHINE"); fi
if [[ "${CUA_DRY_RUN:-0}" == 1 ]]; then args+=(--dry-run true); fi
case "${CUA_MODE:-desktop}" in
  desktop) runner=run_slicer.sh ;;
  smoke) runner=rjob_run_smoke.sh ;;
  *) echo 'CUA_MODE must be desktop or smoke' >&2; exit 2 ;;
esac
rjob "${args[@]}" -- bash "$ROOT/$runner"
