from .pypeak import pypeak

app = pypeak(Log(100, 2000))
server = app.server