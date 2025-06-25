#!/bin/bash
export GIT_CONFIG_NOSYSTEM=1
export HOME=""
export GIT_CONFIG_GLOBAL=/dev/null
git "$@"
