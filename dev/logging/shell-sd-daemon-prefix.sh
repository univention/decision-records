#!/bin/bash

#
# To see results run after this script:
# journalctl --output verbose --output-fields MESSAGE,PRIORITY -S -1m
#

exec 2> >(systemd-cat  -t $(basename "$0"))

ulog_d () {  # log $1 to STDERR with priority 7 (Debug)
    echo "<7>$1" >&2
}
ulog_e () {  # log $1 to STDERR with priority 3 (Error)
    echo "<3>$1" >&2
}

echo "Shell-test #1 normal echo"
echo "Shell-test #2 echo to fd 2 with default prio" >&2
for L in 0 1 2 3 4 5 6 7; do
  echo "<$L>Shell-test #3 echo to fd 2 with prio $L" >&2
done
echo "Shell-test #4 echo to fd 2 and fd 1 with default prio" | tee /dev/stderr
echo "<4>Shell-test #5 echo to 2 and fd 1 with prio 4" | tee /dev/stderr

ulog_d "Shell-test: #6 using ulog_d(). This should be DEBUG"
ulog_e "Shell-test: #7 using ulog_e(). This should be ERROR"
