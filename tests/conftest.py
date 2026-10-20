"""Gemeinsame Fixtures und Hilfen (DEMO-PLAYBOOK §1b): Mini-Instanzen, an denen jede Einheit von Hand geprüft wird."""

import os
import sys
from pathlib import Path

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):    # vor dem ersten Import von numpy (siehe vot_algorithm.py)
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402
import pytest  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def make_adj(n, pairs):
    """Nachbarlisten (Tupel von sortierten Tupeln) aus einer Kantenliste."""
    sets = [set() for _ in range(n)]
    for a, b in pairs:
        if a != b:
            sets[a].add(b)
            sets[b].add(a)
    return tuple(tuple(sorted(s)) for s in sets)


def random_connected(rng, n, extra=None):
    """Zufälliges zusammenhängendes Netz: Baum plus `extra` Zusatzkanten (Standard: n)."""
    pairs = {(i, int(rng.integers(i))) for i in range(1, n)}
    for _ in range(n if extra is None else extra):
        a, b = sorted(rng.choice(n, size=2, replace=False).tolist())
        pairs.add((a, b))
    return make_adj(n, list(pairs))


@pytest.fixture
def pair2():
    """Zwei Betriebe: ein Schritt führt in den Konsens, erwartete Schritte 1, Gewinnwahrscheinlichkeit ½."""
    return make_adj(2, [(0, 1)])


@pytest.fixture
def triangle():
    """Dreieck: Gewinnwahrscheinlichkeit eines einzelnen Betriebs ⅓ in jeder Regel, erwartete Schritte 3 (T = 1 + ⅔ T)."""
    return make_adj(3, [(0, 1), (1, 2), (0, 2)])


@pytest.fixture
def path3():
    """Pfad 0 - 1 - 2, Betrieb 0 allein bei 1: Gewinnwahrscheinlichkeit ¼ (Knoten), ⅓ (Kante), ⅖ (Invasion); erwartete Schritte 3, 4, 6."""
    return make_adj(3, [(0, 1), (1, 2)])


@pytest.fixture
def star5():
    """Stern: Mitte 0, Blätter 1 bis 4; Mitte allein bei 1: ½ (Knoten), ⅕ (Kante), 1/17 (Invasion)."""
    return make_adj(5, [(0, 1), (0, 2), (0, 3), (0, 4)])


@pytest.fixture
def rng():
    return np.random.default_rng(7)
