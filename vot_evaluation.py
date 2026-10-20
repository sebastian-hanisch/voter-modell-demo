"""Kennzahlen, Messreihen und Verdikte der Demo „Voter-Modell“. Verdikte sind reine Funktionen (Art, Text); jede Zahl im Text kommt aus der Rechnung.

Modell: zwei Verfahren (0 und 1), in jedem Schritt übernimmt ein Betrieb das Verfahren eines Partners (drei Regeln: Knoten, Kante, Invasion); das Netz endet sicher im Konsens. Ausgewertet wird die
größte zusammenhängende Gruppe. Gewinnwahrscheinlichkeiten stehen exakt als Formel und aus der exakten Kette; die Simulation bestätigt sie. Jede Messreihe mittelt über feste Netze
(`LIVE_SEEDS` in der App, `SWEEP_SEEDS` für die README-Zahlen); jede Zelle hat ihren eigenen Zufallsstrom (Seed, Zelle)."""

import math
import os
from dataclasses import dataclass

# BLAS-Threads: siehe vot_algorithm.py (muss vor dem ersten Import von numpy stehen).
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

import vot_algorithm as A
import vot_constants as C
from vot_scenario import Instance, make_instance

NAN = float("nan")
GROUPS = ("hubs", "rim")
GROUP_LABEL = {"hubs": "die zehn Hubs", "rim": "die Hälfte am Rand"}


def de(x, digits=1) -> str:
    """Dezimalzahl mit Komma (deutsche Texte); eine nicht definierte Zahl erscheint als Gedankenstrich."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def pct(x, digits=0) -> str:
    return de(100.0 * x, digits)


def sci(x) -> str:
    """Zahl als Zehnerpotenz mit einer Nachkommastelle, zum Beispiel 3,7 · 10⁻¹⁵; null bleibt 0."""
    if x == 0:
        return "0"
    mant, exp = f"{x:.1e}".split("e")
    e = int(exp)
    sup = ("⁻" if e < 0 else "") + "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(d)] for d in str(abs(e)))
    return f"{mant.replace('.', ',')} · 10{sup}"


def _rng(*parts):
    return np.random.default_rng([int(p) for p in parts])


def _median(values):
    return float(np.median(values)) if len(values) else NAN


# --- Netze --------------------------------------------------------------------------------------------------------------------------------------


def network(typ, n, c, seed):
    """Nachbarlisten der größten zusammenhängenden Gruppe des Netzes (ohne Anordnung)."""
    inst = make_instance(typ, n, c, seed, layout=False)
    return A.induced_adj(inst.adj, A.largest_component(inst.adj))


def start_set(group, adj, k=C.HUBS_K):
    """Startmenge der Gruppe: die k Hubs bzw. die Hälfte am Rand (wie `initial_state`)."""
    mode = C.M_HUBS if group == "hubs" else C.M_RIM
    return [int(i) for i in np.flatnonzero(A.initial_state(mode, adj, None, k))]


# --- Hauptanalyse -----------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    netztyp: str = C.T_RANDOM
    n: int = C.DEFAULT_N
    c: int = C.DEFAULT_C
    seed: int = C.DEFAULT_SEED
    rule: str = C.R_NODE
    mode: str = C.DEFAULT_MODE


@dataclass(frozen=True, eq=False)
class Analysis:
    inst: Instance
    settings: Settings
    nodes: tuple            # Betriebe der ausgewerteten Gruppe (Nummern im Gesamtnetz)
    adj: tuple              # Nachbarlisten der Gruppe
    x0: object              # Anfangsverteilung der Gruppe (0/1)
    run: dict               # Ergebnis von `simulate`
    probs: dict             # Regel -> Gewinnwahrscheinlichkeit des Verfahrens 1 (Formel)
    degroot: float          # Konsenswert der DeGroot-Mittelung zum selben Start (Stück 9, aus der Iteration)
    pred_sweeps: float      # n μ1² / μ2

    @property
    def m(self) -> int:
        return len(self.nodes)

    @property
    def steps(self) -> int:
        return self.run["steps"]

    @property
    def sweeps(self) -> float:
        return self.run["steps"] / self.m

    @property
    def winner(self):
        return self.run["winner"]

    @property
    def ones0(self) -> int:
        return int(np.sum(self.x0))


def analyse(settings: Settings) -> Analysis:
    inst = make_instance(settings.netztyp, settings.n, settings.c, settings.seed, layout=True)
    nodes = A.largest_component(inst.adj)
    adj = A.induced_adj(inst.adj, nodes)
    x0 = A.initial_state(settings.mode, adj, _rng(settings.seed, 2), C.HUBS_K)
    ones = [int(i) for i in np.flatnonzero(x0)]
    probs = {r: A.win_probability(adj, ones, r) for r in C.RULES}
    run = A.simulate(adj, x0, settings.rule, _rng(settings.seed, 3), C.MAX_STEPS, frames=A.frame_schedule(C.MAX_STEPS, C.FRAMES))
    return Analysis(inst, settings, tuple(nodes), adj, x0, run, probs, A.degroot_value(adj, x0), A.predicted_sweeps(adj))


def verdict_main(an: Analysis) -> tuple[str, str]:
    """Verdikt dieses Laufs: wer hat gewonnen, wie wahrscheinlich war das, und wie sehr hing es an der Regel?"""
    rule = an.settings.rule
    p = an.probs
    if an.ones0 in (0, an.m):
        return "info", f"Alle {an.m} Betriebe beginnen mit Verfahren {an.ones0 // an.m}: es gibt nichts zu übernehmen."
    chances = ", ".join(f"{C.RULE_LABEL[r]} {pct(p[r], 1)} %" for r in C.RULES)
    head = f"Verfahren 1 beginnt in {an.ones0} von {an.m} Betrieben; seine Gewinnchance ist bei der {C.RULE_LABEL[rule]} {pct(p[rule], 1)} % (alle Regeln: {chances}). "
    if not an.run["converged"]:
        return "warning", head + f"Nach {an.steps} Schritten (Obergrenze) ist noch kein Konsens erreicht: {an.run['ones'][-1]} Betriebe nutzen Verfahren 1."
    ratio = max(p.values()) / min(p.values()) if min(p.values()) > 0 else float("inf")
    won = an.winner
    luck = p[rule] if won == 1 else 1.0 - p[rule]
    text = head + f"Nach {an.steps} Schritten ({de(an.sweeps, 1)} Sweeps) nutzen alle Betriebe Verfahren {won}; das war in {pct(luck, 1)} % der Fälle zu erwarten, der Konsens selbst war sicher. "
    text += f"Der DeGroot-Konsens (Stück 9) zum selben Start ist {de(an.degroot, 3)}: genau die Chance der Knotenregel."
    if ratio >= 2.0:
        return "success", text + f" Die Regel verändert die Chance um das {de(ratio, 1)}-Fache."
    return "info", text


# --- E1: Die Regel ändert den Gewinner ------------------------------------------------------------------------------------------------------------


def rules_rows(n, c, types=C.ALL_TYPES, seeds=C.LIVE_SEEDS, runs=C.LIVE_RUNS, k=C.HUBS_K) -> list[dict]:
    """Je Netztyp, Startgruppe (die k Hubs; die Hälfte am Rand) und Regel: Gewinnwahrscheinlichkeit des Verfahrens 1 als Formel (Mittel über die festen Netze) und als Häufigkeit aus
    `runs` Läufen je Netz (alle Netze zusammen); dazu der Konsenswert der DeGroot-Mittelung (Iteration, Mittel über die Netze)."""
    rows = []
    for typ in types:
        nets = [network(typ, n, c, seed) for seed in seeds]
        for g, group in enumerate(GROUPS):
            starts = [start_set(group, adj, k) for adj in nets]
            degroot = float(np.mean([A.degroot_value(adj, [1 if i in set(s) else 0 for i in range(len(adj))]) for adj, s in zip(nets, starts)]))
            for r, rule in enumerate(C.RULES):
                wins = total = capped = 0
                for seed, adj, ones in zip(seeds, nets, starts):
                    rng = _rng(seed, 10 + g, r)
                    x0 = [1 if i in set(ones) else 0 for i in range(len(adj))]
                    for _ in range(runs):
                        out = A.simulate(adj, x0, rule, rng, C.MAX_STEPS, record=False)
                        wins += out["winner"] == 1
                        capped += not out["converged"]
                        total += 1
                formula = float(np.mean([A.win_probability(adj, ones, rule) for adj, ones in zip(nets, starts)]))
                sim = wins / total
                rows.append({"typ": typ, "group": group, "rule": rule, "formula": formula, "sim": sim, "se": math.sqrt(max(sim * (1 - sim), 1e-12) / total), "degroot": degroot, "runs": total, "capped": capped})
    return rows


def rule_cell(rows, typ, group, rule):
    return next(r for r in rows if r["typ"] == typ and r["group"] == group and r["rule"] == rule)


def verdict_rules(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E1: wo ändert die Regel den Gewinner, wo nicht? Hubs und Hälfte am Rand."""
    types = list(dict.fromkeys(r["typ"] for r in rows))
    if not rows:
        return "warning", "Keine Läufe."

    def spread(typ, group):
        vals = [rule_cell(rows, typ, group, r)["formula"] for r in C.RULES]
        return max(vals) / min(vals) if min(vals) > 0 else float("inf")

    top = max(types, key=lambda t: spread(t, "hubs"))
    cells = [rule_cell(rows, top, "hubs", r) for r in C.RULES]
    same = [t for t in types if spread(t, "hubs") < 1.5]
    low = min(types, key=lambda t: rule_cell(rows, t, "rim", C.R_NODE)["formula"])
    rim = rule_cell(rows, low, "rim", C.R_NODE)
    text = (f"Haben nur die zehn Hubs Verfahren 1, gewinnt es in „{top}“ mit {pct(cells[0]['sim'], 1)} % bei der Knotenregel, {pct(cells[1]['sim'], 1)} % bei der Kantenregel und {pct(cells[2]['sim'], 1)} % bei der Invasionsregel "
            f"(Formeln: {pct(cells[0]['formula'], 1)} / {pct(cells[1]['formula'], 1)} / {pct(cells[2]['formula'], 1)} %). ")
    text += ("Kaum ein Unterschied (unter dem 1,5-Fachen) zwischen den Regeln besteht in: " + ", ".join(f"„{t}“" for t in same) + ". ") if same else "In jedem Netztyp ändert die Regel die Chance um mindestens das 1,5-Fache. "
    text += f"Beginnt die Hälfte der Betriebe am Rand mit Verfahren 1, gewinnt sie in „{low}“ bei der Knotenregel nur in {pct(rim['sim'], 1)} % der Fälle (Formel {pct(rim['formula'], 1)} %), obwohl sie die Hälfte der Betriebe stellt."
    return "info", text


# --- E2: exakt auf kleinen Netzen ------------------------------------------------------------------------------------------------------------------


def small_network(seed, n, m):
    """Zusammenhängendes Zufallsnetz mit n Betrieben und m verschiedenen Partnerschaften (Ablehnungsverfahren). Rückgabe: Nachbarlisten."""
    rng = np.random.default_rng(int(seed))
    while True:
        pairs = set()
        while len(pairs) < m:
            a, b = sorted(rng.choice(n, size=2, replace=False).tolist())
            pairs.add((a, b))
        nb = [set() for _ in range(n)]
        for a, b in pairs:
            nb[a].add(b)
            nb[b].add(a)
        adj = tuple(tuple(sorted(s)) for s in nb)
        if len(A.largest_component(adj)) == n:
            return adj


def exact_rows(nets=C.EXACT_NETS, first_seed=100000, sim_runs=C.EXACT_SIM_RUNS) -> dict:
    """Exakte Kette auf kleinen Netzen: (1) größte Abweichung der Gewinnwahrscheinlichkeit von der Formel über alle Startmengen; (2) im Netz mit 10 Betrieben ein einzelner Hub gegen fünf Randbetriebe;
    (3) erwartete Schritte und Gewinnwahrscheinlichkeit exakt gegen Simulation (8 Betriebe, vier starten bei 1)."""
    dev = {r: 0.0 for r in C.RULES}
    for i in range(nets):
        adj = small_network(first_seed + i, C.EXACT_SMALL_N, C.EXACT_SMALL_M)
        n = len(adj)
        for rule in C.RULES:
            win, _ = A.absorption(adj, rule)
            for s in range(1, (1 << n) - 1):
                ones = [j for j in range(n) if (s >> j) & 1]
                dev[rule] = max(dev[rule], abs(win[s] - A.win_probability(adj, ones, rule)))
    big = small_network(first_seed + 3, C.EXACT_N10, C.EXACT_M10)
    deg = np.array([len(a) for a in big])
    hub = int(np.argsort(-deg, kind="stable")[0])
    rim = [int(v) for v in np.argsort(deg, kind="stable")[: C.EXACT_N10 // 2]]
    hub_rim = []
    for rule in C.RULES:
        win, _ = A.absorption(big, rule)
        hub_rim.append({"rule": rule, "hub": float(win[1 << hub]), "rim": float(win[sum(1 << v for v in rim)])})
    small = small_network(first_seed + 1, C.EXACT_SMALL_N, C.EXACT_SMALL_M)
    start = [0, 1, 2, 3]
    x0 = [1 if i in start else 0 for i in range(C.EXACT_SMALL_N)]
    index = sum(1 << i for i in start)
    times = []
    for r, rule in enumerate(C.RULES):
        win, time = A.absorption(small, rule)
        rng = _rng(first_seed, 20, r)
        out = [A.simulate(small, x0, rule, rng, C.MAX_STEPS, record=False) for _ in range(sim_runs)]
        steps = np.array([o["steps"] for o in out], dtype=float)
        times.append({"rule": rule, "exact_time": float(time[index]), "sim_time": float(steps.mean()), "sim_se": float(steps.std() / math.sqrt(len(out))), "exact_win": float(win[index]),
                      "sim_win": float(np.mean([o["winner"] == 1 for o in out])), "runs": sim_runs})
    return {"dev": [{"rule": r, "max_dev": dev[r], "nets": nets} for r in C.RULES], "hub_rim": hub_rim, "time": times, "hub_degree": int(deg[hub]), "n10": C.EXACT_N10}


def verdict_exact(res: dict) -> tuple[str, str]:
    """Verdikt zu E2: stimmen Formel und Kette, und wie stark entscheidet die Regel zwischen Hub und Rand?"""
    if not res or not res.get("dev"):
        return "warning", "Keine Rechnung."
    worst = max(d["max_dev"] for d in res["dev"])
    hr = {x["rule"]: x for x in res["hub_rim"]}
    tm = {x["rule"]: x for x in res["time"]}
    nets = res["dev"][0]["nets"]
    text = (f"Auf {nets} kleinen Netzen ({C.EXACT_SMALL_N} Betriebe, {C.EXACT_SMALL_M} Partnerschaften) weicht die exakte Gewinnwahrscheinlichkeit der Kette bei jeder Startmenge um höchstens {sci(worst)} von der Formel ab. "
            f"Im Netz mit {res['n10']} Betrieben gewinnt ein einzelner Hub (Grad {res['hub_degree']}) mit {pct(hr[C.R_NODE]['hub'], 1)} / {pct(hr[C.R_EDGE]['hub'], 1)} / {pct(hr[C.R_INVASION]['hub'], 1)} % (Knoten / Kante / Invasion), "
            f"die fünf Betriebe mit den wenigsten Partnern mit {pct(hr[C.R_NODE]['rim'], 1)} / {pct(hr[C.R_EDGE]['rim'], 1)} / {pct(hr[C.R_INVASION]['rim'], 1)} %. "
            f"Erwartete Schritte bei der Knotenregel: exakt {de(tm[C.R_NODE]['exact_time'], 1)}, simuliert {de(tm[C.R_NODE]['sim_time'], 1)} ± {de(tm[C.R_NODE]['sim_se'], 1)}.")
    return "info", text


# --- E3: Konsenszeit -------------------------------------------------------------------------------------------------------------------------------


def time_rows(c, types=C.ALL_TYPES, sizes=C.TIME_SIZES, seeds=C.LIVE_SEEDS, runs=C.TIME_RUNS_LIVE) -> list[dict]:
    """Je Netztyp und Größe: mittlere Konsenszeit in Sweeps (Schritte / n) bei zufälliger Hälfte für jede Regel, die Vorhersage n μ1² / μ2 der Knotenregel (Mittel über die Netze) und ihr Verhältnis."""
    rows = []
    for typ in types:
        for size in sizes:
            nets = [network(typ, size, c, seed) for seed in seeds]
            sweeps = {}
            for r, rule in enumerate(C.RULES):
                values = []
                for seed, adj in zip(seeds, nets):
                    rng = _rng(seed, size, 30 + r)
                    for _ in range(runs):
                        x0 = A.initial_state(C.M_HALF, adj, rng)
                        out = A.simulate(adj, x0, rule, rng, C.MAX_STEPS, record=False)
                        values.append(out["steps"] / len(adj))
                sweeps[rule] = float(np.mean(values))
            pred = float(np.mean([A.predicted_sweeps(adj) for adj in nets]))
            rows.append({"typ": typ, "n": size, "sweeps": sweeps, "pred": pred, "ratio": sweeps[C.R_NODE] / pred, "runs": runs * len(seeds)})
    return rows


def time_cell(rows, typ, n):
    return next(r for r in rows if r["typ"] == typ and r["n"] == n)


def verdict_time(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E3: wo folgt die Konsenszeit der Vorhersage n μ1² / μ2, wo nicht?"""
    types = list(dict.fromkeys(r["typ"] for r in rows))
    sizes = sorted({r["n"] for r in rows})
    if not rows or len(sizes) < 2:
        return "warning", "Zu wenige Messpunkte."
    flat, growing = [], []
    for t in types:
        ratios = [time_cell(rows, t, s)["ratio"] for s in sizes]
        (flat if max(ratios) / min(ratios) <= 1.25 else growing).append((t, ratios))
    text = f"Die mittlere Konsenszeit der Knotenregel geteilt durch n μ₁² / μ₂ liegt bei n = {', '.join(str(s) for s in sizes)} "
    if flat:
        text += "in " + "; ".join(f"„{t}“ bei {de(min(r), 2)} bis {de(max(r), 2)}" for t, r in flat) + " (ungefähr konstant)"
    if growing:
        text += ("; " if flat else "") + "dagegen in " + "; ".join(f"„{t}“ von {de(r[0], 2)} auf {de(r[-1], 2)}" for t, r in growing) + (" (die Vorhersage trifft hier nicht)" if growing else "")
    return "info", text + "."
