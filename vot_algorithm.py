"""Kern: das Voter-Modell mit zwei Verfahren (0 und 1) auf ungerichteten, zusammenhängenden Netzen, mit drei Aktualisierungsregeln.

In jedem Schritt wird ein Paar (Ziel, Quelle) gezogen und das Ziel übernimmt das Verfahren der Quelle:
* Knotenregel: ein zufälliger Betrieb (Ziel) übernimmt das Verfahren eines zufälligen Partners (Quelle),
* Kantenregel: eine zufällige gerichtete Kante (Ziel, Quelle), jede der 2m gerichteten Kanten gleich wahrscheinlich,
* Invasionsregel: ein zufälliger Betrieb (Quelle) gibt sein Verfahren an einen zufälligen Partner (Ziel) weiter.
Das Netz endet sicher im Konsens (alle 0 oder alle 1). Gewinnwahrscheinlichkeit des Verfahrens 1 bei Startmenge A: Σ_A w_i / Σ w_i mit w_i = d_i (Knoten), 1 (Kante), 1/d_i (Invasion).

Netze sind Nachbarlisten `adj` (Tupel von sortierten Tupeln, Knoten 0 bis n - 1, ungerichtet). Zufall nur über `numpy.random.default_rng(Seed)`."""

import os

# Dichte Matrizen bis 1 024 × 1 024 und kleine Lösungen: ein BLAS-Thread genügt. Mehrere Threads machen kleine Lösungen auf ausgelasteten Rechnern hundertfach langsamer.
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

NODE, EDGE, INVASION = "node", "edge", "invasion"
RULES = (NODE, EDGE, INVASION)
BATCH = 4096                        # Zufallszahlen je Block; legt den Strom fest (die Messreihen hängen daran: nicht ändern, ohne sie neu zu rechnen)
EXACT_LIMIT = 12                    # Obergrenze des Kerns für die exakte Kette (4 096 Zustände); die App erlaubt weniger

# --- Netze ----------------------------------------------------------------------------------------------------------------------------------------


def largest_component(adj):
    """Knoten der größten Zusammenhangskomponente, aufsteigend (Gleichstand: die mit dem kleinsten Knoten)."""
    n = len(adj)
    seen = [False] * n
    best = []
    for s in range(n):
        if seen[s]:
            continue
        comp = [s]
        seen[s] = True
        for x in comp:
            for w in adj[x]:
                if not seen[w]:
                    seen[w] = True
                    comp.append(w)
        if len(comp) > len(best):
            best = comp
    return sorted(best)


def induced_adj(adj, nodes):
    """Nachbarlisten des Teilnetzes auf `nodes` (neue Nummern = Position in `nodes`)."""
    idx = {v: i for i, v in enumerate(nodes)}
    return tuple(tuple(sorted(idx[w] for w in adj[v] if w in idx)) for v in nodes)


def csr(adj):
    """(Anfang der Nachbarn je Betrieb, alle Nachbarn hintereinander, Betrieb je Eintrag, Grad): die 2m gerichteten Kanten in fester Reihenfolge."""
    deg = np.array([len(a) for a in adj], dtype=np.int64)
    offsets = np.concatenate(([0], np.cumsum(deg))).astype(np.int64)
    flat = np.array([j for a in adj for j in a], dtype=np.int64)
    rows = np.repeat(np.arange(len(adj), dtype=np.int64), deg)
    return offsets, flat, rows, deg


# --- Schritte -------------------------------------------------------------------------------------------------------------------------------------


def draw_pairs(graph, rule, rng, size):
    """`size` Paare (Ziel, Quelle): das Ziel übernimmt das Verfahren der Quelle. `graph` ist das Ergebnis von `csr`."""
    offsets, flat, rows, deg = graph
    n = len(deg)
    if rule == EDGE:
        e = rng.integers(len(flat), size=size)
        return rows[e], flat[e]
    if rule not in (NODE, INVASION):
        raise ValueError(f"unbekannte Regel: {rule}")
    i = rng.integers(n, size=size)
    u = rng.random(size)
    e = offsets[i] + np.minimum((u * deg[i]).astype(np.int64), deg[i] - 1)
    return (i, flat[e]) if rule == NODE else (flat[e], i)


def pair_probabilities(adj, rule):
    """Wahrscheinlichkeit jedes Paares (Ziel, Quelle) in einem Schritt (Summe 1)."""
    n = len(adj)
    m2 = sum(len(a) for a in adj)
    probs = {}
    for i, nb in enumerate(adj):
        for j in nb:
            if rule == NODE:
                key, p = (i, j), 1.0 / (n * len(nb))
            elif rule == EDGE:
                key, p = (i, j), 1.0 / m2
            elif rule == INVASION:
                key, p = (j, i), 1.0 / (n * len(nb))
            else:
                raise ValueError(f"unbekannte Regel: {rule}")
            probs[key] = probs.get(key, 0.0) + p
    return probs


def simulate(adj, x0, rule, rng, max_steps, frames=None, record=True):
    """Läuft bis Konsens oder `max_steps`. Rückgabe: winner (1, 0 oder None), steps, converged, ones (Zahl der Betriebe mit Verfahren 1 nach 0 bis steps Schritten, oder None ohne `record`),
    frames (Schritt -> Zustand für die Schritte aus `frames` und den letzten), x (Endzustand). Der Zufallsstrom hängt nur von Seed, Regel und Netz ab (Blöcke fester Größe)."""
    graph = csr(adj)
    x = [int(v) for v in x0]
    n = len(x)
    n1 = sum(x)
    ones = [n1] if record else None
    wanted = set(frames or ())
    kept = {0: x.copy()} if 0 in wanted else {}
    steps = 0
    while 0 < n1 < n and steps < max_steps:
        targets, sources = draw_pairs(graph, rule, rng, BATCH)
        for t, s in zip(targets.tolist(), sources.tolist()):
            steps += 1
            v = x[s]
            if x[t] != v:
                x[t] = v
                n1 += 1 if v else -1
            if record:
                ones.append(n1)
            if steps in wanted:
                kept[steps] = x.copy()
            if n1 == 0 or n1 == n or steps >= max_steps:
                break
    kept[steps] = x.copy()
    winner = 1 if n1 == n else (0 if n1 == 0 else None)
    return {"winner": winner, "steps": steps, "converged": winner is not None, "ones": ones, "frames": kept, "x": x}



def frame_schedule(max_steps, frames):
    """Schritte, deren Zustände aufgehoben werden: 0, 1, 2, … und danach geometrisch bis `max_steps` (höchstens etwa `frames` Stück)."""
    steps = {0, 1}
    steps |= {int(round(v)) for v in np.geomspace(1, max(1, max_steps), frames)}
    return sorted(s for s in steps if 0 <= s <= max_steps)


# --- Gewinnwahrscheinlichkeit ---------------------------------------------------------------------------------------------------------------------


def weights(adj, rule):
    """Gewichte w_i der Regel: Σ w_i x_i ist ein Martingal, die Gewinnwahrscheinlichkeit der Startmenge A ist Σ_A w_i / Σ w_i."""
    d = np.array([len(a) for a in adj], dtype=float)
    if rule == NODE:
        return d
    if rule == EDGE:
        return np.ones(len(adj))
    if rule == INVASION:
        return 1.0 / d
    raise ValueError(f"unbekannte Regel: {rule}")


def win_probability(adj, ones, rule):
    """Wahrscheinlichkeit, dass das Verfahren 1 gewinnt, wenn genau die Betriebe `ones` damit beginnen."""
    w = weights(adj, rule)
    return float(np.sum(w[list(ones)]) / np.sum(w))


def degroot_formula(adj, x0):
    """Konsenswert der DeGroot-Mittelung (Stück 9) zur Anfangsverteilung x0: Σ d_i x_i / Σ d_i."""
    d = np.array([len(a) for a in adj], dtype=float)
    return float(np.dot(d, np.asarray(x0, dtype=float)) / d.sum())


def degroot_value(adj, x0, s=0.5, tol=1e-9, max_steps=200_000):
    """Konsenswert der DeGroot-Mittelung durch Iteration x ← s x + (1 − s) D⁻¹ A x (unabhängiger Weg zu `degroot_formula`): Mittel des Endzustands."""
    n = len(adj)
    a = np.zeros((n, n))
    for i, nb in enumerate(adj):
        for j in nb:
            a[i, j] = 1.0
    w = s * np.eye(n) + (1.0 - s) * a / a.sum(axis=1)[:, None]
    x = np.asarray(x0, dtype=float)
    for _ in range(max_steps):
        if x.max() - x.min() < tol:
            break
        x = w @ x
    return float(np.mean(x))


# --- Exakte Kette ----------------------------------------------------------------------------------------------------------------------------------


def exact_chain(adj, rule):
    """Übergangsmatrix über alle 2^n Zustände (Bit i = Verfahren von Betrieb i); n höchstens `EXACT_LIMIT`."""
    n = len(adj)
    if n > EXACT_LIMIT:
        raise ValueError(f"exakte Kette nur bis n = {EXACT_LIMIT}")
    states = 1 << n
    p = np.zeros((states, states))
    pairs = list(pair_probabilities(adj, rule).items())
    for s in range(states):
        for (t, src), prob in pairs:
            ns = (s & ~(1 << t)) | (((s >> src) & 1) << t)
            p[s, ns] += prob
    return p


def absorption(adj, rule):
    """Je Startzustand: (Wahrscheinlichkeit, dass alle bei 1 enden; erwartete Zahl der Schritte bis zum Konsens), aus dem linearen System der absorbierenden Kette."""
    p = exact_chain(adj, rule)
    states = len(p)
    inner = np.arange(1, states - 1)
    q = p[np.ix_(inner, inner)]
    eye = np.eye(len(inner))
    win = np.zeros(states)
    win[states - 1] = 1.0
    time = np.zeros(states)
    if len(inner):
        win[inner] = np.linalg.solve(eye - q, p[inner, states - 1])
        time[inner] = np.linalg.solve(eye - q, np.ones(len(inner)))
    return win, time


# --- Konsenszeit ----------------------------------------------------------------------------------------------------------------------------------


def degree_moments(adj):
    """(μ1, μ2): erstes und zweites Moment der Gradfolge."""
    d = np.array([len(a) for a in adj], dtype=float)
    return float(d.mean()), float(np.mean(d**2))


def predicted_sweeps(adj):
    """n μ1² / μ2: die Vorhersage von Sood und Redner (2005) für die mittlere Konsenszeit der Knotenregel in Sweeps (Schritte / n) im unkorrelierten Netz, bis auf einen Faktor."""
    mu1, mu2 = degree_moments(adj)
    return len(adj) * mu1**2 / mu2


# --- Anfangsverteilungen ----------------------------------------------------------------------------------------------------------------------------


def initial_state(mode, adj, rng, k=10):
    """Anfangsverteilung als 0/1-Feld: „Zufällig die Hälfte“ (n // 2 zufällige Betriebe bei 1), „Die zehn Hubs“ (die k mit den meisten Partnern, Gleichstand: kleinere Nummer; höchstens n − 1),
    „Die Hälfte am Rand“ (die n // 2 mit den wenigsten Partnern, Gleichstand: kleinere Nummer), „Ein einzelner Betrieb“ (ein zufälliger)."""
    n = len(adj)
    deg = np.array([len(a) for a in adj])
    x = np.zeros(n, dtype=int)
    if mode == "Zufällig die Hälfte":
        x[rng.permutation(n)[: n // 2]] = 1
    elif mode == "Die zehn Hubs":
        x[np.argsort(-deg, kind="stable")[: min(k, n - 1)]] = 1
    elif mode == "Die Hälfte am Rand":
        x[np.argsort(deg, kind="stable")[: n // 2]] = 1
    elif mode == "Ein einzelner Betrieb":
        x[int(rng.integers(n))] = 1
    else:
        raise ValueError(f"unbekannter Modus: {mode}")
    return x
