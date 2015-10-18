# encoding: utf-8

def tb(message=None):
    import traceback
    import sys
    if message:
        print message

    traceback.print_stack(file=sys.stdout)

