from .pypeak import run_pypeak
import sys

timeout = 2000
history = 100

argv = list(reversed(sys.argv))

while len(argv) > 0:
    arg = argv.pop()
    if arg in ('--timeout'):
        arg = argv.pop()
        timeout = int(arg)
        timeout = 500 if (timeout<500) else timeout
    elif arg in ('--history'):
        arg = argv.pop()
        history = int(arg)
        histtory = 500 if (history>500) else history

run_pypeak(timeout, history)