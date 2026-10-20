"""Verdikte und Messhilfen an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import dataclasses
import math

import numpy as np
import pytest

import vot_algorithm as A
import vot_constants as C
import vot_evaluation as ev

NAN = float("nan")


def _an(ones0=10, m=40, rule=C.R_NODE, winner=1, steps=800, converged=True, probs=None, degroot=0.5, ones_end=None):
    """Analyse mit handgesetzten Kennzahlen auf einem echten kleinen Lauf: Gewinnchancen 0,5 / 0,25 / 0,125 (Knoten / Kante / Invasion), DeGroot-Konsens 0,5."""
    real = ev.analyse(ev.Settings(C.T_RANDOM, C.N_MIN, 4, 3))
    x0 = np.array([1] * ones0 + [0] * (m - ones0))
    history = [ones0, 20, ones_end if ones_end is not None else (m if winner == 1 else 0)]
    run = {"winner": winner, "steps": steps, "converged": converged, "ones": history, "frames": {0: x0.tolist()}, "x": [1] * m}
    return dataclasses.replace(real, nodes=tuple(range(m)), x0=x0, run=run, settings=dataclasses.replace(real.settings, rule=rule),
                               probs=probs or {C.R_NODE: 0.5, C.R_EDGE: 0.25, C.R_INVASION: 0.125}, degroot=degroot)


def test_de_pct_sci_helpers():
    assert ev.de(1.26, 1) == "1,3" and ev.de(0.9487, 3) == "0,949" and ev.de(NAN, 2) == "–" and ev.de(None) == "–" and ev.pct(0.1234, 1) == "12,3" and ev.pct(0.5) == "50" and ev.de(-1.0, 3) == "−1,000"
    assert ev.sci(3.5e-15) == "3,5 · 10⁻¹⁵" and ev.sci(0) == "0" and ev.sci(1.0e-5) == "1,0 · 10⁻⁵" and ev.sci(2.5e3) == "2,5 · 10³"


def test_main_verdict_names_chances_winner_and_the_degroot_bridge():
    kind, text = ev.verdict_main(_an())
    assert kind == "success"
    assert text == ("Verfahren 1 beginnt in 10 von 40 Betrieben; seine Gewinnchance ist bei der Knotenregel 50,0 % (alle Regeln: Knotenregel 50,0 %, Kantenregel 25,0 %, Invasionsregel 12,5 %). "
                    "Nach 800 Schritten (20,0 Sweeps) nutzen alle Betriebe Verfahren 1; das war in 50,0 % der Fälle zu erwarten, der Konsens selbst war sicher. "
                    "Der DeGroot-Konsens (Stück 9) zum selben Start ist 0,500: genau die Chance der Knotenregel. Die Regel verändert die Chance um das 4,0-Fache.")


def test_main_verdict_loser_uses_the_complementary_probability_and_the_chosen_rule():
    kind, text = ev.verdict_main(_an(rule=C.R_EDGE, winner=0))
    assert kind == "success" and "seine Gewinnchance ist bei der Kantenregel 25,0 %" in text and "nutzen alle Betriebe Verfahren 0; das war in 75,0 % der Fälle zu erwarten" in text
    kind, text = ev.verdict_main(_an(rule=C.R_INVASION, winner=1))
    assert "bei der Invasionsregel 12,5 %" in text and "das war in 12,5 % der Fälle zu erwarten" in text


def test_main_verdict_threshold_is_a_ratio_of_two_between_the_best_and_the_worst_rule():
    close = {C.R_NODE: 0.5, C.R_EDGE: 0.375, C.R_INVASION: 0.3125}
    kind, text = ev.verdict_main(_an(probs=close))
    assert kind == "info" and "Die Regel verändert" not in text
    assert ev.verdict_main(_an(probs={C.R_NODE: 0.5, C.R_EDGE: 0.25, C.R_INVASION: 0.25}))[0] == "success"                         # genau das Doppelte
    assert ev.verdict_main(_an(probs={C.R_NODE: 0.5, C.R_EDGE: 0.2501, C.R_INVASION: 0.26}))[0] == "info"
    kind, text = ev.verdict_main(_an(probs={C.R_NODE: 0.5, C.R_EDGE: 0.0, C.R_INVASION: 0.5}))                                  # eine Regel ohne Chance: unendlich viel Unterschied, kein Absturz
    assert kind == "success" and "Verfahren 1 beginnt" in text


def test_main_verdict_step_limit_is_a_warning_and_names_the_ones_left():
    kind, text = ev.verdict_main(_an(converged=False, winner=None, steps=400000, ones_end=17))
    assert kind == "warning" and text.endswith("Nach 400000 Schritten (Obergrenze) ist noch kein Konsens erreicht: 17 Betriebe nutzen Verfahren 1.")


def test_main_verdict_with_a_consensus_start_has_nothing_to_adopt():
    assert ev.verdict_main(_an(ones0=0)) == ("info", "Alle 40 Betriebe beginnen mit Verfahren 0: es gibt nichts zu übernehmen.")
    assert ev.verdict_main(_an(ones0=40)) == ("info", "Alle 40 Betriebe beginnen mit Verfahren 1: es gibt nichts zu übernehmen.")


# --- E1 bis E3 --------------------------------------------------------------------------------------------------------------------------------


def _rows(spec):
    """spec: {Netztyp: {Gruppe: (formel(3), sim(3))}} -> Zeilen wie `rules_rows`."""
    rows = []
    for typ, groups in spec.items():
        for group, (formula, sim) in groups.items():
            for rule, f, s in zip(C.RULES, formula, sim):
                rows.append({"typ": typ, "group": group, "rule": rule, "formula": f, "sim": s, "se": 0.01, "degroot": formula[0], "runs": 100, "capped": 0})
    return rows


def test_rules_verdict_names_the_biggest_spread_the_equal_types_and_the_rim():
    rows = _rows({"A": {"hubs": ((0.5, 0.25, 0.125), (0.5, 0.375, 0.125)), "rim": ((0.25, 0.5, 0.75), (0.25, 0.5, 0.75))},
                  "B": {"hubs": ((0.2, 0.2, 0.2), (0.2, 0.2, 0.2)), "rim": ((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))}})
    kind, text = ev.verdict_rules(rows)
    assert kind == "info"
    assert text == ("Haben nur die zehn Hubs Verfahren 1, gewinnt es in „A“ mit 50,0 % bei der Knotenregel, 37,5 % bei der Kantenregel und 12,5 % bei der Invasionsregel (Formeln: 50,0 / 25,0 / 12,5 %). "
                    "Kaum ein Unterschied (unter dem 1,5-Fachen) zwischen den Regeln besteht in: „B“. "
                    "Beginnt die Hälfte der Betriebe am Rand mit Verfahren 1, gewinnt sie in „A“ bei der Knotenregel nur in 25,0 % der Fälle (Formel 25,0 %), obwohl sie die Hälfte der Betriebe stellt.")
    assert ev.rule_cell(rows, "A", "rim", C.R_INVASION)["formula"] == 0.75


def test_rules_verdict_threshold_and_the_case_without_equal_types():
    edge = _rows({"A": {"hubs": ((0.75, 0.5, 0.5), (0.75, 0.5, 0.5)), "rim": ((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))}})                  # 0,75 / 0,5 = 1,5 genau: nicht mehr „kaum ein Unterschied“
    assert "In jedem Netztyp ändert die Regel die Chance um mindestens das 1,5-Fache." in ev.verdict_rules(edge)[1]
    below = _rows({"A": {"hubs": ((0.74, 0.5, 0.5), (0.74, 0.5, 0.5)), "rim": ((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))}})
    assert "besteht in: „A“." in ev.verdict_rules(below)[1] and ev.verdict_rules([])[0] == "warning"


def test_exact_verdict_names_the_deviation_hub_and_rim_and_the_time():
    res = {"dev": [{"rule": r, "max_dev": d, "nets": 10} for r, d in zip(C.RULES, (3.5e-15, 1.0e-15, 2.0e-15))],
           "hub_rim": [{"rule": r, "hub": h, "rim": m} for r, h, m in zip(C.RULES, (0.125, 0.1, 0.05), (0.375, 0.5, 0.625))],
           "time": [{"rule": r, "exact_time": 40.0, "sim_time": 41.5, "sim_se": 0.5, "exact_win": 0.5, "sim_win": 0.5, "runs": 2000} for r in C.RULES], "hub_degree": 5, "n10": 10}
    assert ev.verdict_exact(res) == ("info", "Auf 10 kleinen Netzen (8 Betriebe, 11 Partnerschaften) weicht die exakte Gewinnwahrscheinlichkeit der Kette bei jeder Startmenge um höchstens 3,5 · 10⁻¹⁵ von der Formel ab. "
                                           "Im Netz mit 10 Betrieben gewinnt ein einzelner Hub (Grad 5) mit 12,5 / 10,0 / 5,0 % (Knoten / Kante / Invasion), die fünf Betriebe mit den wenigsten Partnern mit 37,5 / 50,0 / 62,5 %. "
                                           "Erwartete Schritte bei der Knotenregel: exakt 40,0, simuliert 41,5 ± 0,5.")
    assert ev.verdict_exact({})[0] == "warning" and ev.verdict_exact({"dev": []})[0] == "warning"


def _trows(spec):
    return [{"typ": t, "n": n, "sweeps": {r: v for r in C.RULES}, "pred": 10.0, "ratio": ratio, "runs": 120} for t, vals in spec.items() for n, ratio, v in vals]


def test_time_verdict_separates_flat_from_growing_ratios_at_the_threshold():
    rows = _trows({"A": [(40, 0.75, 7.5), (80, 0.8, 8.0), (160, 0.875, 8.75)], "B": [(40, 1.0, 10.0), (80, 1.25, 12.5), (160, 1.5, 15.0)]})
    kind, text = ev.verdict_time(rows)
    assert kind == "info" and text == ("Die mittlere Konsenszeit der Knotenregel geteilt durch n μ₁² / μ₂ liegt bei n = 40, 80, 160 in „A“ bei 0,75 bis 0,88 (ungefähr konstant); "
                                       "dagegen in „B“ von 1,00 auf 1,50 (die Vorhersage trifft hier nicht).")
    on_edge = _trows({"B": [(40, 1.0, 10.0), (80, 1.25, 12.5)]})
    assert "in „B“ bei 1,00 bis 1,25 (ungefähr konstant)" in ev.verdict_time(on_edge)[1] and "dagegen" not in ev.verdict_time(on_edge)[1]
    assert ev.verdict_time(_trows({"B": [(40, 1.0, 10.0)]}))[0] == "warning" and ev.verdict_time([])[0] == "warning"
    assert ev.time_cell(rows, "B", 80)["ratio"] == 1.25


# --- Messreihen --------------------------------------------------------------------------------------------------------------------------------


def test_rules_rows_shape_and_the_orders_of_the_formulas():
    rows = ev.rules_rows(60, 6, types=(C.T_POWER, C.T_RING), seeds=C.LIVE_SEEDS[:2], runs=4)
    assert [(r["typ"], r["group"], r["rule"]) for r in rows] == [(t, g, r) for t in (C.T_POWER, C.T_RING) for g in ev.GROUPS for r in C.RULES]
    assert all(r["runs"] == 8 and r["capped"] == 0 and 0.0 <= r["sim"] <= 1.0 and 0.0 < r["formula"] < 1.0 and r["se"] > 0 for r in rows)
    hubs = [ev.rule_cell(rows, C.T_POWER, "hubs", r)["formula"] for r in C.RULES]
    rim = [ev.rule_cell(rows, C.T_POWER, "rim", r)["formula"] for r in C.RULES]
    assert hubs[0] > hubs[1] > hubs[2] and rim[0] < rim[1] < rim[2]                                  # Hubs: Knoten > Kante > Invasion; der Rand umgekehrt
    for typ in (C.T_POWER, C.T_RING):
        for group in ev.GROUPS:
            cells = [ev.rule_cell(rows, typ, group, r) for r in C.RULES]
            assert cells[0]["degroot"] == pytest.approx(cells[0]["formula"], abs=1e-6)               # DeGroot-Iteration gleich Knotenformel


def test_rules_rows_simulation_matches_the_formula_within_the_band():
    rows = ev.rules_rows(40, 6, types=(C.T_POWER,), seeds=C.LIVE_SEEDS[:2], runs=250)
    for r in rows:
        assert r["sim"] == pytest.approx(r["formula"], abs=5 * r["se"] + 0.02), (r["group"], r["rule"])


def test_exact_rows_shape_and_the_exact_values():
    res = ev.exact_rows(nets=2, sim_runs=300)
    assert [d["rule"] for d in res["dev"]] == list(C.RULES) and all(d["max_dev"] < 1e-10 and d["nets"] == 2 for d in res["dev"])
    hr = {x["rule"]: x for x in res["hub_rim"]}
    assert hr[C.R_NODE]["hub"] > hr[C.R_EDGE]["hub"] > hr[C.R_INVASION]["hub"] and hr[C.R_NODE]["rim"] < hr[C.R_EDGE]["rim"] < hr[C.R_INVASION]["rim"]
    assert res["n10"] == C.EXACT_N10 and res["hub_degree"] >= 3
    for t in res["time"]:
        assert abs(t["sim_time"] - t["exact_time"]) < 5 * t["sim_se"] and abs(t["sim_win"] - t["exact_win"]) < 0.12 and t["runs"] == 300
    assert [t["rule"] for t in res["time"]] == list(C.RULES)


def test_time_rows_shape_and_positive_values():
    rows = ev.time_rows(6, types=(C.T_RING, C.T_RANDOM), sizes=(40, 60), seeds=C.LIVE_SEEDS[:2], runs=3)
    assert [(r["typ"], r["n"]) for r in rows] == [(C.T_RING, 40), (C.T_RING, 60), (C.T_RANDOM, 40), (C.T_RANDOM, 60)]
    for r in rows:
        assert r["runs"] == 6 and r["pred"] > 0 and r["ratio"] == pytest.approx(r["sweeps"][C.R_NODE] / r["pred"]) and all(v > 0 for v in r["sweeps"].values())
    assert rows[1]["sweeps"][C.R_NODE] > rows[0]["sweeps"][C.R_NODE]                                 # größerer Ring: mehr Sweeps


def test_network_helper_and_the_small_helpers_agree_with_the_core():
    full = ev.make_instance(C.T_RANDOM, 50, 5, 3, layout=False).adj
    assert ev.network(C.T_RANDOM, 50, 5, 3) == A.induced_adj(full, A.largest_component(full))
    assert ev._rng(1, 2).integers(1000) == ev._rng(1, 2).integers(1000) and math.isnan(ev._median([])) and ev._median([3, 1, 2]) == 2.0
