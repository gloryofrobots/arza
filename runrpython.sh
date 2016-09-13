#!/usr/bin/env bash
PYTHONPATH=../pypy pypy ../pypy/rpython/bin/rpython targetarza.py --lldebug --no-backendopt --log

