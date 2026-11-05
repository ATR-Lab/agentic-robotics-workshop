# Shared launcher for the lab step scripts: find Python 3.9+ and hand the step to lab.py.
# Sourced by lab/NN-*.sh; not meant to be run on its own.

lab_main() {
  local here py
  here=${BASH_SOURCE[1]%/*}
  [ "$here" = "${BASH_SOURCE[1]}" ] && here=.
  for py in python3 python py; do
    if command -v "$py" >/dev/null 2>&1 &&
       "$py" -c 'import sys; sys.exit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
      PYTHONDONTWRITEBYTECODE=1 exec "$py" -I "$here/lab.py" "$@"
    fi
  done
  echo "FAIL  No Python 3.9 or newer found (tried python3, python and py)." >&2
  echo "      Fix: install Python 3.9+ (python.org; on Windows tick 'Add python.exe to PATH')," >&2
  echo "      open a new terminal and run this script again." >&2
  exit 2
}
