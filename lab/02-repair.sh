#!/usr/bin/env bash
# Lab step 02 (repair). Usage: bash lab/02-repair.sh [run|doctor|help] - see lab/README.md.
here=${BASH_SOURCE[0]%/*}; [ "$here" = "${BASH_SOURCE[0]}" ] && here=.
source "$here/common.sh"
lab_main 02 "$@"
