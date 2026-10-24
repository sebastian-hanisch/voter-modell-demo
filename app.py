"""Voter-Modell: wer gewinnt? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zehntes Stück der Reihe „Netzwerkanalyse“ und zweites des Anpassungs-Arms: statt zu mitteln (Stück 9) übernimmt jeder Betrieb das Verfahren eines zufälligen Partners. Das Netz endet sicher im
Konsens, der Gewinner ist Zufall; die Gewinnchancen sind exakt bekannt und hängen an der Aktualisierungsregel (Knoten, Kante, Invasion). Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import vot_constants as C
from vot_evaluation import (
    Settings,
    analyse,
    de,
    exact_rows,
    pct,
    rules_rows,
    sci,
    time_rows,
    verdict_exact,
    verdict_main,
    verdict_rules,
    verdict_time,
)
from vot_layout import dunkles_design, kopf_css
from vot_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from vot_visualization import build_exact_time, build_history, build_hub_rim, build_network, build_rules, build_time_ratio, build_time_rules

st.set_page_config(page_title="Voter-Modell – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _rules(n, c):
    return rules_rows(n, c)


@st.cache_data(show_spinner=False)
def _exact():
    return exact_rows()


@st.cache_data(show_spinner=False)
def _time(c):
    return time_rows(c)


def experiment(name, label, key, compute, show, hint):
    """Teure Zusatzansicht erst auf Klick; das Ergebnis bleibt nur für genau diese Einstellungen stehen (Session State)."""
    state_key = f"exp_{name}"
    if st.button(label, key=f"run_{name}", help=hint):
        with st.spinner("Rechne …"):
            result = compute()
        st.session_state[state_key] = (key, result)
    state = st.session_state.get(state_key)
    if state is None:
        st.caption(f"Noch nicht gerechnet. {hint}")
        return
    if state[0] != key:
        st.info("Die Einstellungen haben sich seit der letzten Rechnung geändert. Bitte neu starten.")
        return
    show(state[1])


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in vot_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🗳️ Voter-Modell: wer gewinnt?")
st.markdown(
    """
**Zehntes Stück** der Reihe „Netzwerkanalyse“ und zweites des **Anpassungs-Arms**: wie in Stück 9 gleichen sich die Betriebe an, aber nicht durch Mittelung, sondern durch **Übernehmen**. Zwei Verfahren konkurrieren in einem Netz von Subunternehmern und Lieferanten (zum Beispiel das alte und das neue); in jedem Schritt übernimmt ein Betrieb das Verfahren eines zufälligen Partners. Irgendwann nutzen **alle dasselbe**: der Konsens ist sicher, aber **welches Verfahren gewinnt, ist Zufall**.

Die Kernfrage: **Wer gewinnt, und wie lange dauert es?** Der Hook: **die Aktualisierungsregel ändert die Gewinnchance.** Auf demselben Netz und mit demselben Start (zum Beispiel zehn Hubs für das neue Verfahren) hängt die Gewinnchance daran, *wer* aktualisiert wird: bei der **Knotenregel** zählt ein Betrieb mit seiner Partnerzahl, bei der **Kantenregel** zählt jeder gleich, bei der **Invasionsregel** zählt er mit dem Kehrwert. Alle drei Chancen sind exakt bekannt. Dazu die Brücke zu [Stück 9](https://sebastianhanisch-meinungsbildung-demo.streamlit.app/): im Mittel macht die Knotenregel dasselbe wie die DeGroot-Mittelung (Kanten- und Invasionsregel gewichten anders), im Einzelfall ist es ein Münzwurf mit diesen Gewichten. Die Ergebnisse sind **Modellbefunde**, keine Aussagen über die Wirklichkeit.

Weiter unten: drei Experimente (**🔬**), der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert das Voter-Modell", expanded=True):
    st.markdown(
        """
1. **Zwei Verfahren:** jeder Betrieb nutzt Verfahren 0 oder 1. Am **Anfang** bestimmen Sie, wer mit 1 beginnt.
2. **Ein Schritt:** je nach **Regel** wird ein Paar (Ziel, Quelle) gezogen, und das Ziel übernimmt das Verfahren der Quelle. Hatten beide dasselbe, ändert sich nichts.
3. **Konsens:** sobald alle dasselbe nutzen, ändert sich nie wieder etwas. In einem zusammenhängenden Netz wird dieser Zustand **sicher** erreicht.
4. **Gewinnchance:** die Wahrscheinlichkeit, dass am Ende alle bei Verfahren 1 landen, ist die Summe der Gewichte der Betriebe, die mit 1 beginnen, geteilt durch die Summe aller Gewichte.
        """
    )
    st.markdown(
        """
| Regel | Wer wird gezogen? | Gewicht eines Betriebs in der Gewinnchance |
|---|---|---|
| **Knotenregel** (das klassische Voter-Modell) | ein zufälliger Betrieb übernimmt von einem zufälligen Partner | seine Zahl der Partner |
| **Kantenregel** | eine zufällige Partnerschaft, einer der beiden übernimmt vom anderen | alle gleich (jeder zählt 1) |
| **Invasionsregel** | ein zufälliger Betrieb gibt sein Verfahren an einen zufälligen Partner weiter | 1 / Zahl der Partner |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um einen Lauf zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Netz**")
    typ = st.selectbox("Netztyp", C.ALL_TYPES, key="netztyp_select", help="Welches Netz erzeugt wird.")
    n = st.slider("Betriebe n", *bounds("n_slider"), key="n_slider", help="Zahl der Betriebe (beim Gitter auf ein Quadrat gerundet; ausgewertet wird die größte zusammenhängende Gruppe).")
    c = st.slider("Partner je Betrieb c", *bounds("c_slider"), key="c_slider", help="Was c bedeutet, hängt vom Netztyp ab (siehe darunter).")
    st.caption(C.C_MEANING[typ])
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Bestimmt das Netz, die zufällige Anfangsverteilung und den Lauf.")
    st.button("🎲 Neuer Lauf", width="stretch", on_click=randomize_seed)
    st.markdown("**Voter-Modell**")
    rule = st.selectbox("Aktualisierungsregel", C.RULES, key="rule_select", format_func=C.RULE_LABEL.get, help="Wer in einem Schritt wen kopiert; die Regel bestimmt das Gewicht eines Betriebs in der Gewinnchance.")
    st.caption(C.RULE_HELP[rule])
    mode = st.selectbox("Anfangsverteilung", C.MODES, key="mode_select", help="Welche Betriebe mit Verfahren 1 beginnen; alle anderen beginnen mit Verfahren 0.")
    st.caption(C.MODE_HELP[mode])

sync_query_params({"netztyp_select": typ, "n_slider": int(n), "c_slider": int(c), "seed_input": int(seed), "rule_select": rule, "mode_select": mode})

settings = Settings(typ, int(n), int(c), int(seed), rule, mode)
with st.spinner("Lasse die Betriebe übernehmen …"):
    an = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Wer gewinnt in diesem Lauf?")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Gewinner", f"Verf. {an.winner}" if an.winner is not None else "offen", delta="Konsens" if an.winner is not None else "Obergrenze", delta_color="off")
m2.metric("Schritte", f"{an.steps}")
m3.metric("Sweeps", de(an.sweeps, 1), help="Schritte geteilt durch die Zahl der Betriebe.")
m4.metric("Chance 1", f"{pct(an.probs[rule], 0)} %", help="Gewinnchance des Verfahrens 1 bei der gewählten Regel und diesem Start (Formel).")
m5.metric("DeGroot", de(an.degroot, 3), help="Konsenswert der DeGroot-Mittelung (Stück 9) zum selben Start, aus der Iteration gerechnet: gleich der Chance der Knotenregel.")
steps = sorted(an.run["frames"])
step_key = "step_" + "_".join(str(v) for v in (typ, n, c, seed, rule, mode))
step = st.select_slider("Schritt", options=steps, value=steps[0], key=step_key, help="Blättert durch den Lauf: ganz links der Start, ganz rechts der Konsens.")
st.markdown("**Das Netz im Lauf** (Farbe: Verfahren im gewählten Schritt; Größe: Zahl der Partner)")
if an.m < an.inst.n:
    st.caption(f"Ausgewertet wird die größte zusammenhängende Gruppe mit {an.m} von {an.inst.n} Betrieben.")
st.plotly_chart(build_network(an, step), width="stretch", key="net_chart")
st.markdown("**Anteil der Betriebe mit Verfahren 1 über die Schritte**")
st.plotly_chart(build_history(an, step), width="stretch", key="hist_chart")
st.markdown("**Gewinnchance von Verfahren 1 bei diesem Start, je Regel** (exakt, Formel)")
st.markdown("| Regel | Gewicht eines Betriebs | Chance von Verfahren 1 |\n|---|---|---|\n" + "\n".join(
    f"| {'**' + C.RULE_LABEL[r] + '**' if r == rule else C.RULE_LABEL[r]} | {C.RULE_WEIGHT_TEXT[r]} | {pct(an.probs[r], 1)} % |" for r in C.RULES))

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wer gewinnt?")
kind, text = verdict_main(an)
getattr(st, kind)(text)
st.caption("Ein einzelner Lauf ist eine Ziehung: der Konsens ist sicher, der Gewinner folgt den Chancen oben. Die Experimente zählen viele Läufe.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

n_exp, c_exp = settings.n, settings.c
st.subheader("🔬 Experiment 1: Die Regel ändert die Gewinnchance")
st.caption(f"Sechs Netztypen, n = {n_exp}, c = {c_exp}: erst haben nur die zehn Hubs Verfahren 1, dann die Hälfte der Betriebe am Rand (mit den wenigsten Partnern). Balken: exakte Chance (Formel), Raute: Häufigkeit aus {C.LIVE_RUNS} Läufen je Netz und {len(C.LIVE_SEEDS)} festen Netzen.")


def show_rules(rows):
    for group, label in (("hubs", "Die zehn Hubs beginnen mit Verfahren 1"), ("rim", "Die Hälfte am Rand beginnt mit Verfahren 1")):
        st.markdown(f"**{label}**")
        st.plotly_chart(build_rules(rows, group), width="stretch", key=f"rules_chart_{group}")
    st.markdown("**Brücke zu Stück 9: DeGroot-Konsens gegen Chance der Knotenregel**")
    st.markdown("| Netztyp | Start | DeGroot-Konsens (Iteration) | Chance der Knotenregel (Formel) | Häufigkeit (Simulation) |\n|---|---|---|---|---|\n" + "\n".join(
        f"| {t} | {label} | {de(next(r for r in rows if r['typ'] == t and r['group'] == g)['degroot'], 3)} | {pct(next(r for r in rows if r['typ'] == t and r['group'] == g and r['rule'] == C.R_NODE)['formula'], 1)} % | "
        f"{pct(next(r for r in rows if r['typ'] == t and r['group'] == g and r['rule'] == C.R_NODE)['sim'], 1)} % |"
        for t in dict.fromkeys(r["typ"] for r in rows) for g, label in (("hubs", "zehn Hubs"), ("rim", "Hälfte am Rand"))))
    kind_, text_ = verdict_rules(rows)
    getattr(st, kind_)(text_)


experiment("rules", "Regeln vergleichen", (n_exp, c_exp), lambda: _rules(n_exp, c_exp), show_rules, "Rechnet 36 Zellen mit je 240 Läufen, etwa zehn Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 2: Exakt auf kleinen Netzen")
st.caption(f"{C.EXACT_NETS} kleine verbundene Zufallsnetze ({C.EXACT_SMALL_N} Betriebe, {C.EXACT_SMALL_M} Partnerschaften) und ein Netz mit {C.EXACT_N10} Betrieben: die **exakte Kette** über alle 2^n Zustände (absorbierende Markov-Kette) gegen die Formeln und gegen eine Simulation.")


def show_exact(res):
    st.markdown("**Größte Abweichung der exakten Gewinnwahrscheinlichkeit von der Formel** (über alle Startmengen)")
    st.markdown("| Regel | Abweichung |\n|---|---|\n" + "\n".join(f"| {C.RULE_LABEL[d['rule']]} | {sci(d['max_dev'])} |" for d in res["dev"]))
    st.markdown(f"**Ein einzelner Hub gegen die fünf Randbetriebe** (exakt, Netz mit {C.EXACT_N10} Betrieben)")
    st.plotly_chart(build_hub_rim(res), width="stretch", key="hubrim_chart")
    st.markdown(f"**Erwartete Schritte bis zum Konsens** (Netz mit {C.EXACT_SMALL_N} Betrieben, vier starten mit Verfahren 1; {C.EXACT_SIM_RUNS} Läufe)")
    st.plotly_chart(build_exact_time(res), width="stretch", key="exacttime_chart")
    kind_, text_ = verdict_exact(res)
    getattr(st, kind_)(text_)


experiment("exact", "Exakt rechnen", "fest", _exact, show_exact, "Löst die Kette für 10 + 1 kleine Netze und simuliert 6 000 Läufe, wenige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 3: Wie lange dauert der Konsens?")
st.caption(f"Knotenregel, zufällig die Hälfte bei 1, Netzgrößen {', '.join(str(x) for x in C.TIME_SIZES)}, c = {c_exp}; {C.TIME_RUNS_LIVE} Läufe je Netz und {len(C.LIVE_SEEDS)} feste Netze. Verglichen wird mit der Vorhersage n μ₁² / μ₂ von Sood und Redner (2005) für unkorrelierte Netze, bis auf einen Faktor.")


def show_time(rows):
    st.plotly_chart(build_time_ratio(rows), width="stretch", key="time_ratio_chart")
    st.plotly_chart(build_time_rules(rows), width="stretch", key="time_rules_chart")
    kind_, text_ = verdict_time(rows)
    getattr(st, kind_)(text_)
    st.caption("Bei wenigen Läufen streut das Verhältnis: die mittlere Konsenszeit schwankt von Netz zu Netz und von Lauf zu Lauf.")


experiment("time", "Zeit messen", c_exp, lambda: _time(c_exp), show_time, "Rechnet 18 Zellen mit je 360 Läufen bis n = 160, etwa zehn bis zwanzig Sekunden.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Zwei Verfahren, nur 0 oder 1** | Mit Meinungen auf einer Skala mittelt man statt zu übernehmen; wer nur auf ähnliche Meinungen hört, zersplittert. | Stück 9 (Mittelung), Stück 11 (begrenztes Vertrauen) |
| **Alle Betriebe gleich, kein Starrsinn** | Betriebe, die ihr Verfahren nie wechseln, verhindern den sicheren Konsens; es bleibt ein Gemisch. | Stück 9 (Friedkin–Johnsen) |
| **Gleiche Wahrscheinlichkeit je Partner** | Mit ungleichem Vertrauen ändert sich das Gewicht der Betriebe; die Formeln gelten dann nicht mehr. | – |
| **Kein spontaner Wechsel** | Wechseln Betriebe gelegentlich von selbst (Rauschen), gibt es keinen Konsens mehr, sondern eine Verteilung. | – |
| **Festes Netz** | Das Netz ändert sich nicht mit den Verfahren. Wer sich nach Gleichgesinnten umsieht, verändert die Struktur. | Stück 12 (Standortwahl) |
| **Zeitformel nur unkorreliert** | Die Vorhersage n μ₁² / μ₂ ist für Netze ohne Gradkorrelationen hergeleitet; im Gitter gilt sie nicht, im Ring weicht sie um bis zu 40 % ab (Experiment 3 misst das nur an wenigen Läufen). | – |
| **Stichproben** | Gewinnhäufigkeiten und Zeiten sind Mittel über wenige Läufe und vier feste Netze (in der README acht); die exakte Kette gibt es nur bis zehn Betriebe. | – |
| **Modellbefund** | Die Demo zeigt Verhalten im Modell, nicht die Wirkung in der Wirklichkeit. Wie weit Meinungsmodelle echte Daten treffen, ist offen (Flache u. a. 2017). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Schritt.** Mit der Zahl der Partner $d_i$, der Betriebszahl $n$ und der Kantenzahl $m$ wird ein Paar $(t, s)$ gezogen (das Ziel $t$ übernimmt das Verfahren der Quelle $s$). Bei der Knotenregel ist

$$P(t = i, s = j) = \frac{1}{n\, d_i} \qquad (j \text{ Partner von } i)$$

bei der Kantenregel jede der $2m$ gerichteten Kanten gleich wahrscheinlich,

$$P(t = i, s = j) = \frac{1}{2m}$$

und bei der Invasionsregel gibt $s = i$ an einen Partner $t = j$ weiter:

$$P(t = j, s = i) = \frac{1}{n\, d_i}$$

**Martingal.** Mit dem Zustand $x_i \in \{0, 1\}$ und den Gewichten $w_i = d_i$ (Knoten), $w_i = 1$ (Kante), $w_i = 1/d_i$ (Invasion) ist die gewichtete Summe im Erwartungswert über einen Schritt unverändert:

$$\mathbb{E}\Big[\sum_i w_i\, x_i' \,\Big|\, x\Big] = \sum_i w_i\, x_i$$

**Gewinnwahrscheinlichkeit.** Beginnt genau die Menge $A$ mit Verfahren 1, ist das Netz nach dem Konsens bei 1 mit Wahrscheinlichkeit

$$P(\text{alle bei } 1) = \frac{\sum_{i \in A} w_i}{\sum_{i} w_i}$$

Bei der Knotenregel ist das der DeGroot-Konsens zum Start $x(0) = \mathbf{1}_A$ (Stück 9): $\sum_i \pi_i x_i(0)$ mit $\pi_i = d_i / 2m$.

**Exakte Kette.** Über alle $2^n$ Zustände ist die Übergangsmatrix $P$ aus den Paarwahrscheinlichkeiten bekannt; mit der Teilmatrix $Q$ der Zustände ohne Konsens und dem Vektor $r$ der Übergänge in „alle bei 1“ gilt für die Gewinnwahrscheinlichkeit $u$ und die erwarteten Schritte $T$:

$$(I - Q)\, u = r$$

$$(I - Q)\, T = \mathbf{1}$$

**Konsenszeit** (Sood und Redner 2005). In einem Netz ohne Gradkorrelationen mit den Momenten $\mu_k$ der Gradfolge skaliert die mittlere Konsenszeit der Knotenregel wie

$$T_N \sim \frac{N\, \mu_1^{2}}{\mu_2}$$

**Literatur.**
- Clifford, P., Sudbury, A. (1973): *A model for spatial conflict.* Biometrika 60, 581–588.
- Sood, V., Redner, S. (2005): *Voter model on heterogeneous graphs.* Physical Review Letters 94, 178701.
- Antal, T., Redner, S., Sood, V. (2006): *Evolutionary dynamics on degree-heterogeneous graphs.* Physical Review Letters 96, 188104.
- Sood, V., Antal, T., Redner, S. (2008): *Voter models on heterogeneous networks.* Physical Review E 77, 041121.
- Flache, A. u. a. (2017): *Models of Social Influence: Towards the Next Frontiers.* Journal of Artificial Societies and Social Simulation 20(4).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
