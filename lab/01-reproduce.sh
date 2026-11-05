#!/usr/bin/env bash
# Lab step 01 (reproduce). Usage: bash lab/01-reproduce.sh [run|doctor|help] - see lab/README.md.
here=${BASH_SOURCE[0]%/*}; [ "$here" = "${BASH_SOURCE[0]}" ] && here=.
source "$here/common.sh"
lab_main 01 "$@"
