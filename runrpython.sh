#!/usr/bin/env bash
PYTHONPATH=../pypy pypy ../pypy/rpython/bin/rpython targetlalan.py --lldebug --no-backendopt --log

