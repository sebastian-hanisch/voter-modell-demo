"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt, wofür es benannt ist."""

import pytest

import vot_algorithm as A
import vot_constants as C
import vot_evaluation as ev
import vot_presets as P


def _settings(name):
    return ev.Settings(**C.PRESETS[name])


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert p["netztyp"] in C.ALL_TYPES and C.N_MIN <= p["n"] <= C.N_MAX and C.C_MIN <= p["c"] <= C.C_MAX and 0 <= p["seed"] <= C.SEED_MAX, name
        assert p["rule"] in C.RULES and p["mode"] in C.MODES, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[C.DEFAULT_PRESET_NAME]) == ev.Settings()
    assert next(iter(C.PRESETS)) == C.DEFAULT_PRESET_NAME


def test_setting_specs_cover_every_preset_key_and_defaults_match():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for key, state_key in P.PRESET_KEYS.items():
        assert P.SETTING_SPECS[state_key].default == C.PRESETS[C.DEFAULT_PRESET_NAME][key], key


def test_every_preset_differs_from_the_default_in_something_besides_the_network_type():
    default = C.PRESETS[C.DEFAULT_PRESET_NAME]
    for name, p in C.PRESETS.items():
        if name != C.DEFAULT_PRESET_NAME:
            assert any(p[k] != default[k] for k in p if k != "netztyp"), name


def test_the_core_and_the_constants_agree_on_rule_and_mode_names():
    assert C.RULES == A.RULES and set(C.RULE_LABEL) == set(C.RULES) == set(C.RULE_HELP) == set(C.RULE_WEIGHT_TEXT)
    for mode in C.MODES:
        assert A.initial_state(mode, ev.network(C.T_RANDOM, 60, 6, 1), __import__("numpy").random.default_rng(1)).sum() >= 1
    assert set(C.MODE_HELP) == set(C.MODES)


def test_each_preset_shows_what_its_name_says():
    an = {name: ev.analyse(_settings(name)) for name in C.PRESETS}
    base = an[C.DEFAULT_PRESET_NAME]
    assert base.run["converged"] and base.ones0 == base.m // 2 and base.probs[C.R_EDGE] == pytest.approx(0.5, abs=0.02) and base.degroot == pytest.approx(base.probs[C.R_NODE], abs=1e-7)
    node, inv, edge = an["Knotenregel: die Hubs im Vorteil"], an["Invasionsregel: dieselben Hubs im Nachteil"], an["Kantenregel: nur der Anteil zählt"]
    for a in (node, inv, edge):
        assert a.inst.typ == C.T_POWER and a.ones0 == C.HUBS_K and a.probs == an["Knotenregel: die Hubs im Vorteil"].probs                 # dasselbe Netz und derselbe Start
    assert node.settings.rule == C.R_NODE and inv.settings.rule == C.R_INVASION and edge.settings.rule == C.R_EDGE
    assert node.probs[C.R_NODE] > 4 * node.probs[C.R_EDGE] / 2 and node.probs[C.R_NODE] > 2 * node.probs[C.R_EDGE] > 4 * node.probs[C.R_INVASION]            # Knoten > 2 · Kante > 4 · Invasion
    assert node.winner == 1 and inv.winner == 0 and edge.winner == 0                                                                           # der Lauf zeigt dieselbe Geschichte (per Scan gewählt)
    ring = an["Ring: die Regel ist egal"]
    assert ring.inst.typ == C.T_RING and max(ring.probs.values()) / min(ring.probs.values()) < 1.5
    rim = an["Mehrheit am Rand verliert oft"]
    assert rim.inst.typ == C.T_POWER and rim.ones0 == rim.m // 2 and rim.probs[C.R_NODE] < 0.35 < 0.5 == pytest.approx(rim.probs[C.R_EDGE], abs=0.01) and rim.probs[C.R_INVASION] > 0.6 and rim.winner == 0


def test_every_preset_runs_and_the_verdict_is_a_known_kind():
    for name in C.PRESETS:
        an = ev.analyse(_settings(name))
        kind, text = ev.verdict_main(an)
        assert kind in ("success", "info", "warning") and text
        assert set(an.run["frames"]) >= {0, an.steps} and all(len(x) == an.m for x in an.run["frames"].values())
