#from dash import Dash, Input, Output, dcc, html, dash_table
import dash
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import psutil
import json
import numpy as np
import os

class History:
    def __init__(self, N):
        self.N = N
        self.data = [0]*self.N
        
    def init_record(self):
        self.data.pop(0)
        self.data += [0.0]
        
    def __call__(self, dat):
        self.data[-1] += dat
        
    def last(self):
        return self.data[-1]
    
    def get(self):
        return np.array(self.data)
    
class User:
    def __init__(self, N):
        self.cpu = History(N)
        self.ram = History(N)
        
    def start(self):
        self.cpu.init_record()
        self.ram.init_record()
        
class Monitor:
    def __init__(self, N, timeout):
        self.N = N
        self.users = {}
        self.xax = np.arange(N)*timeout/1e3
        
    def get_users(self):
        for u in psutil.users():
            if not u.name in self.users:
                self.users[u.name] = User(self.N)
                
    def __call__(self):
        self.get_users()
        
        for u in self.users:
            self.users[u].start()
        
        # need to keep loops separate
        for p in psutil.process_iter():
            u = p.username()
            if u in self.users:
                try:
                    self.users[u].cpu(p.cpu_percent())
                except:
                    pass
            
        for p in psutil.process_iter():
            u = p.username()
            if u in self.users:
                try:
                    self.users[u].ram(p.memory_info().rss)
                except:
                    pass
        
    def plots(self, tag, maxval, norm):
        fig1 = go.Figure(layout=go.Layout(title=go.layout.Title(text=f"{tag} usage")))
        fig2 = go.Figure(layout=go.Layout(title=go.layout.Title(text=f"{tag} usage history")))

        _labels = list(self.users.keys())
        _values = []
        for u in self.users:
            x = getattr(self.users[u], tag)
            _values += [x.last() / maxval * 100]
            fig2.add_trace(go.Scatter(x=self.xax, y=x.get() / norm, mode="lines", name=u))
        _labels += ['free']
        _values += [100.0 - sum(_values)]
        fig1.add_trace(go.Pie(labels=_labels, values=_values))

        fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        return fig1, fig2

    def graphs(self, tag, f1, f2):
        return [dcc.Graph(
            id=f"{tag}_pie",
            figure = f1,
        ), dcc.Graph(
            id=f"{tag}_history",
            figure = f2,
        )]

figure_template = go.Layout(
    font = {'color': 'white'},
    colorway = ['rgb(136,204,238)','rgb(221,204,119)'],
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)'
)


### CPU

ncpus = psutil.cpu_count()

def cpu(monitor):
    fig1, fig2 = monitor.plots('cpu', ncpus*100, ncpus)
    fig2.update_yaxes(range=[0, 100]) 
    fig3 = go.Figure(
        go.Bar(y=[p.user for p in psutil.cpu_times_percent(percpu=True)]),
        layout=go.Layout(title=go.layout.Title(text=f"cpu threads global usage"))
    )
    fig3.update_yaxes(range=[0, 100])
    fig1.update_layout(figure_template)
    fig2.update_layout(figure_template)
    fig3.update_layout(figure_template)
    return fig1, fig2, fig3

def cpu_div(monitor):
    f1, f2, f3 = cpu(monitor)
    return dash.html.Div(children = [
        dash.html.H3("CPU"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="cpu_pie",figure = f1), width=4),
            dbc.Col(dcc.Graph(id="cpu_bars", figure = f3), width=8)
        ]),
        dbc.Row(dbc.Col(dcc.Graph(id="cpu_history",figure = f2), width=12))
    ])

### RAM

GB = 1024**3
maxram = psutil.virtual_memory().total

def ram(monitor):
    fig1, fig2 = monitor.plots('ram', maxram, GB)
    fig2.update_yaxes(range=[0, maxram/GB]) 
    fig1.update_layout(figure_template)
    fig2.update_layout(figure_template)
    return fig1, fig2

def ram_div(monitor):
    f1, f2 = ram(monitor)
    return dash.html.Div(children = [
        dash.html.H3("Memory"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="ram_pie", figure = f1), width=4),
            dbc.Col(dcc.Graph(id="ram_history", figure = f2), width=8)
        ])
    ])


######

def disks():
    out = [];
    for p in configs['disks']:
        disk_info = psutil.disk_usage(p)
        out.append({'path': p, 'size': f'{disk_info.used/1024**3:.2f}'})
    return out

######

def run_pypeak(timeout, history, port):
    
    monitor = Monitor(history, timeout)

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
    app.title = "Avocado Analytics: Understand Your Avocados!"

    @app.callback(
        dash.Output("callback", "key"),
        dash.Output("cpu_pie", "figure"), 
        dash.Output("cpu_history", "figure"), 
        dash.Output("cpu_bars", "figure"), 
        dash.Output("ram_pie", "figure"), 
        dash.Output("ram_history", "figure"),     
        dash.Input("interval","n_intervals")
    )
    def callback(n):
        monitor()
        return ("mykey",) + cpu(monitor) + ram(monitor)

    app.layout = dash.html.Div(children = [
        dbc.Container([
            dash.html.H1("PyPeak", className="display-3"),
            dash.html.P("A Python program to monitor system resources",                     
                        id="callback",
                        className="lead"),
            dash.html.Hr(className="my-2")
        ], className="p-3 rounded-3"),
        dbc.Container(dbc.Col([
            cpu_div(monitor),
            dash.html.Hr(className="my-2"),
            ram_div(monitor),
        ])),
        dcc.Interval(
            id="interval",
            interval=timeout,
            n_intervals=0
        )
    ])

# if __name__ == "__main__":
    app.run_server(debug=True, port=port)
