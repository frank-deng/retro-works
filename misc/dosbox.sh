#!/bin/bash

DOSBOX_EXEC=dosbox-x
PIDFILE='/var/tmp/dosbox-x.pid'
if [[ -f ${PIDFILE} ]]; then
  ps -p $(cat "${PIDFILE}") &>/dev/null
  if [[ 0 == $? ]]; then
    echo "An instance of ${DOSBOX_EXEC} is already running.";
    exit 1;
  fi;
fi;

"${DOSBOX_EXEC}" &
PID=$!;
echo -n "${PID}" > "${PIDFILE}"
wait "${PID}";
rm "${PIDFILE}"

