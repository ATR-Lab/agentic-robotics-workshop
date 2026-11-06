#!/usr/bin/env bash
# Install what the workshop lab needs on macOS or Linux: Python 3, Git and Docker Engine
# (docker-ce, docker-ce-cli, containerd.io, docker-buildx-plugin, docker-compose-plugin on Linux),
# then pull the station image. On Windows, run scripts/install-windows.ps1 instead.
#
# Usage: bash scripts/install.sh [--no-pull] [--desktop]
#   or, before you have the folder:
#   curl -fsSL https://raw.githubusercontent.com/ATR-Lab/agentic-robotics-workshop/main/scripts/install.sh | bash
#
# Linux (Ubuntu, Debian and their derivatives, Fedora, RHEL, CentOS, Rocky, Alma): adds Docker's own package
# repository, installs the latest Docker Engine packages, starts the service and adds you to the docker group.
# Packages that conflict with Docker's (docker.io, podman-docker, distribution containerd and runc) are removed.
# macOS: Docker Engine only runs on Linux, so it runs in a small Linux VM managed by Colima (Homebrew packages
# docker, docker-buildx, docker-compose and colima). --desktop installs Docker Desktop instead. A Docker that
# already works (OrbStack or Docker Desktop) is kept as it is.
# Every command that changes the computer is printed with a $ in front. Safe to run again.
set -euo pipefail

IMAGE=ghcr.io/atr-lab/agentic-workshop-station:2026.11
PULL=1
DESKTOP=0
CHECK_DOCKER=1
for arg in "$@"; do
  case "$arg" in
    --no-pull) PULL=0 ;;
    --desktop) DESKTOP=1 ;;
    -h|--help) sed -n '2,16p' "${BASH_SOURCE[0]}" 2>/dev/null | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "FAIL unknown option $arg (use --no-pull, --desktop or --help)" >&2; exit 2 ;;
  esac
done

say() { printf '\n== %s\n' "$*"; }
run() { printf '$ %s\n' "$*"; "$@"; }
fail() { printf 'FAIL %s\n' "$*" >&2; exit 1; }

SUDO=
if [ "$(id -u)" -ne 0 ]; then
  SUDO=sudo
fi

python_ok() {
  command -v python3 >/dev/null 2>&1 &&
    python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1
}

docker_ok() {
  command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1
}

# ---------------------------------------------------------------- Linux

linux_remove_conflicts() {
  # Docker's install guide: these distribution packages conflict with docker-ce.
  local found=
  for pkg in "$@"; do
    if [ "$PKG" = apt ]; then
      dpkg -s "$pkg" >/dev/null 2>&1 && found="$found $pkg"
    else
      rpm -q "$pkg" >/dev/null 2>&1 && found="$found $pkg"
    fi
  done
  if [ -n "$found" ]; then
    echo "Removing packages that conflict with Docker Engine:$found"
    if [ "$PKG" = apt ]; then
      # shellcheck disable=SC2086
      run $SUDO apt-get remove -y $found
    else
      # shellcheck disable=SC2086
      run $SUDO dnf remove -y $found
    fi
  fi
}

linux_apt() {
  local repo codename
  # Ubuntu and its derivatives (Mint, Pop!_OS) use Docker's Ubuntu repository; Debian and others its Debian one.
  case " $ID ${ID_LIKE:-} " in
    *" ubuntu "*) repo=ubuntu; codename=${UBUNTU_CODENAME:-${VERSION_CODENAME:-}} ;;
    *) repo=debian; codename=${DEBIAN_CODENAME:-${VERSION_CODENAME:-}} ;;
  esac
  [ -n "$codename" ] || fail "cannot tell which $repo release this is (no VERSION_CODENAME in /etc/os-release)"

  say "Python 3 and Git"
  run $SUDO apt-get update -qq
  run $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y python3 git ca-certificates curl

  say "Docker Engine from Docker's $repo repository ($codename)"
  linux_remove_conflicts docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc
  run $SUDO install -m 0755 -d /etc/apt/keyrings
  run $SUDO curl -fsSL "https://download.docker.com/linux/$repo/gpg" -o /etc/apt/keyrings/docker.asc
  run $SUDO chmod a+r /etc/apt/keyrings/docker.asc
  if [ -e /etc/apt/sources.list.d/docker.sources ]; then
    echo "Keeping the existing /etc/apt/sources.list.d/docker.sources."
  else
    local line="deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/$repo $codename stable"
    printf '$ echo "%s" | %s tee /etc/apt/sources.list.d/docker.list\n' "$line" "${SUDO:-}"
    echo "$line" | $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null
  fi
  if ! $SUDO apt-get update -qq; then
    fail "Docker's repository has no packages for $repo $codename yet. See https://docs.docker.com/engine/install/ for your release."
  fi
  run $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
}

linux_dnf() {
  local repo
  case "$ID" in
    fedora) repo=fedora ;;
    rhel) repo=rhel ;;
    *) repo=centos ;;
  esac

  say "Python 3 and Git"
  run $SUDO dnf install -y python3 git dnf-plugins-core

  say "Docker Engine from Docker's $repo repository"
  linux_remove_conflicts docker docker-client docker-client-latest docker-common docker-latest \
    docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine podman-docker
  local url="https://download.docker.com/linux/$repo/docker-ce.repo"
  # dnf5 (Fedora 41 and newer) and dnf4 spell this differently.
  run $SUDO dnf config-manager addrepo --overwrite --from-repofile="$url" 2>/dev/null ||
    run $SUDO dnf config-manager --add-repo "$url"
  run $SUDO dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
}

install_linux() {
  [ -r /etc/os-release ] || fail "no /etc/os-release; install Python 3, Git and Docker Engine by hand: https://docs.docker.com/engine/install/"
  # shellcheck disable=SC1091
  . /etc/os-release
  if [ -n "$SUDO" ] && ! command -v sudo >/dev/null 2>&1; then
    fail "sudo is not installed; run this script as root"
  fi
  case " $ID ${ID_LIKE:-} " in
    *" debian "*|*" ubuntu "*) PKG=apt; linux_apt ;;
    *" fedora "*|*" rhel "*|*" centos "*) PKG=dnf; linux_dnf ;;
    *) fail "$ID is not covered by this script. Install Python 3.9+, Git and Docker Engine by hand: https://docs.docker.com/engine/install/" ;;
  esac

  say "Start Docker and let $USER_NAME use it"
  if [ -d /run/systemd/system ]; then
    run $SUDO systemctl enable --now docker
  else
    run $SUDO service docker start
  fi
  if [ "$USER_NAME" != root ]; then
    run $SUDO usermod -aG docker "$USER_NAME"
  fi
  DOCKER="$SUDO docker"
}

# ---------------------------------------------------------------- macOS

brew_env() {
  local b
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if [ -x "$b" ]; then
      eval "$("$b" shellenv)"
      return 0
    fi
  done
  return 1
}

ensure_brew() {
  command -v brew >/dev/null 2>&1 || brew_env || true
  if ! command -v brew >/dev/null 2>&1; then
    say "Homebrew (asks for your password and installs the Xcode command line tools)"
    printf '$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"\n'
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew_env || fail "Homebrew did not install; see https://brew.sh"
  fi
}

add_cli_plugin_dir() {
  # Homebrew's docker-buildx and docker-compose live outside Docker's default plugin folder.
  local dir="$1"
  printf '$ add %s to cliPluginsExtraDirs in ~/.docker/config.json\n' "$dir"
  mkdir -p "$HOME/.docker"
  python3 - "$HOME/.docker/config.json" "$dir" <<'EOF'
import json, os, sys
path, folder = sys.argv[1], sys.argv[2]
config = {}
if os.path.exists(path):
    with open(path, encoding='utf-8') as f:
        text = f.read().strip()
    config = json.loads(text) if text else {}
dirs = config.setdefault('cliPluginsExtraDirs', [])
if folder not in dirs:
    dirs.append(folder)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
        f.write('\n')
EOF
}

install_macos() {
  if ! python_ok || ! command -v git >/dev/null 2>&1 || { ! docker_ok && [ "$DESKTOP" = 0 ]; } ||
     { [ "$DESKTOP" = 1 ] && [ ! -d /Applications/Docker.app ]; }; then
    ensure_brew
  fi

  say "Python 3 and Git"
  if python_ok && command -v git >/dev/null 2>&1; then
    echo "Already installed: $(python3 --version), $(git --version)"
  else
    run brew install python git
  fi

  say "Docker"
  if docker_ok; then
    echo "Docker already works here ($(docker version -f '{{.Server.Os}}/{{.Server.Arch}} {{.Server.Version}}' 2>/dev/null)); keeping it."
  elif [ "$DESKTOP" = 1 ]; then
    [ -d /Applications/Docker.app ] || run brew install --cask docker-desktop
    run open -a Docker
    echo "Docker Desktop is starting. Accept its first-run screens, then give it at least 4 GB of memory"
    echo "(Settings > Resources) and run this script again to pull the image."
    CHECK_DOCKER=0
  elif [ -d /Applications/OrbStack.app ] || [ -d /Applications/Docker.app ]; then
    echo "OrbStack or Docker Desktop is installed but not running. Start it, then run this script again."
    CHECK_DOCKER=0
  else
    run brew install docker docker-buildx docker-compose colima
    add_cli_plugin_dir "$(brew --prefix)/lib/docker/cli-plugins"
    if colima status >/dev/null 2>&1; then
      echo "Colima is already running."
    else
      # 4 GB of memory for the simulator; vz is Apple's own virtualization (macOS 13 or newer).
      local vm=()
      [ "$(sw_vers -productVersion | cut -d. -f1)" -ge 13 ] && vm=(--vm-type vz)
      run colima start --cpu 2 --memory 4 --disk 40 ${vm[@]+"${vm[@]}"}
    fi
    echo "After a restart, run  colima start  before the lab (or  brew services start colima  to start it at login)."
  fi
  DOCKER=docker
}

# ---------------------------------------------------------------- main

USER_NAME=${SUDO_USER:-$(id -un)}
DOCKER=docker
case "$(uname -s)" in
  Linux) install_linux ;;
  Darwin) install_macos ;;
  MINGW*|MSYS*|CYGWIN*) fail "this is Windows: run scripts/install-windows.ps1 in PowerShell instead" ;;
  *) fail "$(uname -s) is not covered by this script" ;;
esac

say "Check"
python3 --version
git --version
if [ "$CHECK_DOCKER" = 1 ]; then
  $DOCKER version -f 'Docker Engine {{.Server.Version}} ({{.Server.Os}}/{{.Server.Arch}})'
  $DOCKER buildx version
  $DOCKER compose version
fi
if [ "$CHECK_DOCKER" = 1 ] && [ "$PULL" = 1 ]; then
  say "Station image (about 1.2 GB)"
  # shellcheck disable=SC2086
  run $DOCKER pull "$IMAGE"
fi

say "Done"
if [ "$(uname -s)" = Linux ] && [ "$USER_NAME" != root ]; then
  echo "Log out and back in (or restart) so $USER_NAME can use docker without sudo."
fi
echo "Next, in the workshop folder:  bash lab/00-check.sh"
echo "No workshop folder yet:  git clone https://github.com/ATR-Lab/agentic-robotics-workshop"
