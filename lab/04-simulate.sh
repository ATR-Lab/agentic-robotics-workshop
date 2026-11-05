#!/usr/bin/env bash
# Lab step 04 (simulate). Usage: bash lab/04-simulate.sh [run|doctor|help] - see lab/README.md.
here=${BASH_SOURCE[0]%/*}; [ "$here" = "${BASH_SOURCE[0]}" ] && here=.
source "$here/common.sh"
lab_main 04 "$@"
