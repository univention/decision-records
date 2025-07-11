#!/usr/bin/python3

import sys

print("print to stdout, default prio")
print("<1>print to stdout, prio 1")
print("<3>print to stdout, prio 3")
print("<4>print to stdout, prio 4")
print("print to stderr, default prio", file=sys.stderr)
print("<1>print to stderr, prio 1", file=sys.stderr)
print("<3>print to stderr, prio 3", file=sys.stderr)
print("<4>print to stderr, prio 4", file=sys.stderr)
