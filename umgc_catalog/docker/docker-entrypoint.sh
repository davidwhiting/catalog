#!/usr/bin/env bash

export VENV="${HOME}/venv"

set -e
export H2O_WAVE_ADDRESS="http://127.0.0.1:${H2O_WAVE_PORT}"
printf '\n$ ( cd %s && ./waved -listen ":%s" & )\n\n' "${WAVE_PATH}" "${H2O_WAVE_PORT}"
(cd "${WAVE_PATH}" && ./waved -listen ":${H2O_WAVE_PORT}" &)
sleep 3

printf '\n$ $VENV/bin/wave run --no-reload --no-autostart %s\n\n' "$PYTHON_MODULE"
exec $VENV/bin/wave run --no-reload --no-autostart "$PYTHON_MODULE"

#source $VENV/bin/activate
#exec wave run --no-reload --no-autostart "$PYTHON_MODULE"
