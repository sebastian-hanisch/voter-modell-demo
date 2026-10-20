"""Orakel-Tests (ORACLE-PLAYBOOK): der Kern wird gegen unabhängige Rechenwege geprüft, nicht gegen sich selbst.

* Gewinnwahrscheinlichkeit: die exakte Kette (Übergangsmatrix, lineares System) gegen die drei Formeln Σ w_i / Σ w auf über 100 Zufallsnetzen und allen Startmengen.
* Martingal: die Übergangsmatrix lässt Σ w_i x_i im Erwartungswert unverändert (P · W = W über alle Zustände).
* Gezogene Paare: die Häufigkeit der gezogenen Paare gegen die Wahrscheinlichkeiten `pair_probabilities`.
* Zeit und Gewinner: Simulation gegen die exakte erwartete Zeit und Gewinnwahrscheinlichkeit (Band über Standardfehler).
* Brücke zu Stück 9: Gewinnwahrscheinlichkeit der Knotenregel gegen die Iteration der DeGroot-Mittelung.
"""

import numpy as np
import pytest

import vot_algorithm as A
from conftest import make_adj, random_connected

NETS = 110


def _nets(count=NETS, seed=21, lo=4, hi=9):
    rng = np.random.default_rng(seed)
    for _ in range(count):
        n = int(rng.integers(lo, hi + 1))
        yield rng, random_connected(rng, n, extra=int(rng.integers(0, 2 * n)))


def _bits(n):
    """Matrix der Zustände: Zeile s, Spalte i = Bit i von s."""
    return np.array([[(s >> i) & 1 for i in range(n)] for s in range(1 << n)], dtype=float)


def test_exact_win_probability_equals_the_formula_for_every_start_set_on_many_networks():
    for _, adj in _nets():
        n = len(adj)
        bits = _bits(n)
        for rule in A.RULES:
            win, _ = A.absorption(adj, rule)
            d = np.array([len(a) for a in adj], dtype=float)
            w = {A.NODE: d, A.EDGE: np.ones(n), A.INVASION: 1.0 / d}[rule]                          # unabhängig vom Kern aus den Graden gebaut
            assert np.allclose(win, bits @ w / w.sum(), atol=1e-10), (rule, adj)


def test_the_weighted_sum_is_a_martingale_of_the_chain():
    for _, adj in _nets(count=40, seed=22):
        n = len(adj)
        bits = _bits(n)
        for rule in A.RULES:
            p = A.exact_chain(adj, rule)
            w = A.weights(adj, rule)
            value = bits @ w
            assert np.allclose(p @ value, value, atol=1e-12), rule                                 # E[W(x')] = W(x) in jedem Zustand
            assert np.allclose(p.sum(axis=1), 1.0)


def test_drawn_pairs_follow_the_pair_probabilities():
    rng = np.random.default_rng(23)
    adj = random_connected(rng, 6, extra=4)
    graph = A.csr(adj)
    draws = 60_000
    for rule in A.RULES:
        t, s = A.draw_pairs(graph, rule, np.random.default_rng(24), draws)
        counts = {}
        for key in zip(t.tolist(), s.tolist()):
            counts[key] = counts.get(key, 0) + 1
        expected = A.pair_probabilities(adj, rule)
        assert set(counts) == set(expected), rule
        for key, p in expected.items():
            assert counts[key] / draws == pytest.approx(p, abs=4.5 * (p * (1 - p) / draws) ** 0.5 + 1e-4), (rule, key)


def test_simulated_time_and_winner_match_the_exact_values():
    rng = np.random.default_rng(25)
    checked = 0
    for k in range(4):
        adj = random_connected(rng, 6, extra=4)
        start = [0, 1, 2]
        x0 = [1 if i in start else 0 for i in range(6)]
        index = sum(1 << i for i in start)
        for rule in A.RULES:
            win, time = A.absorption(adj, rule)
            runs = [A.simulate(adj, x0, rule, np.random.default_rng([k, i, 7]), 100_000, record=False) for i in range(2500)]
            steps = np.array([r["steps"] for r in runs], dtype=float)
            wins = np.array([r["winner"] == 1 for r in runs], dtype=float)
            assert steps.mean() == pytest.approx(time[index], abs=4.5 * steps.std() / len(runs) ** 0.5), (k, rule)
            assert wins.mean() == pytest.approx(win[index], abs=4.5 * (win[index] * (1 - win[index]) / len(runs)) ** 0.5 + 1e-3), (k, rule)
            checked += 1
    assert checked == 12


def test_the_node_rule_win_probability_is_the_degroot_consensus():
    for rng, adj in _nets(count=30, seed=26, lo=5, hi=12):
        n = len(adj)
        ones = rng.choice(n, size=int(rng.integers(1, n)), replace=False).tolist()
        x0 = [1 if i in ones else 0 for i in range(n)]
        assert A.win_probability(adj, ones, A.NODE) == pytest.approx(A.degroot_value(adj, x0, s=0.5), abs=1e-7)
        assert A.degroot_formula(adj, x0) == pytest.approx(A.win_probability(adj, ones, A.NODE))


def test_regular_networks_make_the_rules_equal_and_irregular_ones_differ():
    cycle = make_adj(7, [(i, (i + 1) % 7) for i in range(7)])
    star = make_adj(6, [(0, i) for i in range(1, 6)])
    for ones in ([0], [2, 3]):
        values = [A.win_probability(cycle, ones, r) for r in A.RULES]
        assert max(values) - min(values) < 1e-12
    values = [A.win_probability(star, [0], r) for r in A.RULES]                                     # der Hub: Knoten ½, Kante 1/6, Invasion 1/26
    assert values == pytest.approx([1 / 2, 1 / 6, (1 / 5) / (1 / 5 + 5)]) and values[0] > values[1] > values[2]


def test_the_winner_is_always_zero_or_one_and_the_number_of_ones_changes_by_at_most_one():
    for rng, adj in _nets(count=25, seed=27, lo=5, hi=14):
        x0 = A.initial_state("Zufällig die Hälfte", adj, rng)
        for rule in A.RULES:
            out = A.simulate(adj, x0, rule, rng, 200_000)
            assert out["converged"] and out["winner"] in (0, 1) and set(out["x"]) == {out["winner"]}
            assert all(abs(a - b) <= 1 for a, b in zip(out["ones"], out["ones"][1:]))
