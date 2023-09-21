from .pypeak import pypeak, Log

app = pypeak(Log(100, 2000))
server = app.server