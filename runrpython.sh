#!/usr/bin/env bash
 PYTHONPATH=../pypy pypy ../pypy/rpython/bin/rpython targetobin.py --lldebug --no-backendopt --log

