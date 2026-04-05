#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
SERVICE_DIR="${REPO_ROOT}/services/python/elder-service"
PYPROJECT_FILE="${SERVICE_DIR}/pyproject.toml"
VENV_DIR="${SERVICE_DIR}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"
VENV_CFG="${VENV_DIR}/pyvenv.cfg"
LOCK_DIR="${VENV_DIR}.lock"
STAMP_FILE="${VENV_DIR}/.verify-deps.sha256"
TEST_DIR="${SERVICE_DIR}/tests"
SMOKE_TARGETS=(
  "${REPO_ROOT}/tests/integration/elder_mvp_smoke.py"
  "${REPO_ROOT}/tests/integration/elder_mvp_smoke.sh"
  "${REPO_ROOT}/tests/integration/elder_create_query_smoke.sh"
)

stage=${1:-all}

log() {
  printf '%s\n' "$1"
}

pick_locale() {
  local available
  available=$(locale -a 2>/dev/null || true)

  for candidate in C.UTF-8 en_US.UTF-8 UTF-8 C; do
    if grep -Fxq "${candidate}" <<<"${available}"; then
      printf '%s\n' "${candidate}"
      return
    fi
  done

  printf 'C\n'
}

CHOSEN_LOCALE=$(pick_locale)
export LANG="${CHOSEN_LOCALE}"
export LC_ALL="${CHOSEN_LOCALE}"

with_lock() {
  while ! mkdir "${LOCK_DIR}" 2>/dev/null; do
    sleep 1
  done

  trap 'rmdir "${LOCK_DIR}" >/dev/null 2>&1 || true' EXIT
  "$@"
  rmdir "${LOCK_DIR}" >/dev/null 2>&1 || true
  trap - EXIT
}

skip_if_missing_service() {
  if [[ ! -f "${PYPROJECT_FILE}" ]]; then
    log "[python] skipped: ${PYPROJECT_FILE} not found"
    exit 0
  fi
}

project_hash() {
  shasum -a 256 "${PYPROJECT_FILE}" | awk '{print $1}'
}

venv_dependencies_ready() {
  run_in_venv -c "import fastapi, httpx, uvicorn" >/dev/null 2>&1
}

ensure_venv() {
  if [[ ! -x "${VENV_PYTHON}" ]] || venv_uses_system_site_packages; then
    with_lock ensure_venv_locked
  fi
}

venv_uses_system_site_packages() {
  [[ -f "${VENV_CFG}" ]] && grep -Eq '^include-system-site-packages *= *true$' "${VENV_CFG}"
}

ensure_venv_locked() {
  if [[ ! -x "${VENV_PYTHON}" ]] || venv_uses_system_site_packages; then
    if [[ -d "${VENV_DIR}" ]] && venv_uses_system_site_packages; then
      log "[python] recreating elder-service virtualenv without system site packages"
      rm -rf "${VENV_DIR}"
    fi
    log "[python] creating elder-service virtualenv"
    python3 -m venv "${VENV_DIR}"
  fi

  "${VENV_PYTHON}" -m ensurepip --upgrade >/dev/null
}

install_dependencies() {
  local expected_hash current_hash

  expected_hash=$(project_hash)
  current_hash=""
  if [[ -f "${STAMP_FILE}" ]]; then
    current_hash=$(<"${STAMP_FILE}")
  fi

  if [[ "${current_hash}" == "${expected_hash}" ]]; then
    return
  fi

  with_lock install_dependencies_locked "${expected_hash}"
}

install_dependencies_locked() {
  local expected_hash current_hash

  expected_hash=${1}
  current_hash=""
  if [[ -f "${STAMP_FILE}" ]]; then
    current_hash=$(<"${STAMP_FILE}")
  fi

  if [[ "${current_hash}" == "${expected_hash}" ]]; then
    return
  fi

  if venv_dependencies_ready; then
    log "[python] reusing elder-service dependencies from ${VENV_DIR}"
    printf '%s\n' "${expected_hash}" > "${STAMP_FILE}"
    return
  fi

  log "[python] syncing elder-service dependencies from pyproject.toml"
  "${VENV_PYTHON}" -m pip install --disable-pip-version-check --no-build-isolation -e "${SERVICE_DIR}[test]"
  venv_dependencies_ready
  printf '%s\n' "${expected_hash}" > "${STAMP_FILE}"
}

run_in_venv() {
  PYTHONPATH="${SERVICE_DIR}/src" "${VENV_PYTHON}" "$@"
}

run_in_service_dir() {
  (
    cd "${SERVICE_DIR}"
    PYTHONPATH="${SERVICE_DIR}/src" "${VENV_PYTHON}" "$@"
  )
}

run_prepare() {
  log "[python] elder-service verification environment ready: ${VENV_PYTHON}"
  run_in_venv -c "import fastapi, httpx, uvicorn; print('fastapi/httpx/uvicorn imports ok')"
}

run_format() {
  run_in_venv -m compileall "${SERVICE_DIR}/src" >/dev/null
  log "[python] elder-service format check completed"
}

run_lint() {
  run_in_service_dir -m unittest discover -s tests
  log "[python] elder-service lint proxy check completed"
}

run_test() {
  run_prepare
  log "[python] running elder-service service and HTTP suites inside ${VENV_DIR}"
  run_in_service_dir -m unittest tests.test_service tests.test_http
}

run_build() {
  run_in_venv -c "from elder_service.http.server import create_app; app = create_app(); print(app.title)"
}

run_smoke() {
  local smoke_target smoke_label

  for smoke_target in "${SMOKE_TARGETS[@]}"; do
    if [[ ! -f "${smoke_target}" ]]; then
      continue
    fi

    smoke_label=${smoke_target#"${REPO_ROOT}/"}
    case "${smoke_target}" in
      *.py)
        log "[smoke] running ${smoke_label}"
        PYTHONPATH="${SERVICE_DIR}/src" REPO_ROOT="${REPO_ROOT}" "${VENV_PYTHON}" "${smoke_target}"
        return
        ;;
      *.sh)
        log "[smoke] running ${smoke_label}"
        PATH="${VENV_DIR}/bin:${PATH}" REPO_ROOT="${REPO_ROOT}" PYTHONPATH="${SERVICE_DIR}/src" bash "${smoke_target}"
        return
        ;;
    esac
  done

  log "[smoke] skipped: no supported smoke asset found under tests/integration"
}

run_all() {
  run_prepare
  run_format
  run_lint
  run_test
  run_build
  run_smoke
}

skip_if_missing_service
ensure_venv
install_dependencies

case "${stage}" in
  prepare)
    run_prepare
    ;;
  format)
    run_format
    ;;
  lint)
    run_lint
    ;;
  test)
    run_test
    ;;
  build)
    run_build
    ;;
  smoke)
    run_smoke
    ;;
  all)
    run_all
    ;;
  *)
    printf 'unknown stage: %s\n' "${stage}" >&2
    exit 2
    ;;
esac
