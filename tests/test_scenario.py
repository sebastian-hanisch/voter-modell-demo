"""Netze: gültige Netze, Determinismus (auch über Prozesse), Positionen, größte Gruppe, Startmengen und kleine Zufallsnetze."""

import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import vot_algorithm as A
import vot_constants as C
import vot_evaluation as ev
import vot_scenario as S

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("typ", C.ALL_TYPES)
@pytest.mark.parametrize("n,c", [(C.N_MIN, C.C_MIN), (C.N_MIN, C.C_MAX), (C.DEFAULT_N, C.DEFAULT_C), (C.N_MAX, C.C_MAX)])
def test_every_corner_gives_a_valid_network(typ, n, c):
    inst = S.make_instance(typ, n, c, 35)
    assert inst.n >= 2 and len(inst.pos) == inst.n
    for x, y in inst.pos:
        assert math.isfinite(x) and math.isfinite(y) and -1e-9 <= x <= 1 + 1e-9 and -1e-9 <= y <= 1 + 1e-9
    for a, nb in enumerate(inst.adj):
        assert list(nb) == sorted(set(nb)) and a not in nb
        for b in nb:
            assert a in inst.adj[b]


def test_instances_are_deterministic_per_seed_and_differ_between_seeds():
    a = S.make_instance(C.T_COMMUNITIES, 80, 6, 5)
    assert a.adj == S.make_instance(C.T_COMMUNITIES, 80, 6, 5).adj and a.pos == S.make_instance(C.T_COMMUNITIES, 80, 6, 5).pos
    assert S.make_instance(C.T_COMMUNITIES, 80, 6, 6, layout=False).adj != a.adj


def test_network_run_and_start_are_independent_of_the_hash_seed_of_the_process():
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import hashlib, vot_scenario as S, vot_constants as C, vot_evaluation as E;"
            "h = hashlib.sha256();"
            "[h.update(repr(S.make_instance(t, 60, 5, 7, layout=False).adj).encode()) for t in C.ALL_TYPES];"
            "[h.update(repr((E.analyse(E.Settings(t, 60, 5, 7, r, m)).x0.tolist(), E.analyse(E.Settings(t, 60, 5, 7, r, m)).run['steps'], E.analyse(E.Settings(t, 60, 5, 7, r, m)).winner)).encode()) for t in C.ALL_TYPES for r in C.RULES for m in C.MODES];"
            "print(h.hexdigest())")
    outs = []
    for hashseed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        outs.append(subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", code, str(ROOT)], capture_output=True, text=True, env=env, check=True).stdout.strip())
    assert outs[0] == outs[1] and len(outs[0]) == 64


def test_layout_false_skips_the_force_layout_and_unknown_type_raises():
    inst = S.make_instance(C.T_RANDOM, 60, 4, 1, layout=False)
    assert set(inst.pos) == {(0.5, 0.5)}
    with pytest.raises(ValueError):
        S.make_instance("gibt es nicht", 60, 4, 1)


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_network_is_the_connected_largest_component(typ):
    adj = ev.network(typ, 90, 3, 11)
    assert len(adj) >= 2 and min(len(a) for a in adj) >= 1 and len(A.largest_component(adj)) == len(adj)
    for a, nb in enumerate(adj):
        assert all(a in adj[b] for b in nb)


def test_start_sets_are_hubs_and_the_rim_half():
    adj = ev.network(C.T_POWER, 80, 6, 3)
    deg = np.array([len(a) for a in adj])
    hubs, rim = ev.start_set("hubs", adj), ev.start_set("rim", adj)
    assert len(hubs) == C.HUBS_K and deg[hubs].min() >= deg[[i for i in range(len(adj)) if i not in hubs]].max()
    assert len(rim) == len(adj) // 2 and deg[rim].max() <= deg[[i for i in range(len(adj)) if i not in rim]].min()
    assert hubs == [int(i) for i in np.flatnonzero(A.initial_state(C.M_HUBS, adj, None, C.HUBS_K))]


@pytest.mark.parametrize("n,m", [(C.EXACT_SMALL_N, C.EXACT_SMALL_M), (C.EXACT_N10, C.EXACT_M10), (5, 4), (6, 15)])
def test_small_network_is_connected_has_the_requested_size_and_is_deterministic(n, m):
    for seed in range(100000, 100006):
        adj = ev.small_network(seed, n, m)
        assert len(adj) == n and sum(len(a) for a in adj) == 2 * m and len(A.largest_component(adj)) == n
        assert all(list(nb) == sorted(set(nb)) and i not in nb for i, nb in enumerate(adj))
        assert ev.small_network(seed, n, m) == adj
    assert ev.small_network(100000, 8, 11) != ev.small_network(100001, 8, 11)
