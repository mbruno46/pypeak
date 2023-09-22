from .pypeak import pypeak, Log
import sys

interval = 2000
history = 100
port = 5656
base_url = None

argv = list(reversed(sys.argv))

while len(argv) > 0:
    arg = argv.pop()
    if arg in ('--interval'):
        arg = argv.pop()
        interval = int(arg)
        interval = 500 if (interval<500) else interval
    elif arg in ('--history'):
        arg = argv.pop()
        history = int(arg)
        history = 500 if (history>500) else history
    elif arg in ('--port'):
        arg = argv.pop()
        port = int(arg)
    elif arg in ('--base_url'):
        base_url = argv.pop()

app = pypeak(Log(history, interval), base_url)
app.run_server(debug=True, port=port)