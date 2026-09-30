#!/usr/bin/env bash
set -euo pipefail

# ========== Configurable parameters ==========
SOCK="$HOME/.np2modem.sock"
TCP_HOST="127.0.0.1"
TCP_PORT="18650"
TCPSER_SPEED="38400"
TCPSER_LOGLEVEL="4"
# Phonebook path: override with the optional 2nd argument (see usage below).
PHONEBOOK="$PWD/phonebook.txt"
# =============================

PID_DIR="${XDG_RUNTIME_DIR:-$HOME/.cache}/np2modem"
mkdir -p "$PID_DIR"

TCPSER_PID_FILE="$PID_DIR/tcpser.pid"
SOCAT_PID_FILE="$PID_DIR/socat.pid"
TCPSER_LOG="$PID_DIR/tcpser.log"
SOCAT_LOG="$PID_DIR/socat.log"

PB_ARGS=()

is_running() {
    local pidfile="$1"
    [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null
}

build_phonebook_args() {
    PB_ARGS=()

    if [ ! -f "$PHONEBOOK" ]; then
        echo "Phonebook not found at $PHONEBOOK, starting without number mappings."
        return 0
    fi

    if [ ! -r "$PHONEBOOK" ]; then
        echo "Phonebook at $PHONEBOOK is not readable, starting without number mappings."
        return 0
    fi

    # Parse with awk. Emit NUL-separated "-n" and "<number>=<host:port>" tokens.
    mapfile -d '' -t PB_ARGS < <(
        awk '
            /^[[:space:]]*#/ { next }
            /^[[:space:]]*$/ { next }
            NF < 2           { next }
            {
                gsub(/\r$/, "", $2)
                printf "-n\0%s=%s\0", $1, $2
            }
        ' "$PHONEBOOK"
    )

    local n=${#PB_ARGS[@]}
    if [ "$n" -eq 0 ]; then
        echo "Phonebook $PHONEBOOK has no valid entries."
        return 0
    fi

    echo "Loaded $((n / 2)) phonebook entries:"
    local i
    for ((i = 0; i < n; i += 2)); do
        printf '  %s -> %s\n' "${PB_ARGS[i+1]%%=*}" "${PB_ARGS[i+1]#*=}"
    done
}

start() {
    if is_running "$TCPSER_PID_FILE" || is_running "$SOCAT_PID_FILE"; then
        echo "Already running. Run: $0 stop first"
        exit 1
    fi

    rm -f "$SOCK"

    build_phonebook_args

    # Start tcpser, bound to 127.0.0.1:18650, with phonebook mappings appended.
    # Note: if tcpser does not support -i, remove -i "$TCP_HOST".
    #       if tcpser does not support -n, remove "${PB_ARGS[@]}".
    setsid bash -c '
        echo $$ > "$1"
        shift
        exec tcpser "$@"
    ' _ "$TCPSER_PID_FILE" \
      -v "$TCP_PORT" -i "$TCP_HOST" -s "$TCPSER_SPEED" -l "$TCPSER_LOGLEVEL" \
      ${PB_ARGS[@]+"${PB_ARGS[@]}"} \
      >"$TCPSER_LOG" 2>&1 &

    # Wait for tcpser to start
    for i in {1..50}; do
        if is_running "$TCPSER_PID_FILE"; then
            sleep 0.2
            break
        fi
        sleep 0.1
    done

    if ! is_running "$TCPSER_PID_FILE"; then
        echo "tcpser failed to start, check log: $TCPSER_LOG"
        exit 1
    fi

    # Start socat, bridge Unix Socket to tcpser's IP232 port
    setsid bash -c '
        echo $$ > "$1"
        exec socat UNIX-LISTEN:"$2",fork,unlink-early TCP:"$3":"$4"
    ' _ "$SOCAT_PID_FILE" "$SOCK" "$TCP_HOST" "$TCP_PORT" \
      >"$SOCAT_LOG" 2>&1 &

    # Wait for Unix Socket file to appear
    for i in {1..50}; do
        if [ -S "$SOCK" ] && is_running "$SOCAT_PID_FILE"; then
            break
        fi
        sleep 0.1
    done

    if ! is_running "$SOCAT_PID_FILE"; then
        echo "socat failed to start, check log: $SOCAT_LOG"
        stop
        exit 1
    fi

    echo "Started successfully:"
    echo "  tcpser PID: $(cat "$TCPSER_PID_FILE")  listening on $TCP_HOST:$TCP_PORT"
    echo "  socat  PID: $(cat "$SOCAT_PID_FILE")  listening on Unix Socket: $SOCK"
    echo "Point your emulator to: $SOCK"
}

stop() {
    local pid

    # Stop socat first
    if [ -f "$SOCAT_PID_FILE" ]; then
        pid="$(cat "$SOCAT_PID_FILE")"
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping socat (PID $pid)..."
            kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
            for i in {1..20}; do
                kill -0 "$pid" 2>/dev/null || break
                sleep 0.1
            done
            kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
        fi
        rm -f "$SOCAT_PID_FILE"
    fi

    # Then stop tcpser
    if [ -f "$TCPSER_PID_FILE" ]; then
        pid="$(cat "$TCPSER_PID_FILE")"
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping tcpser (PID $pid)..."
            kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
            for i in {1..20}; do
                kill -0 "$pid" 2>/dev/null || break
                sleep 0.1
            done
            kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
        fi
        rm -f "$TCPSER_PID_FILE"
    fi

    rm -f "$SOCK"
    echo "Stopped."
}

status() {
    if is_running "$TCPSER_PID_FILE"; then
        echo "tcpser is running, PID $(cat "$TCPSER_PID_FILE"), listening on $TCP_HOST:$TCP_PORT"
    else
        echo "tcpser is not running"
    fi

    if is_running "$SOCAT_PID_FILE"; then
        echo "socat  is running, PID $(cat "$SOCAT_PID_FILE"), Unix Socket: $SOCK"
    else
        echo "socat  is not running"
    fi
}

usage() {
    echo "Usage: $0 {start|stop|restart|status} [phonebook]"
    echo "  phonebook   Path to phonebook file (default: $PWD/phonebook.txt)"
}

ACTION="${1:-}"
shift 2>/dev/null || true

if [ "$#" -gt 0 ] && [ -n "${1:-}" ]; then
    PHONEBOOK="$1"
fi

case "$ACTION" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; start ;;
    status)  status ;;
    *)
        usage
        exit 1
        ;;
esac

