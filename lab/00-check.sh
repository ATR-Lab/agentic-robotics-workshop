#!/usr/bin/env bash
# Lab step 00 (check). Usage: bash lab/00-check.sh [run|doctor|help] - see lab/README.md.
here=${BASH_SOURCE[0]%/*}; [ "$here" = "${BASH_SOURCE[0]}" ] && here=.
source "$here/common.sh"
lab_main 00 "$@"
