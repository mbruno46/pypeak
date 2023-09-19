from .pypeak import run_pypeak
import sys

timeout = 2000
history = 100
port = None

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
        history = 500 if (history>500) else history
    elif arg in ('--port'):
        arg = argv.pop()
        port = int(arg)

run_pypeak(timeout, history, port)