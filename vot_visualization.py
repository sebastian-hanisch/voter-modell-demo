"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import vot_constants as C
from vot_evaluation import GROUP_LABEL, de

MAX_POINTS = 600          # Verlaufslinien werden auf so viele Punkte ausgedünnt


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340, bottom=10):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=bottom), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _pct_axis(fig, title):
    fig.update_yaxes(title_text=title, ticksuffix=" %", rangemode="tozero")
    return fig


def _edges(adj):
    return [(a, b) for a in range(len(adj)) for b in adj[a] if a < b]


def build_network(an, step):
    """Netz der ausgewerteten Gruppe; Farbe = Verfahren im gewählten Schritt, Größe = Zahl der Partner (Hubs sind groß)."""
    inst = an.inst
    nodes = an.nodes
    pos = inst.pos
    xs, ys = [], []
    for a, b in _edges(an.adj):
        xs += [pos[nodes[a]][0], pos[nodes[b]][0], None]
        ys += [pos[nodes[a]][1], pos[nodes[b]][1], None]
    state = an.run["frames"][step]
    scale = 0.75 if an.m > 90 else 1.0
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=0.7), hoverinfo="skip", showlegend=False))
    for value, color in ((0, C.COLOR_0), (1, C.COLOR_1)):
        idx = [i for i in range(an.m) if state[i] == value]
        if idx:
            fig.add_trace(go.Scatter(
                x=[pos[nodes[i]][0] for i in idx], y=[pos[nodes[i]][1] for i in idx], mode="markers", name=f"Verfahren {value}",
                marker=dict(size=[scale * (6.0 + 2.6 * math.sqrt(len(an.adj[i]))) for i in idx], color=color, line=dict(color="rgba(40,40,40,0.45)", width=0.5)),
                hovertext=[f"Betrieb {nodes[i]}: Verfahren {value}, {len(an.adj[i])} Partner" for i in idx], hoverinfo="text"))
    fig.add_trace(go.Scatter(x=[-0.04, 1.04], y=[-0.04, 1.04], mode="markers", marker=dict(size=1, color="rgba(0,0,0,0)"), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, autorange=True)
    fig.update_yaxes(visible=False, autorange=True, scaleanchor="x", scaleratio=1)
    fig.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.02), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _thin(values):
    """(Schritte, Werte) höchstens `MAX_POINTS` + 1 Punkte, erster und letzter bleiben."""
    n = len(values)
    stride = max(1, -(-n // MAX_POINTS))
    idx = list(range(0, n, stride))
    if idx[-1] != n - 1:
        idx.append(n - 1)
    return idx, [values[i] for i in idx]


def build_history(an, step):
    """Anteil der Betriebe mit Verfahren 1 über die Schritte; senkrechte Linie = gewählter Schritt."""
    xs, ys = _thin(an.run["ones"])
    fig = go.Figure(go.Scatter(x=xs, y=[100.0 * v / an.m for v in ys], mode="lines", line=dict(color=C.COLOR_1, width=3), name="Verfahren 1"))
    fig.add_vline(x=step, line=dict(color="rgba(120,120,120,0.9)", width=1.5, dash="dot"))
    fig.update_xaxes(title_text="Schritt")
    fig.update_yaxes(title_text="Betriebe mit Verfahren 1 (%)", range=[-2, 102], ticksuffix=" %")
    return _base(fig, height=280, bottom=50)


def build_rules(rows, group):
    """Gewinnwahrscheinlichkeit des Verfahrens 1 je Netztyp und Regel: Balken = Formel, Raute = Simulation (auf der Mitte des Balkens)."""
    types = list(dict.fromkeys(r["typ"] for r in rows))
    fig = go.Figure()
    for k, rule in enumerate(C.RULES):
        cells = [next(r for r in rows if r["typ"] == t and r["group"] == group and r["rule"] == rule) for t in types]
        xs = [i + (k - 1) * 0.28 for i in range(len(types))]
        fig.add_trace(go.Bar(x=xs, y=[100.0 * c["formula"] for c in cells], width=0.26, name=f"{C.RULE_LABEL[rule]} (Formel)", marker_color=C.RULE_COLORS[rule],
                             text=[de(100.0 * c["formula"], 1) for c in cells], textposition="inside", insidetextanchor="start", textfont=dict(color="white", size=10)))
        fig.add_trace(go.Scatter(x=xs, y=[100.0 * c["sim"] for c in cells], mode="markers", name="Simulation", marker=dict(symbol="diamond-open", size=10, color="rgba(30,30,30,0.9)", line=dict(width=2)),
                                 showlegend=k == 0, hovertext=[f"{C.RULE_LABEL[rule]}: {de(100.0 * c['sim'], 1)} % ({c['runs']} Läufe)" for c in cells], hoverinfo="text"))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(tickvals=list(range(len(types))), ticktext=types, tickangle=-20)
    _pct_axis(fig, f"Gewinnchance von Verfahren 1: {GROUP_LABEL[group]}")
    return _base(fig, height=400, bottom=120)


def build_hub_rim(res):
    """Exakt im Netz mit 10 Betrieben: ein einzelner Hub gegen fünf Randbetriebe, je Regel (Balken in Prozent)."""
    rules = [x["rule"] for x in res["hub_rim"]]
    fig = go.Figure()
    for key, label, color in (("hub", "ein einzelner Hub", C.COLOR_1), ("rim", "die fünf Betriebe mit den wenigsten Partnern", C.COLOR_0)):
        ys = [100.0 * x[key] for x in res["hub_rim"]]
        fig.add_trace(go.Bar(x=[C.RULE_LABEL[r] for r in rules], y=ys, name=label, marker_color=color, text=[de(y, 1) for y in ys], textposition="outside"))
    fig.update_layout(barmode="group")
    _pct_axis(fig, "Gewinnchance von Verfahren 1 (exakt)")
    return _base(fig, height=320, bottom=60)


def build_exact_time(res):
    """Erwartete Schritte bis zum Konsens im Netz mit 8 Betrieben: exakt (Balken) gegen Simulation (Raute mit Standardfehler)."""
    labels = [C.RULE_LABEL[x["rule"]] for x in res["time"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[x["exact_time"] for x in res["time"]], name="exakt (Kette)", marker_color=[C.RULE_COLORS[x["rule"]] for x in res["time"]],
                         text=[de(x["exact_time"], 1) for x in res["time"]], textposition="outside"))
    fig.add_trace(go.Scatter(x=labels, y=[x["sim_time"] for x in res["time"]], mode="markers", name="Simulation", error_y=dict(type="data", array=[x["sim_se"] for x in res["time"]], visible=True),
                             marker=dict(symbol="diamond-open", size=10, color="rgba(30,30,30,0.9)", line=dict(width=2))))
    fig.update_yaxes(title_text="erwartete Schritte", rangemode="tozero")
    return _base(fig, height=320, bottom=60)


def build_time_ratio(rows):
    """Gemessene mittlere Konsenszeit der Knotenregel durch die Vorhersage n μ₁² / μ₂ über die Netzgröße, je Netztyp (waagerecht heißt: die Formel trifft bis auf einen Faktor)."""
    fig = go.Figure()
    sizes = sorted({r["n"] for r in rows})
    for typ in dict.fromkeys(r["typ"] for r in rows):
        mine = sorted((r for r in rows if r["typ"] == typ), key=lambda r: r["n"])
        fig.add_trace(go.Scatter(x=[r["n"] for r in mine], y=[r["ratio"] for r in mine], mode="lines+markers", name=typ, line=dict(color=C.TYPE_COLORS[typ], width=3)))
    fig.update_xaxes(title_text="Betriebe n", tickvals=sizes, type="log")
    fig.update_yaxes(title_text="Konsenszeit / (n μ₁² / μ₂)", rangemode="tozero")
    return _base(fig, height=340, bottom=60)


def build_time_rules(rows):
    """Mittlere Konsenszeit in Sweeps bei der größten Netzgröße, je Netztyp und Regel."""
    size = max(r["n"] for r in rows)
    mine = [r for r in rows if r["n"] == size]
    fig = go.Figure()
    for rule in C.RULES:
        ys = [r["sweeps"][rule] for r in mine]
        fig.add_trace(go.Bar(x=[r["typ"] for r in mine], y=ys, name=C.RULE_LABEL[rule], marker_color=C.RULE_COLORS[rule], text=[de(y, 0) for y in ys], textposition="outside"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(tickangle=-20)
    fig.update_yaxes(title_text=f"Sweeps bis zum Konsens (n = {size})", rangemode="tozero")
    return _base(fig, height=360, bottom=110)
