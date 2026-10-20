"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste und größte Regler, alle Netztypen, Regeln und Modi, Warnungen als Fehler, Obergrenze der Schritte, Abbildungen."""

import dataclasses
import warnings

import numpy as np
import pytest

import vot_algorithm as A
import vot_constants as C
import vot_evaluation as ev
import vot_visualization as V


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_every_network_type_at_the_slider_corners_runs_without_warnings(typ):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        for n, c, rule, mode in ((C.N_MIN, C.C_MIN, C.R_NODE, C.M_HALF), (C.N_MIN, C.C_MAX, C.R_EDGE, C.M_HUBS), (C.N_MAX, C.C_MAX, C.R_INVASION, C.M_RIM), (C.N_MAX, C.C_MIN, C.R_NODE, C.M_SINGLE)):
            an = ev.analyse(ev.Settings(typ, n, c, 3, rule, mode))
            assert 2 <= an.m <= an.inst.n and ev.verdict_main(an)[0] in ("success", "info", "warning")
            assert an.run["converged"] and an.winner in (0, 1) and an.steps >= 1 and len(an.run["ones"]) == an.steps + 1
            assert all(len(x) == an.m for x in an.run["frames"].values()) and an.run["frames"][an.steps] == an.run["x"]
            assert an.probs[C.R_NODE] == pytest.approx(A.win_probability(an.adj, np.flatnonzero(an.x0), A.NODE)) and 0.0 < min(an.probs.values()) <= max(an.probs.values()) < 1.0


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_many_seeds_in_the_smallest_networks_never_break_the_analysis(typ):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        for seed in range(6):
            for rule in C.RULES:
                for mode in C.MODES:
                    an = ev.analyse(ev.Settings(typ, C.N_MIN, C.C_MIN, seed, rule, mode))
                    assert an.m >= 2 and an.run["converged"] and np.isfinite(list(an.probs.values())).all()


def test_the_step_limit_is_reported_as_not_converged(monkeypatch):
    monkeypatch.setattr(C, "MAX_STEPS", 30)
    an = ev.analyse(ev.Settings(C.T_RING, 100, 4, 3, C.R_NODE, C.M_HALF))
    assert not an.run["converged"] and an.steps == 30 and an.winner is None and ev.verdict_main(an)[0] == "warning" and "Obergrenze" in ev.verdict_main(an)[1]
    assert set(an.run["frames"]) <= {0, 1, 2, 30} | set(A.frame_schedule(30, C.FRAMES))
    fig = V.build_history(an, 30)
    assert fig.data and all(ax.fixedrange for ax in (fig.layout.xaxis, fig.layout.yaxis))


def test_consensus_start_stops_at_once_and_still_has_figures():
    an = ev.analyse(ev.Settings(C.T_RANDOM, 50, 5, 3, C.R_NODE, C.M_HALF))
    flat = dataclasses.replace(an, x0=np.zeros(an.m, dtype=int), run=A.simulate(an.adj, np.zeros(an.m, dtype=int), A.NODE, np.random.default_rng(1), 100, frames=[0]))
    assert flat.steps == 0 and flat.winner == 0 and ev.verdict_main(flat)[1].startswith("Alle")
    for fig in (V.build_network(flat, 0), V.build_history(flat, 0)):
        assert fig.data and all(ax.fixedrange for ax in (fig.layout.xaxis, fig.layout.yaxis))


def test_hub_mode_never_makes_everyone_a_hub_on_tiny_networks():
    adj = ((1, 2), (0, 2), (0, 1))
    assert A.initial_state(C.M_HUBS, adj, np.random.default_rng(1), C.HUBS_K).sum() == 2 and A.initial_state(C.M_RIM, adj, np.random.default_rng(1)).sum() == 1


def test_experiments_run_on_the_smallest_networks_without_warnings():
    seeds = C.LIVE_SEEDS[:2]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        e1 = ev.rules_rows(C.N_MIN, C.C_MIN, seeds=seeds, runs=3)
        e2 = ev.exact_rows(nets=2, sim_runs=50)
        e3 = ev.time_rows(C.C_MIN, sizes=(40, 60), seeds=seeds, runs=2)
    assert len(e1) == len(C.ALL_TYPES) * 2 * 3 and len(e3) == len(C.ALL_TYPES) * 2
    for verdict in (ev.verdict_rules(e1), ev.verdict_exact(e2), ev.verdict_time(e3)):
        assert verdict[0] in ("success", "info", "warning") and verdict[1]


def test_figures_are_built_for_the_analysis_and_the_experiment_rows():
    seeds = C.LIVE_SEEDS[:2]
    for typ in (C.T_RING, C.T_GRID, C.T_COMMUNITIES):
        an = ev.analyse(ev.Settings(typ, 80, 6, 3, C.R_NODE, C.M_HUBS))
        for step in (0, max(an.run["frames"])):
            for fig in (V.build_network(an, step), V.build_history(an, step)):
                assert fig.data and all(ax.fixedrange for ax in (fig.layout.xaxis, fig.layout.yaxis))
    e1 = ev.rules_rows(C.N_MIN, 4, types=(C.T_POWER, C.T_RING), seeds=seeds, runs=3)
    e2 = ev.exact_rows(nets=2, sim_runs=50)
    e3 = ev.time_rows(4, types=(C.T_POWER, C.T_RING), sizes=(40, 60), seeds=seeds, runs=2)
    for fig in (V.build_rules(e1, "hubs"), V.build_rules(e1, "rim"), V.build_hub_rim(e2), V.build_exact_time(e2), V.build_time_ratio(e3), V.build_time_rules(e3)):
        assert fig.data and all(ax.fixedrange for ax in (fig.layout.xaxis, fig.layout.yaxis))


def test_the_network_figure_colors_follow_the_chosen_step_and_the_size_follows_the_degree():
    an = ev.analyse(ev.Settings(C.T_POWER, 60, 6, 1, C.R_NODE, C.M_HUBS))
    first, last = V.build_network(an, 0), V.build_network(an, an.steps)
    ones0 = [tr for tr in first.data if tr.name == "Verfahren 1"][0]
    assert len(ones0.x) == C.HUBS_K and [tr for tr in first.data if tr.name == "Verfahren 0"][0].x is not None
    assert {tr.name for tr in last.data if tr.name} == {f"Verfahren {an.winner}"}                    # im Konsens nur noch eine Farbe
    sizes = [s for tr in first.data if tr.name for s in tr.marker.size]
    assert max(sizes) > min(sizes)


def test_the_history_chart_is_thinned_and_keeps_the_first_and_the_last_point():
    xs, ys = V._thin(list(range(5000)))
    assert xs[0] == 0 and xs[-1] == 4999 and len(xs) <= V.MAX_POINTS + 1 and ys[0] == 0 and ys[-1] == 4999
    assert V._thin([7])[0] == [0]


def test_the_rules_chart_puts_markers_on_the_bar_centers():
    rows = ev.rules_rows(C.N_MIN, 4, types=(C.T_POWER, C.T_RING), seeds=C.LIVE_SEEDS[:2], runs=2)
    fig = V.build_rules(rows, "hubs")
    bars = [tr for tr in fig.data if tr.type == "bar"]
    marks = [tr for tr in fig.data if tr.type == "scatter"]
    assert len(bars) == len(marks) == 3 and all(list(b.x) == list(m.x) for b, m in zip(bars, marks))
    assert [tr.showlegend for tr in marks] == [True, False, False]
