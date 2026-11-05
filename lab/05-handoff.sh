#!/usr/bin/env bash
# Lab step 05 (handoff). Usage: bash lab/05-handoff.sh [run|doctor|help] - see lab/README.md.
here=${BASH_SOURCE[0]%/*}; [ "$here" = "${BASH_SOURCE[0]}" ] && here=.
source "$here/common.sh"
lab_main 05 "$@"
