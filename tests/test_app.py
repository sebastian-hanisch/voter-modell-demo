"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Slider an seine Grenzen,
prüft Permalink, Netztypen, Regeln, Modi, den Schritt-Regler und alle drei Experimente; es darf kein Python-Fehler auftreten."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import vot_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
EXPERIMENTS = ("rules", "exact", "time")


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _metric(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_app_loads_without_exception():
    at = _fresh_app()
    assert [m.label for m in at.metric] == ["Gewinner", "Schritte", "Sweeps", "Chance 1", "DeGroot"]
    assert _metric(at, "Gewinner") == "Verf. 1" and _metric(at, "Schritte") == "1772" and _metric(at, "Sweeps") == "29,5" and _metric(at, "Chance 1") == "54 %" and _metric(at, "DeGroot") == "0,544"
    assert not at.error and not at.warning
    assert any(i.value.startswith("Verfahren 1 beginnt in 30 von 60 Betrieben") for i in at.info)


def test_every_preset_click_does_not_raise():
    for name in C.PRESETS:
        at = _fresh_app()
        at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])


def test_the_rule_presets_show_the_same_chances_and_the_chosen_rule_changes_the_metric():
    at = _fresh_app()
    at.sidebar.button(key="preset_Knotenregel: die Hubs im Vorteil").click().run(timeout=TIMEOUT)
    node = _metric(at, "Chance 1")
    at.sidebar.button(key="preset_Invasionsregel: dieselben Hubs im Nachteil").click().run(timeout=TIMEOUT)
    inv = _metric(at, "Chance 1")
    at.sidebar.button(key="preset_Kantenregel: nur der Anteil zählt").click().run(timeout=TIMEOUT)
    edge = _metric(at, "Chance 1")
    assert (node, edge, inv) == ("38 %", "17 %", "6 %") and _metric(at, "DeGroot") == "0,379"
    assert any("Die Regel verändert die Chance" in s.value for s in at.success)


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().sidebar.slider]
    assert labels == ["Betriebe n", "Partner je Betrieb c"], labels
    for index in range(len(labels)):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.sidebar.slider[index]
            value = slider.min if edge == "min" else slider.max
            slider.set_value(int(value)).run(timeout=TIMEOUT)
            assert not at.exception, (labels[index], edge, [str(e) for e in at.exception])


def test_all_sliders_at_their_minimum_and_all_at_their_maximum_do_not_raise():
    for edge in ("min", "max"):
        at = _fresh_app()
        for index in range(len(at.sidebar.slider)):
            slider = at.sidebar.slider[index]
            slider.set_value(int(slider.min if edge == "min" else slider.max))
        at.run(timeout=TIMEOUT)
        assert not at.exception, (edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_every_network_type_renders(typ):
    at = _fresh_app()
    at.selectbox(key="netztyp_select").set_value(typ).run(timeout=TIMEOUT)
    assert not at.exception, (typ, [str(e) for e in at.exception])


@pytest.mark.parametrize("rule", C.RULES)
@pytest.mark.parametrize("mode", C.MODES)
def test_every_rule_and_initial_distribution_renders(rule, mode):
    at = _fresh_app()
    at.selectbox(key="rule_select").set_value(rule)
    at.selectbox(key="mode_select").set_value(mode).run(timeout=TIMEOUT)
    assert not at.exception, (rule, mode, [str(e) for e in at.exception])


def test_the_step_slider_moves_through_the_frames_and_resets_with_the_settings():
    at = _fresh_app()
    slider = at.select_slider[0]
    last = int(slider.options[-1])
    assert slider.label == "Schritt" and slider.value == 0 and last == 1772
    slider.set_value(last).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == last
    at.selectbox(key="rule_select").set_value(C.R_INVASION).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == 0 and int(at.select_slider[0].options[-1]) != last       # neue Einstellungen: neuer Regler, zurück auf Schritt 0


def test_a_new_run_changes_the_seed_and_the_result():
    at = _fresh_app()
    before = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index("🎲 Neuer Lauf")].click().run(timeout=TIMEOUT)
    assert not at.exception and at.number_input(key="seed_input").value != before


def test_permalink_values_are_clamped_and_unknown_choices_ignored():
    at = AppTest.from_file(APP_PATH)
    at.query_params["n"] = "5"
    at.query_params["c"] = "99"
    at.query_params["regel"] = "gibt es nicht"
    at.query_params["start"] = "gibt es nicht"
    at.query_params["typ"] = "gibt es nicht"
    at.run(timeout=TIMEOUT)
    assert not at.exception
    assert at.slider(key="n_slider").value == C.N_MIN and at.slider(key="c_slider").value == C.C_MAX
    assert at.selectbox(key="rule_select").value == C.R_NODE and at.selectbox(key="mode_select").value == C.DEFAULT_MODE and at.selectbox(key="netztyp_select").value == C.T_RANDOM


def test_permalink_selects_type_rule_and_mode_and_the_address_mirrors_the_settings():
    at = AppTest.from_file(APP_PATH)
    at.query_params["typ"] = C.T_POWER
    at.query_params["regel"] = C.R_INVASION
    at.query_params["start"] = C.M_HUBS
    at.run(timeout=TIMEOUT)
    assert not at.exception and at.selectbox(key="netztyp_select").value == C.T_POWER and at.selectbox(key="rule_select").value == C.R_INVASION and at.selectbox(key="mode_select").value == C.M_HUBS
    assert dict(at.query_params) == {"typ": C.T_POWER, "n": "60", "c": "6", "seed": "35", "regel": C.R_INVASION, "start": C.M_HUBS}


def test_every_experiment_runs_and_is_invalidated_by_a_setting_change():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN).run(timeout=TIMEOUT)         # kleines Netz: schnell
    for name in EXPERIMENTS:
        at.button(key=f"run_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])
    texts = " ".join(x.value for x in list(at.info) + list(at.warning) + list(at.success))
    for fragment in ("Haben nur die zehn Hubs Verfahren 1", "weicht die exakte Gewinnwahrscheinlichkeit der Kette", "Die mittlere Konsenszeit der Knotenregel geteilt durch"):
        assert fragment in texts, fragment
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN + 10).run(timeout=TIMEOUT)
    assert not at.exception
    assert sum("neu starten" in i.value for i in at.info) == 1                                    # nur Experiment 1 hängt an n; die Zeit an c, die exakte Kette an nichts
    at.sidebar.slider(key="c_slider").set_value(C.C_MIN).run(timeout=TIMEOUT)
    assert not at.exception and sum("neu starten" in i.value for i in at.info) == 2               # Experiment 1 und 3 hängen an c
