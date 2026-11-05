#!/usr/bin/env bash
# Lab step 03 (replay). Usage: bash lab/03-replay.sh [run|doctor|help] - see lab/README.md.
here=${BASH_SOURCE[0]%/*}; [ "$here" = "${BASH_SOURCE[0]}" ] && here=.
source "$here/common.sh"
lab_main 03 "$@"
