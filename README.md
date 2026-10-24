# Voter-Modell: wer gewinnt? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-voter-modell-demo.streamlit.app/)** -->

Zehntes Stück der **Netzwerkanalyse-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ und zweites des **Anpassungs-Arms** (Stücke 9 bis 12): wie in der [Meinungsbildungs-Demo](https://sebastianhanisch-meinungsbildung-demo.streamlit.app/) (Stück 9) gleichen sich die Betriebe an, aber nicht durch Mittelung, sondern durch **Übernehmen**. Es gibt nur zwei Verfahren, und das Netz endet **sicher** im Konsens; der Gewinner ist ein Zufallsergebnis. Die [Kaskaden-Demo](https://sebastianhanisch-kaskaden-demo.streamlit.app/) rechnet Ausbreitung ohne Rückkehr, die [Zentralitäts-Demo](https://sebastianhanisch-centrality-demo.streamlit.app/) kennt die Gewichte, mit denen hier ein Betrieb in die Gewinnchance eingeht.

Zwei Verfahren konkurrieren in einem Netz von Subunternehmern und Lieferanten (zum Beispiel das alte und das neue). In jedem Schritt übernimmt ein Betrieb das Verfahren eines zufälligen Partners. Irgendwann nutzen alle dasselbe. Die Demo zeigt, **wer gewinnt, wie wahrscheinlich das war und wie lange es dauert**.

## Kernfrage

**Wer gewinnt, und wie lange dauert es?** Der Hook: **die Aktualisierungsregel ändert die Gewinnchance.** Auf demselben Netz und mit demselben Start (zehn Hubs für das neue Verfahren) hängt die Chance daran, *wer* aktualisiert wird: bei der **Knotenregel** zählt ein Betrieb mit seiner Partnerzahl, bei der **Kantenregel** zählt jeder gleich, bei der **Invasionsregel** mit dem Kehrwert. Alle drei Chancen sind exakt bekannt. Dazu die Brücke zu Stück 9: die Gewinnchance der Knotenregel ist der DeGroot-Konsens zum Start 0/1; bei der Knotenregel macht das Voter-Modell im Mittel dasselbe wie die Mittelung (Kanten- und Invasionsregel gewichten mit 1 bzw. 1/*d*), im Einzelfall ist es ein Münzwurf mit diesen Gewichten. Alle Ergebnisse sind **Modellbefunde**, keine Aussagen über die Wirklichkeit.

## Befunde und Korrekturen gegenüber dem Plan

- **Die drei Formeln sind exakt** (Aussage aus Sekundärquellen im Gesamtplan bestätigt): Gewinnchance der Startmenge *A* gleich Σ<sub>*A*</sub> *w*<sub>*i*</sub> / Σ *w*<sub>*i*</sub> mit *w*<sub>*i*</sub> = *d*<sub>*i*</sub> (Knoten), 1 (Kante), 1/*d*<sub>*i*</sub> (Invasion). Die exakte Kette über alle 2<sup>*n*</sup> Zustände weicht auf 10 Netzen mit 8 Betrieben bei jeder Startmenge um höchstens 1,0 · 10⁻¹⁴ ab.
- **Die Regel ändert die Gewinnchance:** haben nur die zehn Hubs Verfahren 1, gewinnt es im Potenzgesetz-Netz laut Formel mit 32,6 % (Knotenregel), 10,0 % (Kantenregel) und 2,6 % (Invasionsregel); die Simulation (1 600 Läufe) gibt 34,2 / 10,9 / 1,9 %. Auf 100 weiteren Netzen derselben Art liegt die Formel im Mittel bei 34,1 / 10,2 / 2,7 %. Im Ring (11,7 / 10,0 / 8,5 %) und im Gitter (11,5 / 10,0 / 8,2 %) ist der Unterschied klein.
- **Die Hälfte der Betriebe gewinnt nicht sicher:** beginnt die Hälfte der Betriebe am Rand mit Verfahren 1, gewinnt sie im Potenzgesetz-Netz bei der Knotenregel nur mit 26,3 % (Formel 26,6 %), bei der Kantenregel mit 49,9 % und bei der Invasionsregel mit 68,4 %. Auch eine echte Mehrheit am Rand gewinnt bei der Knotenregel nicht sicher (Nachrechnung mit der Formel im Potenzgesetz-Netz: 60 % der Betriebe 34 %, 70 % der Betriebe 42,5 %). Exakt im Netz mit 10 Betrieben: ein einzelner Hub (Grad 5) gewinnt mit 15,6 / 10,0 / 5,0 %, die fünf Betriebe mit den wenigsten Partnern mit 31,2 / 50,0 / 71,1 %.
- **Brücke zu Stück 9 (exakt):** die DeGroot-Mittelung, durch Iteration gerechnet, liefert in allen 12 Zeilen von Experiment 1 denselben Wert wie die Formel der Knotenregel (Abweichung unter 10⁻⁶): die Gewinnchance der Knotenregel ist der DeGroot-Konsens zum Start 0/1.
- **Die Simulation stimmt mit den Formeln:** in allen 36 Zellen von Experiment 1 (je 1 600 Läufe) liegt die Häufigkeit innerhalb von 3 Standardfehlern der Formel (größte Abweichung 2,5 Standardfehler mit dem Standardfehler der Simulation, 2,7 mit dem der Formel), in 2 bis 3 Zellen über zwei Standardfehlern (bei 36 Zellen erwartet man etwa zwei). Erwartete Schritte der Knotenregel im Netz mit 8 Betrieben: exakt 45,4, simuliert 45,3 ± 0,9.
- **Die Konsenszeit folgt *n* μ₁² / μ₂ nur bis auf einen Faktor und nicht überall** (Vermutung im Gesamtplan nur teilweise bestätigt): in Zufalls-, Potenzgesetz-, skalenfreien und Verbünde-Netzen liegt das Verhältnis gemessene Sweeps / Vorhersage bei *n* = 40, 80, 160, 320 zwischen 0,74 und 0,99; im Ring steigt es langsam von 1,14 auf 1,37, **im Gitter von 1,09 auf 1,79**. Die Vormessung im Einzelplan (vier Netze, *n* bis 160) hatte den Ring bei 1,08 bis 1,51 gesehen: Ring und Gitter weichen ab, der Ring weniger deutlich als vermutet.
- **Die Regel ändert auch die Zeit:** im Potenzgesetz-Netz mit *n* = 320 braucht der Konsens bei der Knotenregel 77,6 Sweeps, bei der Kantenregel 277,8 und bei der Invasionsregel 949,6; im Ring unterscheiden sich die Regeln höchstens um das 1,36-Fache.
- **Technisches:** die dichte Lösung der exakten Kette setzt wie in Stück 9 vor dem ersten Import von numpy einen BLAS-Thread.

## Modell

Netz ungerichtet und zusammenhängend (größte Gruppe), jeder Betrieb nutzt Verfahren 0 oder 1. In jedem Schritt wird ein Paar (Ziel, Quelle) gezogen und das Ziel übernimmt das Verfahren der Quelle: **Knotenregel** (klassisches Voter-Modell): ein zufälliger Betrieb übernimmt von einem zufälligen Partner, Wahrscheinlichkeit 1 / (*n* *d*<sub>*i*</sub>) je Paar; **Kantenregel:** jede der 2*m* gerichteten Kanten gleich wahrscheinlich; **Invasionsregel:** ein zufälliger Betrieb gibt sein Verfahren an einen zufälligen Partner weiter. Das Netz endet sicher im Konsens. **Gewinnchance** des Verfahrens 1 bei Startmenge *A*: Σ<sub>*A*</sub> *w*<sub>*i*</sub> / Σ *w*<sub>*i*</sub> (Martingal Σ *w*<sub>*i*</sub> *x*<sub>*i*</sub>). **Exakte Kette:** die absorbierende Markov-Kette über alle 2<sup>*n*</sup> Zustände (*n* ≤ 10 in der App) mit (*I* − *Q*) *u* = *r* und (*I* − *Q*) *T* = 1. **Konsenszeit:** Vorhersage *n* μ₁² / μ₂ der Knotenregel (Sood und Redner 2005, unkorreliertes Netz). Zeit in Schritten und in Sweeps (Schritte / *n*).

## Methodik

| Baustein | Inhalt |
|---|---|
| **Netze** | Generatoren aus `k-core-demo` (Stück 1) als Kopie: Zufallsnetz, Potenzgesetz-Netz, skalenfrei (BA), Verbünde, Ring mit Abkürzungen, Gitter |
| **Hauptansicht** | Netz mit Verfahren als Farbe, Größe = Partnerzahl, Regler „Schritt“, Verlauf des Anteils der Betriebe mit Verfahren 1, Gewinnchance je Regel, DeGroot-Konsens zum selben Start |
| **Experiment 1** | die zehn Hubs bzw. die Hälfte am Rand beginnt mit Verfahren 1: Gewinnchance als Formel und aus 200 Läufen je Netz, je Netztyp und Regel; dazu die DeGroot-Iteration |
| **Experiment 2** | exakte Kette auf 10 Netzen mit 8 Betrieben (alle Startmengen) gegen die Formeln; ein Netz mit 10 Betrieben (ein Hub gegen fünf Randbetriebe); erwartete Schritte exakt gegen 2000 Läufe |
| **Experiment 3** | Konsenszeit in Sweeps über *n* = 40, 80, 160, 320 je Netztyp und Regel (25 Läufe je Netz) gegen *n* μ₁² / μ₂ |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Netze der Messreihen: die acht festen Netze `SWEEP_SEEDS` je Zelle, *n* = 100 (Experiment 3: 40, 80, 160, 320), *c* = 6; Experiment 1 mit 200 Läufen je Netz (1 600 je Zelle), Experiment 3 mit 25 Läufen je Netz. Gewinnchancen in Prozent, Zeiten in Sweeps.

| Frage | Befund |
|---|---|
| **Stimmen die Bausteine?** | Gewinnwahrscheinlichkeit der exakten Kette gegen die Formeln auf 110 Zufallsnetzen mit 4 bis 9 Betrieben und allen Startmengen; die Übergangsmatrix lässt Σ *w*<sub>*i*</sub> *x*<sub>*i*</sub> im Erwartungswert unverändert; die gezogenen Paare folgen den Paarwahrscheinlichkeiten (60 000 Ziehungen je Regel); erwartete Zeit und Gewinner aus der Simulation gegen die Kette; Knotenregel-Formel gegen die Iteration der DeGroot-Mittelung (`tests/test_oracle_voter_modell.py`) |
| **Wer gewinnt, und mit welcher Chance?** | Tabellen zu Experiment 1 |
| **Stimmt die exakte Kette?** | Tabellen zu Experiment 2 |
| **Wie lange dauert der Konsens?** | Tabelle zu Experiment 3 |
| **Standardlauf** | 60 Betriebe, 180 Partnerschaften; Verfahren 1 beginnt in 30; Gewinnchance von Verfahren 1: Knotenregel 54,4 %, Kantenregel 50,0 %, Invasionsregel 43,1 %; DeGroot-Konsens 0,544; Lauf: Verfahren 1 gewinnt nach 1772 Schritten |
| **Preset Knotenregel: die Hubs im Vorteil** | 60 Betriebe, 161 Partnerschaften; Verfahren 1 beginnt in 10; Gewinnchance von Verfahren 1: Knotenregel 37,9 %, Kantenregel 16,7 %, Invasionsregel 5,8 %; DeGroot-Konsens 0,379; Lauf: Verfahren 1 gewinnt nach 3380 Schritten |
| **Preset Invasionsregel: dieselben Hubs im Nachteil** | 60 Betriebe, 161 Partnerschaften; Verfahren 1 beginnt in 10; Gewinnchance von Verfahren 1: Knotenregel 37,9 %, Kantenregel 16,7 %, Invasionsregel 5,8 %; DeGroot-Konsens 0,379; Lauf: Verfahren 0 gewinnt nach 3220 Schritten |
| **Preset Kantenregel: nur der Anteil zählt** | 60 Betriebe, 161 Partnerschaften; Verfahren 1 beginnt in 10; Gewinnchance von Verfahren 1: Knotenregel 37,9 %, Kantenregel 16,7 %, Invasionsregel 5,8 %; DeGroot-Konsens 0,379; Lauf: Verfahren 0 gewinnt nach 2980 Schritten |
| **Preset Ring: die Regel ändert wenig** | 60 Betriebe, 188 Partnerschaften; Verfahren 1 beginnt in 10; Gewinnchance von Verfahren 1: Knotenregel 19,4 %, Kantenregel 16,7 %, Invasionsregel 14,3 %; DeGroot-Konsens 0,194; Lauf: Verfahren 0 gewinnt nach 661 Schritten |
| **Preset Mehrheit am Rand verliert oft** | 60 Betriebe, 161 Partnerschaften; Verfahren 1 beginnt in 30; Gewinnchance von Verfahren 1: Knotenregel 28,0 %, Kantenregel 50,0 %, Invasionsregel 69,9 %; DeGroot-Konsens 0,280; Lauf: Verfahren 0 gewinnt nach 3380 Schritten |

Die Läufe in der Tabelle sind Einzelziehungen. Den Zufalls-Seed der drei Potenzgesetz-Presets mit den Hubs (`STORY_SEED`) hat die Entwicklung per Scan so gewählt, dass die Geschichte sichtbar wird (die Hubs gewinnen bei der Knotenregel und verlieren bei den anderen Regeln); der Lauf ist damit kein typischer; die Gewinnchancen in denselben Zeilen sind die Wahrscheinlichkeiten vor dem Lauf.

**Experiment 1: Gewinnchance, wenn nur die zehn Hubs mit Verfahren 1 beginnen** (Prozent; je Regel Formel und Simulation):

| Netztyp | Knoten: Formel | Simulation | Kante: Formel | Simulation | Invasion: Formel | Simulation |
|---|---|---|---|---|---|---|
| Zufallsnetz | 17,6 | 17,3 | 10,0 | 9,8 | 4,7 | 4,4 |
| Potenzgesetz-Netz | 32,6 | 34,2 | 10,0 | 10,9 | 2,6 | 1,9 |
| Skalenfreies Netz (BA) | 30,6 | 29,8 | 10,0 | 9,7 | 2,7 | 3,2 |
| Verbünde | 16,4 | 16,6 | 10,0 | 9,7 | 5,2 | 5,7 |
| Ring mit Abkürzungen | 11,7 | 11,4 | 10,0 | 12,1 | 8,5 | 9,6 |
| Gitter | 11,5 | 12,1 | 10,0 | 11,0 | 8,2 | 9,4 |

**Gewinnchance, wenn die Hälfte der Betriebe am Rand (mit den wenigsten Partnern) mit Verfahren 1 beginnt** (Prozent):

| Netztyp | Knoten: Formel | Simulation | Kante: Formel | Simulation | Invasion: Formel | Simulation |
|---|---|---|---|---|---|---|
| Zufallsnetz | 34,7 | 33,9 | 49,9 | 51,2 | 67,2 | 67,1 |
| Potenzgesetz-Netz | 26,6 | 26,3 | 49,9 | 49,9 | 68,1 | 68,4 |
| Skalenfreies Netz (BA) | 27,5 | 28,9 | 50,0 | 50,9 | 67,1 | 69,1 |
| Verbünde | 36,4 | 36,4 | 49,9 | 52,7 | 65,4 | 63,8 |
| Ring mit Abkürzungen | 47,8 | 47,1 | 50,0 | 48,1 | 52,0 | 53,5 |
| Gitter | 42,5 | 42,9 | 50,0 | 48,6 | 59,0 | 59,6 |

**Experiment 2: größte Abweichung der exakten Gewinnwahrscheinlichkeit von der Formel** (10 Netze mit 8 Betrieben, 11 Partnerschaften, alle 254 Startmengen):

| Regel | größte Abweichung |
|---|---|
| Knotenregel | 5,3 · 10⁻¹⁵ |
| Kantenregel | 1,0 · 10⁻¹⁴ |
| Invasionsregel | 9,5 · 10⁻¹⁵ |

**Ein einzelner Hub gegen die fünf Betriebe mit den wenigsten Partnern** (exakt, Netz mit 10 Betrieben, Hub mit Grad 5; Prozent):

| Regel | Hub allein bei 1 | fünf Randbetriebe bei 1 |
|---|---|---|
| Knotenregel | 15,6 | 31,2 |
| Kantenregel | 10,0 | 50,0 |
| Invasionsregel | 5,0 | 71,1 |

**Erwartete Schritte bis zum Konsens** (Netz mit 8 Betrieben, vier beginnen mit Verfahren 1):

| Regel | exakt | simuliert (2000 Läufe) | Gewinnchance exakt | simuliert |
|---|---|---|---|---|
| Knotenregel | 45,44 | 45,34 ± 0,91 | 54,5 | 54,3 |
| Kantenregel | 49,34 | 48,85 ± 0,97 | 50,0 | 50,0 |
| Invasionsregel | 57,69 | 55,85 ± 1,20 | 46,0 | 46,9 |

**Experiment 3: mittlere Konsenszeit in Sweeps** (zufällig die Hälfte bei 1; Vorhersage *n* μ₁² / μ₂ der Knotenregel, Verhältnis = Knotenregel / Vorhersage):

| Netztyp | *n* | Knotenregel | Kantenregel | Invasionsregel | Vorhersage | Verhältnis |
|---|---|---|---|---|---|---|
| Zufallsnetz | 40 | 26,2 | 30,8 | 42,3 | 35,4 | 0,74 |
| Zufallsnetz | 80 | 58,4 | 61,0 | 101,3 | 68,7 | 0,85 |
| Zufallsnetz | 160 | 115,3 | 137,0 | 196,4 | 138,0 | 0,84 |
| Zufallsnetz | 320 | 218,6 | 287,2 | 373,3 | 275,9 | 0,79 |
| Potenzgesetz-Netz | 40 | 22,2 | 34,1 | 71,5 | 26,0 | 0,85 |
| Potenzgesetz-Netz | 80 | 44,8 | 67,5 | 174,1 | 46,1 | 0,97 |
| Potenzgesetz-Netz | 160 | 47,1 | 132,1 | 565,1 | 54,0 | 0,87 |
| Potenzgesetz-Netz | 320 | 77,6 | 277,8 | 949,6 | 78,5 | 0,99 |
| Skalenfreies Netz (BA) | 40 | 20,7 | 31,5 | 59,3 | 27,7 | 0,75 |
| Skalenfreies Netz (BA) | 80 | 40,7 | 65,0 | 126,0 | 49,2 | 0,83 |
| Skalenfreies Netz (BA) | 160 | 69,0 | 129,4 | 316,2 | 87,8 | 0,79 |
| Skalenfreies Netz (BA) | 320 | 137,5 | 248,8 | 591,4 | 155,2 | 0,89 |
| Verbünde | 40 | 34,0 | 42,9 | 54,6 | 35,9 | 0,95 |
| Verbünde | 80 | 67,6 | 74,2 | 95,7 | 72,3 | 0,94 |
| Verbünde | 160 | 130,0 | 143,7 | 220,1 | 138,8 | 0,94 |
| Verbünde | 320 | 252,5 | 269,1 | 413,0 | 279,3 | 0,90 |
| Ring mit Abkürzungen | 40 | 45,1 | 46,4 | 43,6 | 39,8 | 1,14 |
| Ring mit Abkürzungen | 80 | 99,2 | 109,2 | 115,4 | 79,5 | 1,25 |
| Ring mit Abkürzungen | 160 | 205,2 | 246,0 | 278,5 | 158,8 | 1,29 |
| Ring mit Abkürzungen | 320 | 435,7 | 489,1 | 544,3 | 317,6 | 1,37 |
| Gitter | 40 | 36,7 | 42,6 | 47,0 | 33,7 | 1,09 |
| Gitter | 80 | 97,4 | 112,6 | 124,6 | 77,3 | 1,26 |
| Gitter | 160 | 241,6 | 220,2 | 314,7 | 163,5 | 1,48 |
| Gitter | 320 | 565,7 | 482,6 | 533,5 | 316,3 | 1,79 |

### Hypothesen des Einzelplans

| | Hypothese | Ergebnis |
|---|---|---|
| H1 | Knotenregel: die Gewinnwahrscheinlichkeit ist das Gradgewicht Σ *d*<sub>*i*</sub> / 2*m* der Startmenge | ✅ Kette bis 1,0 · 10⁻¹⁴, Simulation in allen Zellen im Band |
| H2 | Kantenregel: die Gewinnwahrscheinlichkeit ist der Anteil \|*A*\| / *n* | ✅ Kette, Simulation; Hubs 10,0 %, Hälfte am Rand 49,9 % |
| H3 | Invasionsregel: Gewicht 1/*d*<sub>*i*</sub>, ein Hub gewinnt seltener als ein Blatt | ✅ Potenzgesetz-Hubs 2,6 % gegen 32,6 % bei der Knotenregel; Netz mit 10 Betrieben: Hub 5,0 %, fünf Randbetriebe 71,1 % |
| H4 | Die Regel ändert die Gewinnchance stark, wo der Grad schwankt, kaum auf (fast) regulären Netzen | ✅ Potenzgesetz-Hubs 32,6 / 10,0 / 2,6 %; Ring und Gitter höchstens das 1,5-Fache zwischen den Regeln |
| H5 | Die Knotenregel liefert im Mittel den DeGroot-Konsens zum Start 0/1 (Brücke zu Stück 9) | ✅ DeGroot-Iteration gleich Knotenformel in allen 12 Zeilen (unter 10⁻⁶) |
| H6 | Die Konsenszeit skaliert wie *n* μ₁² / μ₂ (Sood und Redner 2005) | ⚠ nur bis auf einen Faktor (0,74 bis 0,99) in Zufalls-, Potenzgesetz-, skalenfreien und Verbünde-Netzen; Ring 1,14 → 1,37, Gitter 1,09 → 1,79 |
| H7 | Die erwartete Absorptionszeit der Kette stimmt mit der Simulation überein | ✅ 45,4 gegen 45,3 ± 0,9 (Knotenregel), Kanten- und Invasionsregel ebenso im Band |
| H8 | Die Hälfte der Betriebe (auch eine echte Mehrheit) gewinnt nicht sicher | ✅ Hälfte am Rand gewinnt bei der Knotenregel im Potenzgesetz-Netz nur mit 26,6 %; exakt im Netz mit 10 Betrieben 31,2 % |

## Ehrliche Grenzen

- **Zwei Verfahren, gleiche Betriebe, kein Starrsinn, kein spontaner Wechsel:** mit Meinungen auf einer Skala (Stück 9, 11), mit Betrieben, die nie wechseln, oder mit gelegentlichem Rauschen sind die Formeln andere; es gibt dann keinen sicheren Konsens.
- **Gleiche Wahrscheinlichkeit je Partner, festes Netz:** mit ungleichem Vertrauen ändert sich das Gewicht der Betriebe, mit wanderndem Netz die Struktur (Stück 12).
- **Zeitformel nur unkorreliert:** *n* μ₁² / μ₂ ist für Netze ohne Gradkorrelationen hergeleitet; sie ist hier nur bis auf einen Faktor gemessen und im Gitter nicht erfüllt. Für Potenzgesetz-Gradfolgen mit Exponent unter 3 gibt die Literatur andere Skalierungen an; sie werden hier nicht übernommen. Kleine Netzgrößen (40 bis 320) und 25 Läufe je Netz: die Streuung ist erheblich.
- **Stichproben:** Mittel über acht (App: vier) feste Netze; die Streuung zwischen den Netzen ist nicht ausgewiesen. Die exakte Kette gibt es nur bis zehn Betriebe (dichte Rechnung mit 1 024 Zuständen).
- **Größte Gruppe:** isolierte Betriebe und kleine Inseln bleiben unberücksichtigt.
- **Modellbefund:** die Demo zeigt Verhalten im Modell, nicht die Wirkung in der Wirklichkeit; wie weit Meinungsmodelle echte Daten treffen, ist offen (Flache u. a. 2017).
- **Literatur (nachgeschlagen am 2026-10-20, nur Zusammenfassungen gesehen):** Sood und Redner, Phys. Rev. Lett. 94, 178701 (2005); Antal, Redner und Sood, Phys. Rev. Lett. 96, 188104 (2006); Sood, Antal und Redner, Phys. Rev. E 77, 041121 (2008); Clifford und Sudbury, Biometrika 60, 1973, S. 581–588 (aus einer Literaturliste, Zusammenfassung nicht gesehen); Flache u. a., JASSS 20(4), 2017. Die Arbeiten selbst sind nicht vollständig gelesen.

## Verifikation

- **Kern:** Handwerte auf Mini-Instanzen (`tests/conftest.py`, `tests/test_algorithm.py`): zwei Betriebe (ein Schritt, Chance ½), Dreieck (Chance ⅓ in jeder Regel, erwartete Schritte 3), Pfad (Chancen ¼, ⅓, ⅖; Schritte 3, 4, 6), Stern (½, ⅕, 1/17), Paarwahrscheinlichkeiten des Pfades, Fehlerfälle, Bilder des Schritt-Reglers, Anfangsverteilungen je Modus.
- **Orakel:** `tests/test_oracle_voter_modell.py` – Kette gegen Formel auf 110 Zufallsnetzen, Martingal, gezogene Paare gegen Paarwahrscheinlichkeiten, Simulation gegen Kette (Zeit und Gewinner), Knotenformel gegen DeGroot-Iteration, reguläre Netze, Invarianten (Gewinner 0 oder 1, Zahl der Einsen ändert sich um höchstens 1).
- **Netze und Läufe:** gültig in allen Ecken der Regler, deterministisch je Seed (auch über Prozesse mit verschiedenem Hash-Seed), kleine Zufallsnetze verbunden und mit der verlangten Kantenzahl (`tests/test_scenario.py`).
- **Verdikte:** jede Schwelle und jede Zahl im Text an von Hand gesetzten Werten (`tests/test_verdicts.py`), Randfälle (Regler-Ecken für alle Netztypen, Regeln und Modi, Obergrenze der Schritte, Konsensstart, kleinste Netze in allen Experimenten, alle Abbildungen) in `tests/test_edge_cases.py`.
- **Befunde:** jede Zahl dieser README in `tests/test_claims.py` (die Messreihe dauert einige Minuten).
- **Mutationsprüfung des Kerns:** (`vot_algorithm.py`, 73 Stellen, ohne die langsamen Aussagen-Tests in der Suite der Überlebenden): 14 Stellen sind durch wortgleiche Zeilen in Nachbar-Demos gesichert, 52 Mutanten gefangen (2 davon erst nach Ergänzung von Tests: die Grenze der exakten Kette und die Zahl der Iterationsschritte der DeGroot-Probe), 2 als äquivalent festgehalten (der Schutz `deg − 1` gegen eine Zufallszahl, die nie exakt 1 ist), und 5 laufen in eine Zeitüberschreitung (Schleifenbedingung der Simulation und Abbruchbedingung der DeGroot-Probe: die Schleife läuft dann bis zur Obergrenze der Schritte) und werden durch das Hängen der Suite erkannt. Zustand in `tests/mutation_state.json`.
- **Presets:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung, jedes Preset zeigt, wofür es benannt ist.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum, jeder Netztyp, jede Regel und Anfangsverteilung, Schritt-Regler, neuer Lauf, Permalink, alle drei Experimente) und Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `vot_algorithm.py` | Kern: Paare und Schritte der drei Regeln, Simulation, Formeln der Gewinnchance, exakte Kette und Absorption, Momente der Gradfolge, Anfangsverteilungen |
| `vot_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `vot_evaluation.py` | Analyse, Verdikt-Logik, Messreihen über feste Netze |
| `vot_layout.py` | Fester Kopf (Stylesheet) |
| `vot_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `vot_scenario.py` | Netze: Generatoren (Kopie aus `k-core-demo`), Anordnung |
| `vot_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest, networkx, scipy (nur für die Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen und Handwerte, Orakel, Netze, Verdikte, Randfälle, Presets, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe, Befunde |

## Bewusst nicht umgesetzt

- **Mehr als zwei Meinungen, Starrsinn, Rauschen:** eigene Fragen; nicht Teil der Demo.
- **Mittelung statt Übernehmen** (Stück 9), **begrenztes Vertrauen** (Stück 11), **Standortwahl nach Nachbarn** (Stück 12): eigene Demos der Reihe.
- **Gewichtete oder gerichtete Netze:** die Formeln änderten sich.
- **Exakte Kette über zehn Betriebe:** die Zustandszahl wächst mit 2<sup>*n*</sup>.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
