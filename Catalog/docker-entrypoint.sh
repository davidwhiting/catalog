#!/usr/bin/env bash

## Having issues with environment variables in docker
## Hard coding values in for the moment

set -e
export H2O_WAVE_ADDRESS="http://127.0.0.1:10101"
#printf '\n$ ( cd %s && ./waved -listen ":%s" & )\n\n' "${H2O_WAVE_PATH}" "${H2O_WAVE_PORT}"

#printf '\n$ (cd "${H2O_WAVE_PATH}" && ./waved -listen ":10101" &)'
#(cd "${H2O_WAVE_PATH}" && ./waved -listen ":10101" &)

printf '\n$ (cd "${H2O_WAVE_PATH}" && ./waved -listen ":10101" &)'
(cd $HOME/wave/wave-1.1.1-linux-amd64 && ./waved -listen ":10101" &)

sleep 3

#printf '\n$ $VENV/bin/wave run --no-reload --no-autostart %s\n\n' "$PYTHON_MODULE"

printf '\n$ exec $HOME/venv/bin/wave run --no-reload --no-autostart app'
exec $HOME/venv/bin/wave run --no-reload --no-autostart app
