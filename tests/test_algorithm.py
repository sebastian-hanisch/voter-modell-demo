"""Einheiten des Kerns an Mini-Instanzen mit von Hand gerechneten Werten (DEMO-PLAYBOOK §1b)."""

import numpy as np
import pytest

import vot_algorithm as A
import vot_constants as C
from conftest import make_adj


def _state(n, ones):
    return sum(1 << i for i in ones)


# --- Netze ----------------------------------------------------------------------------------------------------------------------------------------


def test_largest_component_induced_adj_and_csr():
    adj = make_adj(6, [(0, 1), (1, 2), (3, 4)])
    assert A.largest_component(adj) == [0, 1, 2] and A.largest_component(make_adj(4, [(0, 1), (2, 3)])) == [0, 1] and A.largest_component(()) == []
    assert A.induced_adj(adj, [2, 1, 0]) == ((1,), (0, 2), (1,))                                  # neue Nummern = Position: Pfad in umgekehrter Nummerierung
    offsets, flat, rows, deg = A.csr(make_adj(3, [(0, 1), (1, 2)]))
    assert offsets.tolist() == [0, 1, 3, 4] and flat.tolist() == [1, 0, 2, 1] and rows.tolist() == [0, 1, 1, 2] and deg.tolist() == [1, 2, 1]


# --- Paare und Schritte ------------------------------------------------------------------------------------------------------------------------


def test_pair_probabilities_of_the_path_by_hand(path3):
    third, sixth = 1 / 3, 1 / 6
    assert A.pair_probabilities(path3, A.NODE) == pytest.approx({(0, 1): third, (1, 0): sixth, (1, 2): sixth, (2, 1): third})
    assert A.pair_probabilities(path3, A.EDGE) == pytest.approx({(0, 1): 0.25, (1, 0): 0.25, (1, 2): 0.25, (2, 1): 0.25})
    assert A.pair_probabilities(path3, A.INVASION) == pytest.approx({(1, 0): third, (0, 1): sixth, (2, 1): sixth, (1, 2): third})
    for rule in A.RULES:
        assert sum(A.pair_probabilities(path3, rule).values()) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        A.pair_probabilities(path3, "gibt es nicht")


def test_draw_pairs_are_edges_with_the_right_orientation(path3, rng):
    graph = A.csr(path3)
    for rule in A.RULES:
        t, s = A.draw_pairs(graph, rule, rng, 500)
        assert len(t) == len(s) == 500 and all(int(b) in path3[int(a)] for a, b in zip(t, s))      # jedes Paar ist eine Partnerschaft
    t, s = A.draw_pairs(graph, A.NODE, np.random.default_rng(3), 4000)
    assert set(zip(t.tolist(), s.tolist())) == {(0, 1), (1, 0), (1, 2), (2, 1)}
    with pytest.raises(ValueError):
        A.draw_pairs(graph, "gibt es nicht", rng, 3)


def test_draw_pairs_are_deterministic_per_seed(path3):
    graph = A.csr(path3)
    one = A.draw_pairs(graph, A.INVASION, np.random.default_rng(5), 50)
    two = A.draw_pairs(graph, A.INVASION, np.random.default_rng(5), 50)
    assert one[0].tolist() == two[0].tolist() and one[1].tolist() == two[1].tolist()


# --- Gewinnwahrscheinlichkeit ---------------------------------------------------------------------------------------------------------------------


def test_weights_and_win_probability_by_hand(pair2, triangle, path3, star5):
    assert A.weights(path3, A.NODE).tolist() == [1, 2, 1] and A.weights(path3, A.EDGE).tolist() == [1, 1, 1] and A.weights(path3, A.INVASION).tolist() == [1.0, 0.5, 1.0]
    assert [A.win_probability(path3, [0], r) for r in A.RULES] == pytest.approx([1 / 4, 1 / 3, 2 / 5])
    assert [A.win_probability(star5, [0], r) for r in A.RULES] == pytest.approx([1 / 2, 1 / 5, 1 / 17])
    assert [A.win_probability(triangle, [1], r) for r in A.RULES] == pytest.approx([1 / 3] * 3)
    assert [A.win_probability(pair2, [0], r) for r in A.RULES] == pytest.approx([1 / 2] * 3)
    assert A.win_probability(star5, [], A.NODE) == 0.0 and A.win_probability(star5, range(5), A.INVASION) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        A.weights(path3, "gibt es nicht")


def test_a_regular_network_gives_every_rule_the_same_share():
    cycle = make_adj(8, [(i, (i + 1) % 8) for i in range(8)])
    for ones in ([0], [0, 1, 2], [1, 4, 6, 7]):
        assert [A.win_probability(cycle, ones, r) for r in A.RULES] == pytest.approx([len(ones) / 8] * 3)


def test_degroot_formula_and_iteration_agree_on_the_path(path3):
    assert A.degroot_formula(path3, [1, 0, 0]) == 0.25 and A.degroot_formula(path3, [0, 1, 0]) == 0.5
    assert A.degroot_value(path3, [1, 0, 0]) == pytest.approx(0.25, abs=1e-8)
    assert A.degroot_value(path3, [1, 1, 1]) == 1.0 and A.degroot_value(path3, [0, 0, 0]) == 0.0


# --- Exakte Kette -------------------------------------------------------------------------------------------------------------------------------


def test_exact_chain_of_two_nodes_and_the_triangle_by_hand(pair2, triangle):
    for rule in A.RULES:
        win, time = A.absorption(pair2, rule)
        assert win.tolist() == [0.0, 0.5, 0.5, 1.0] and time.tolist() == [0.0, 1.0, 1.0, 0.0]            # ein Schritt führt in den Konsens
        win, time = A.absorption(triangle, rule)
        assert win[_state(3, [0])] == pytest.approx(1 / 3) and time[_state(3, [0])] == pytest.approx(3.0)  # T = 1 + ⅔ T
        assert win[_state(3, [0, 1])] == pytest.approx(2 / 3) and time[_state(3, [0, 1])] == pytest.approx(3.0)


def test_exact_chain_of_the_path_by_hand(path3):
    start = _state(3, [0])
    wins, times = [], []
    for rule in A.RULES:
        win, time = A.absorption(path3, rule)
        wins.append(win[start])
        times.append(time[start])
    assert wins == pytest.approx([1 / 4, 1 / 3, 2 / 5]) and times == pytest.approx([3.0, 4.0, 6.0])


def test_exact_chain_rows_sum_to_one_and_consensus_states_stay(path3):
    for rule in A.RULES:
        p = A.exact_chain(path3, rule)
        assert p.shape == (8, 8) and np.allclose(p.sum(axis=1), 1.0) and p[0, 0] == 1.0 and p[7, 7] == 1.0
    with pytest.raises(ValueError):
        A.exact_chain(make_adj(A.EXACT_LIMIT + 1, [(i, i + 1) for i in range(A.EXACT_LIMIT)]), A.NODE)


# --- Simulation -----------------------------------------------------------------------------------------------------------------------------------


def test_simulate_reaches_a_consensus_and_records_the_history(path3):
    out = A.simulate(path3, [1, 0, 0], A.NODE, np.random.default_rng(1), 10_000)
    assert out["converged"] and out["winner"] in (0, 1) and out["steps"] >= 1 and len(out["ones"]) == out["steps"] + 1 and out["ones"][0] == 1
    assert out["ones"][-1] in (0, 3) and set(out["x"]) == {out["winner"]} and out["frames"][out["steps"]] == out["x"]
    assert all(abs(a - b) <= 1 for a, b in zip(out["ones"], out["ones"][1:]))                      # je Schritt ändert sich die Zahl der Einsen um höchstens 1
    assert all(0 < v < 3 for v in out["ones"][:-1])                                                # vorher nie Konsens


def test_simulate_is_deterministic_and_lean_without_record(path3):
    one = A.simulate(path3, [1, 0, 0], A.EDGE, np.random.default_rng(9), 10_000)
    two = A.simulate(path3, [1, 0, 0], A.EDGE, np.random.default_rng(9), 10_000)
    assert one["steps"] == two["steps"] and one["winner"] == two["winner"] and one["ones"] == two["ones"]
    lean = A.simulate(path3, [1, 0, 0], A.EDGE, np.random.default_rng(9), 10_000, record=False)
    assert lean["ones"] is None and lean["steps"] == one["steps"] and lean["winner"] == one["winner"]


def test_simulate_with_a_consensus_start_stops_at_once(triangle, rng):
    for start, winner in (([0, 0, 0], 0), ([1, 1, 1], 1)):
        out = A.simulate(triangle, start, A.NODE, rng, 100)
        assert out["steps"] == 0 and out["winner"] == winner and out["converged"] and out["ones"] == [sum(start)]


def test_simulate_stops_at_the_step_limit(path3, rng):
    out = A.simulate(path3, [1, 0, 0], A.NODE, rng, 1)
    assert out["steps"] == 1 and (out["converged"] or out["winner"] is None)
    long_path = make_adj(40, [(i, i + 1) for i in range(39)])
    capped = A.simulate(long_path, [1] * 20 + [0] * 20, A.NODE, np.random.default_rng(2), 30)
    assert capped["steps"] == 30 and not capped["converged"] and capped["winner"] is None and len(capped["ones"]) == 31


def test_simulate_keeps_only_the_wanted_frames(path3):
    wanted = [0, 2, 5]
    out = A.simulate(path3, [1, 0, 0], A.NODE, np.random.default_rng(4), 10_000, frames=wanted)
    assert set(out["frames"]) <= {0, 2, 5, out["steps"]} and 0 in out["frames"] and out["frames"][0] == [1, 0, 0]
    assert all(s <= out["steps"] for s in out["frames"])


def test_frame_schedule_is_sorted_unique_and_bounded():
    sched = A.frame_schedule(5000, 120)
    assert sched == sorted(set(sched)) and sched[0] == 0 and sched[1] == 1 and sched[-1] == 5000 and len(sched) <= 125
    assert A.frame_schedule(0, 10) == [0] and A.frame_schedule(3, 120) == [0, 1, 2, 3]


# --- Konsenszeit und Anfangsverteilungen ----------------------------------------------------------------------------------------------------------


def test_degree_moments_and_the_predicted_sweeps_by_hand(star5, triangle):
    assert A.degree_moments(triangle) == (2.0, 4.0) and A.predicted_sweeps(triangle) == pytest.approx(3 * 4 / 4)
    mu1, mu2 = A.degree_moments(star5)                                                             # Grade 4, 1, 1, 1, 1
    assert mu1 == pytest.approx(8 / 5) and mu2 == pytest.approx(20 / 5) and A.predicted_sweeps(star5) == pytest.approx(5 * (8 / 5) ** 2 / 4)


def test_initial_state_by_mode(star5):
    rng = np.random.default_rng(3)
    half = A.initial_state(C.M_HALF, star5, rng)
    assert half.sum() == 2 and any(not np.array_equal(half, A.initial_state(C.M_HALF, star5, np.random.default_rng(seed))) for seed in range(4, 12)) and half.tolist() == A.initial_state(C.M_HALF, star5, np.random.default_rng(3)).tolist()
    assert A.initial_state(C.M_HUBS, star5, rng, k=1).tolist() == [1, 0, 0, 0, 0] and A.initial_state(C.M_HUBS, star5, rng, k=3).tolist() == [1, 1, 1, 0, 0]
    assert A.initial_state(C.M_HUBS, star5, rng, k=99).tolist() == [1, 1, 1, 1, 0]                 # höchstens n - 1: es bleibt ein Gegner
    assert A.initial_state(C.M_RIM, star5, rng).tolist() == [0, 1, 1, 0, 0]                        # n // 2 = 2 mit den wenigsten Partnern: Blätter 1 und 2
    single = A.initial_state(C.M_SINGLE, star5, rng)
    assert single.sum() == 1
    with pytest.raises(ValueError):
        A.initial_state("unbekannt", star5, rng)


# --- Lücken der Mutationsprüfung -----------------------------------------------------------------------------------------------------------------


def test_degroot_value_stops_after_exactly_the_given_number_of_steps(path3):
    assert A.degroot_value(path3, [1, 0, 0], max_steps=0) == pytest.approx(1 / 3)                  # kein Schritt: Mittel der Anfangsverteilung
    assert A.degroot_value(path3, [1, 0, 0], max_steps=1) == pytest.approx(0.25)                   # ein Schritt mit s = ½: (1, 0, 0) → (½, ¼, 0)
    assert A.degroot_value(path3, [1, 0, 0], max_steps=2) == pytest.approx((0.375 + 0.25 + 0.125) / 3)


def test_exact_chain_limit_is_inclusive(monkeypatch):
    monkeypatch.setattr(A, "EXACT_LIMIT", 4)
    four = make_adj(4, [(0, 1), (1, 2), (2, 3)])
    assert A.exact_chain(four, A.NODE).shape == (16, 16)                                           # genau n = Grenze ist erlaubt
    with pytest.raises(ValueError):
        A.exact_chain(make_adj(5, [(i, i + 1) for i in range(4)]), A.NODE)
