"""Jede Zahl aus der README wird hier über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Netze der Messreihen: die acht festen Netze `SWEEP_SEEDS` je Zelle, n = 100 (Experiment 3: 40, 80, 160, 320), c = 6. Experiment 1: 200 Läufe je Netz, also 1 600 je Zelle; Experiment 3: 25 Läufe je Netz.
Alle Läufe haben ihren eigenen seedbaren Zufallsstrom (ganzzahlige Ziehungen, plattformstabil): Häufigkeiten stehen auf vier, Sweeps auf zwei Nachkommastellen, die Bänder fangen die Rundung.
Die Messreihe dauert mehrere Minuten (Experiment 1 etwa eine, Experiment 3 etwa anderthalb Minuten)."""

from functools import lru_cache

import pytest

import vot_algorithm as A
import vot_constants as C
import vot_evaluation as ev

SW = C.SWEEP_SEEDS
N, CC = 100, 6
TIME_SIZES, TIME_RUNS = (40, 80, 160, 320), 25
EXPECT = {'E1': [{'typ': 'Zufallsnetz', 'group': 'hubs', 'rule': 'node', 'formula': 0.1765, 'sim': 0.1731, 'se': 0.0095, 'degroot': 0.1765, 'runs': 1600, 'capped': 0},
        {'typ': 'Zufallsnetz', 'group': 'hubs', 'rule': 'edge', 'formula': 0.1001, 'sim': 0.0981, 'se': 0.0074, 'degroot': 0.1765, 'runs': 1600, 'capped': 0},
        {'typ': 'Zufallsnetz', 'group': 'hubs', 'rule': 'invasion', 'formula': 0.0474, 'sim': 0.0444, 'se': 0.0051, 'degroot': 0.1765, 'runs': 1600, 'capped': 0},
        {'typ': 'Zufallsnetz', 'group': 'rim', 'rule': 'node', 'formula': 0.3467, 'sim': 0.3387, 'se': 0.0118, 'degroot': 0.3467, 'runs': 1600, 'capped': 0},
        {'typ': 'Zufallsnetz', 'group': 'rim', 'rule': 'edge', 'formula': 0.4994, 'sim': 0.5125, 'se': 0.0125, 'degroot': 0.3467, 'runs': 1600, 'capped': 0},
        {'typ': 'Zufallsnetz', 'group': 'rim', 'rule': 'invasion', 'formula': 0.6718, 'sim': 0.6706, 'se': 0.0117, 'degroot': 0.3467, 'runs': 1600, 'capped': 0},
        {'typ': 'Potenzgesetz-Netz', 'group': 'hubs', 'rule': 'node', 'formula': 0.3256, 'sim': 0.3425, 'se': 0.0119, 'degroot': 0.3256, 'runs': 1600, 'capped': 0},
        {'typ': 'Potenzgesetz-Netz', 'group': 'hubs', 'rule': 'edge', 'formula': 0.1001, 'sim': 0.1094, 'se': 0.0078, 'degroot': 0.3256, 'runs': 1600, 'capped': 0},
        {'typ': 'Potenzgesetz-Netz', 'group': 'hubs', 'rule': 'invasion', 'formula': 0.0262, 'sim': 0.0194, 'se': 0.0034, 'degroot': 0.3256, 'runs': 1600, 'capped': 0},
        {'typ': 'Potenzgesetz-Netz', 'group': 'rim', 'rule': 'node', 'formula': 0.2655, 'sim': 0.2631, 'se': 0.011, 'degroot': 0.2655, 'runs': 1600, 'capped': 0},
        {'typ': 'Potenzgesetz-Netz', 'group': 'rim', 'rule': 'edge', 'formula': 0.4994, 'sim': 0.4988, 'se': 0.0125, 'degroot': 0.2655, 'runs': 1600, 'capped': 0},
        {'typ': 'Potenzgesetz-Netz', 'group': 'rim', 'rule': 'invasion', 'formula': 0.6813, 'sim': 0.6837, 'se': 0.0116, 'degroot': 0.2655, 'runs': 1600, 'capped': 0},
        {'typ': 'Skalenfreies Netz (BA)', 'group': 'hubs', 'rule': 'node', 'formula': 0.3055, 'sim': 0.2981, 'se': 0.0114, 'degroot': 0.3055, 'runs': 1600, 'capped': 0},
        {'typ': 'Skalenfreies Netz (BA)', 'group': 'hubs', 'rule': 'edge', 'formula': 0.1, 'sim': 0.0969, 'se': 0.0074, 'degroot': 0.3055, 'runs': 1600, 'capped': 0},
        {'typ': 'Skalenfreies Netz (BA)',
         'group': 'hubs',
         'rule': 'invasion',
         'formula': 0.0266,
         'sim': 0.0319,
         'se': 0.0044,
         'degroot': 0.3055,
         'runs': 1600,
         'capped': 0},
        {'typ': 'Skalenfreies Netz (BA)', 'group': 'rim', 'rule': 'node', 'formula': 0.2747, 'sim': 0.2888, 'se': 0.0113, 'degroot': 0.2747, 'runs': 1600, 'capped': 0},
        {'typ': 'Skalenfreies Netz (BA)', 'group': 'rim', 'rule': 'edge', 'formula': 0.5, 'sim': 0.5088, 'se': 0.0125, 'degroot': 0.2747, 'runs': 1600, 'capped': 0},
        {'typ': 'Skalenfreies Netz (BA)',
         'group': 'rim',
         'rule': 'invasion',
         'formula': 0.6713,
         'sim': 0.6906,
         'se': 0.0116,
         'degroot': 0.2747,
         'runs': 1600,
         'capped': 0},
        {'typ': 'Verbünde', 'group': 'hubs', 'rule': 'node', 'formula': 0.1642, 'sim': 0.1663, 'se': 0.0093, 'degroot': 0.1642, 'runs': 1600, 'capped': 0},
        {'typ': 'Verbünde', 'group': 'hubs', 'rule': 'edge', 'formula': 0.1003, 'sim': 0.0969, 'se': 0.0074, 'degroot': 0.1642, 'runs': 1600, 'capped': 0},
        {'typ': 'Verbünde', 'group': 'hubs', 'rule': 'invasion', 'formula': 0.0524, 'sim': 0.0569, 'se': 0.0058, 'degroot': 0.1642, 'runs': 1600, 'capped': 0},
        {'typ': 'Verbünde', 'group': 'rim', 'rule': 'node', 'formula': 0.3638, 'sim': 0.3644, 'se': 0.012, 'degroot': 0.3638, 'runs': 1600, 'capped': 0},
        {'typ': 'Verbünde', 'group': 'rim', 'rule': 'edge', 'formula': 0.4987, 'sim': 0.5269, 'se': 0.0125, 'degroot': 0.3638, 'runs': 1600, 'capped': 0},
        {'typ': 'Verbünde', 'group': 'rim', 'rule': 'invasion', 'formula': 0.6544, 'sim': 0.6381, 'se': 0.012, 'degroot': 0.3638, 'runs': 1600, 'capped': 0},
        {'typ': 'Ring mit Abkürzungen', 'group': 'hubs', 'rule': 'node', 'formula': 0.1168, 'sim': 0.1138, 'se': 0.0079, 'degroot': 0.1168, 'runs': 1600, 'capped': 0},
        {'typ': 'Ring mit Abkürzungen', 'group': 'hubs', 'rule': 'edge', 'formula': 0.1, 'sim': 0.1206, 'se': 0.0081, 'degroot': 0.1168, 'runs': 1600, 'capped': 0},
        {'typ': 'Ring mit Abkürzungen',
         'group': 'hubs',
         'rule': 'invasion',
         'formula': 0.0854,
         'sim': 0.0963,
         'se': 0.0074,
         'degroot': 0.1168,
         'runs': 1600,
         'capped': 0},
        {'typ': 'Ring mit Abkürzungen', 'group': 'rim', 'rule': 'node', 'formula': 0.4778, 'sim': 0.4706, 'se': 0.0125, 'degroot': 0.4778, 'runs': 1600, 'capped': 0},
        {'typ': 'Ring mit Abkürzungen', 'group': 'rim', 'rule': 'edge', 'formula': 0.5, 'sim': 0.4813, 'se': 0.0125, 'degroot': 0.4778, 'runs': 1600, 'capped': 0},
        {'typ': 'Ring mit Abkürzungen', 'group': 'rim', 'rule': 'invasion', 'formula': 0.5202, 'sim': 0.535, 'se': 0.0125, 'degroot': 0.4778, 'runs': 1600, 'capped': 0},
        {'typ': 'Gitter', 'group': 'hubs', 'rule': 'node', 'formula': 0.1149, 'sim': 0.1212, 'se': 0.0082, 'degroot': 0.1149, 'runs': 1600, 'capped': 0},
        {'typ': 'Gitter', 'group': 'hubs', 'rule': 'edge', 'formula': 0.1, 'sim': 0.11, 'se': 0.0078, 'degroot': 0.1149, 'runs': 1600, 'capped': 0},
        {'typ': 'Gitter', 'group': 'hubs', 'rule': 'invasion', 'formula': 0.082, 'sim': 0.0944, 'se': 0.0073, 'degroot': 0.1149, 'runs': 1600, 'capped': 0},
        {'typ': 'Gitter', 'group': 'rim', 'rule': 'node', 'formula': 0.4253, 'sim': 0.4288, 'se': 0.0124, 'degroot': 0.4253, 'runs': 1600, 'capped': 0},
        {'typ': 'Gitter', 'group': 'rim', 'rule': 'edge', 'formula': 0.5, 'sim': 0.4863, 'se': 0.0125, 'degroot': 0.4253, 'runs': 1600, 'capped': 0},
        {'typ': 'Gitter', 'group': 'rim', 'rule': 'invasion', 'formula': 0.5902, 'sim': 0.5956, 'se': 0.0123, 'degroot': 0.4253, 'runs': 1600, 'capped': 0}],
 'E2': {'dev': [{'rule': 'node', 'max_dev': 5.33e-15, 'nets': 10},
                {'rule': 'edge', 'max_dev': 1.05e-14, 'nets': 10},
                {'rule': 'invasion', 'max_dev': 9.55e-15, 'nets': 10}],
        'hub_rim': [{'rule': 'node', 'hub': 0.1563, 'rim': 0.3125}, {'rule': 'edge', 'hub': 0.1, 'rim': 0.5}, {'rule': 'invasion', 'hub': 0.0502, 'rim': 0.7113}],
        'time': [{'rule': 'node', 'exact_time': 45.438, 'sim_time': 45.344, 'sim_se': 0.91, 'exact_win': 0.5455, 'sim_win': 0.543, 'runs': 2000},
                 {'rule': 'edge', 'exact_time': 49.345, 'sim_time': 48.855, 'sim_se': 0.971, 'exact_win': 0.5, 'sim_win': 0.4995, 'runs': 2000},
                 {'rule': 'invasion', 'exact_time': 57.694, 'sim_time': 55.852, 'sim_se': 1.203, 'exact_win': 0.4595, 'sim_win': 0.469, 'runs': 2000}],
        'hub_degree': 5,
        'n10': 10},
 'E3': [{'typ': 'Zufallsnetz', 'n': 40, 'sweeps': {'node': 26.23, 'edge': 30.8, 'invasion': 42.32}, 'pred': 35.37, 'ratio': 0.741, 'runs': 200},
        {'typ': 'Zufallsnetz', 'n': 80, 'sweeps': {'node': 58.4, 'edge': 60.97, 'invasion': 101.32}, 'pred': 68.69, 'ratio': 0.85, 'runs': 200},
        {'typ': 'Zufallsnetz', 'n': 160, 'sweeps': {'node': 115.34, 'edge': 137.01, 'invasion': 196.43}, 'pred': 138.04, 'ratio': 0.836, 'runs': 200},
        {'typ': 'Zufallsnetz', 'n': 320, 'sweeps': {'node': 218.63, 'edge': 287.17, 'invasion': 373.28}, 'pred': 275.93, 'ratio': 0.792, 'runs': 200},
        {'typ': 'Potenzgesetz-Netz', 'n': 40, 'sweeps': {'node': 22.18, 'edge': 34.1, 'invasion': 71.49}, 'pred': 26.01, 'ratio': 0.853, 'runs': 200},
        {'typ': 'Potenzgesetz-Netz', 'n': 80, 'sweeps': {'node': 44.83, 'edge': 67.46, 'invasion': 174.07}, 'pred': 46.08, 'ratio': 0.973, 'runs': 200},
        {'typ': 'Potenzgesetz-Netz', 'n': 160, 'sweeps': {'node': 47.12, 'edge': 132.13, 'invasion': 565.12}, 'pred': 53.97, 'ratio': 0.873, 'runs': 200},
        {'typ': 'Potenzgesetz-Netz', 'n': 320, 'sweeps': {'node': 77.64, 'edge': 277.75, 'invasion': 949.6}, 'pred': 78.5, 'ratio': 0.989, 'runs': 200},
        {'typ': 'Skalenfreies Netz (BA)', 'n': 40, 'sweeps': {'node': 20.72, 'edge': 31.52, 'invasion': 59.33}, 'pred': 27.69, 'ratio': 0.748, 'runs': 200},
        {'typ': 'Skalenfreies Netz (BA)', 'n': 80, 'sweeps': {'node': 40.73, 'edge': 65.04, 'invasion': 126.02}, 'pred': 49.18, 'ratio': 0.828, 'runs': 200},
        {'typ': 'Skalenfreies Netz (BA)', 'n': 160, 'sweeps': {'node': 69.05, 'edge': 129.39, 'invasion': 316.19}, 'pred': 87.8, 'ratio': 0.786, 'runs': 200},
        {'typ': 'Skalenfreies Netz (BA)', 'n': 320, 'sweeps': {'node': 137.5, 'edge': 248.85, 'invasion': 591.4}, 'pred': 155.15, 'ratio': 0.886, 'runs': 200},
        {'typ': 'Verbünde', 'n': 40, 'sweeps': {'node': 33.96, 'edge': 42.92, 'invasion': 54.64}, 'pred': 35.86, 'ratio': 0.947, 'runs': 200},
        {'typ': 'Verbünde', 'n': 80, 'sweeps': {'node': 67.63, 'edge': 74.22, 'invasion': 95.7}, 'pred': 72.27, 'ratio': 0.936, 'runs': 200},
        {'typ': 'Verbünde', 'n': 160, 'sweeps': {'node': 130.0, 'edge': 143.67, 'invasion': 220.07}, 'pred': 138.83, 'ratio': 0.936, 'runs': 200},
        {'typ': 'Verbünde', 'n': 320, 'sweeps': {'node': 252.52, 'edge': 269.13, 'invasion': 412.98}, 'pred': 279.29, 'ratio': 0.904, 'runs': 200},
        {'typ': 'Ring mit Abkürzungen', 'n': 40, 'sweeps': {'node': 45.15, 'edge': 46.35, 'invasion': 43.63}, 'pred': 39.78, 'ratio': 1.135, 'runs': 200},
        {'typ': 'Ring mit Abkürzungen', 'n': 80, 'sweeps': {'node': 99.22, 'edge': 109.2, 'invasion': 115.41}, 'pred': 79.53, 'ratio': 1.248, 'runs': 200},
        {'typ': 'Ring mit Abkürzungen', 'n': 160, 'sweeps': {'node': 205.23, 'edge': 245.97, 'invasion': 278.52}, 'pred': 158.8, 'ratio': 1.292, 'runs': 200},
        {'typ': 'Ring mit Abkürzungen', 'n': 320, 'sweeps': {'node': 435.73, 'edge': 489.05, 'invasion': 544.32}, 'pred': 317.63, 'ratio': 1.372, 'runs': 200},
        {'typ': 'Gitter', 'n': 40, 'sweeps': {'node': 36.73, 'edge': 42.59, 'invasion': 46.97}, 'pred': 33.68, 'ratio': 1.09, 'runs': 200},
        {'typ': 'Gitter', 'n': 80, 'sweeps': {'node': 97.41, 'edge': 112.61, 'invasion': 124.64}, 'pred': 77.33, 'ratio': 1.26, 'runs': 200},
        {'typ': 'Gitter', 'n': 160, 'sweeps': {'node': 241.6, 'edge': 220.17, 'invasion': 314.69}, 'pred': 163.54, 'ratio': 1.477, 'runs': 200},
        {'typ': 'Gitter', 'n': 320, 'sweeps': {'node': 565.73, 'edge': 482.6, 'invasion': 533.49}, 'pred': 316.31, 'ratio': 1.789, 'runs': 200}],
 'presets': {'Zufallsnetz: die Hälfte gegen die Hälfte (Voreinstellung)': {'n': 60,
                                                                           'm': 60,
                                                                           'edges': 180,
                                                                           'ones0': 30,
                                                                           'steps': 1772,
                                                                           'winner': 1,
                                                                           'probs': {'node': 0.5444, 'edge': 0.5, 'invasion': 0.4309},
                                                                           'degroot': 0.5444,
                                                                           'pred_sweeps': 52.26,
                                                                           'kind': 'info',
                                                                           'verdict': 'Verfahren 1 beginnt in 30 von 60 Betrieben; seine Gewinnchance ist bei der '
                                                                                      'Knotenregel 54,4 % (alle Regeln: Knotenregel 54,4 %, Kantenregel 50,0 %, '
                                                                                      'Invasionsregel 43,1 %). Nach 1772 Schritten (29,5 Sweeps) nutzen alle Betriebe '
                                                                                      'Verfahren 1; das war in 54,4 % der Fälle zu erwarten, der Konsens selbst war '
                                                                                      'sicher. Der DeGroot-Konsens (Stück 9) zum selben Start ist 0,544: genau die '
                                                                                      'Chance der Knotenregel.'},
             'Knotenregel: die Hubs im Vorteil': {'n': 60,
                                                  'm': 60,
                                                  'edges': 161,
                                                  'ones0': 10,
                                                  'steps': 3380,
                                                  'winner': 1,
                                                  'probs': {'node': 0.3789, 'edge': 0.1667, 'invasion': 0.0584},
                                                  'degroot': 0.3789,
                                                  'pred_sweeps': 40.85,
                                                  'kind': 'success',
                                                  'verdict': 'Verfahren 1 beginnt in 10 von 60 Betrieben; seine Gewinnchance ist bei der Knotenregel 37,9 % (alle '
                                                             'Regeln: Knotenregel 37,9 %, Kantenregel 16,7 %, Invasionsregel 5,8 %). Nach 3380 Schritten (56,3 Sweeps) '
                                                             'nutzen alle Betriebe Verfahren 1; das war in 37,9 % der Fälle zu erwarten, der Konsens selbst war sicher. '
                                                             'Der DeGroot-Konsens (Stück 9) zum selben Start ist 0,379: genau die Chance der Knotenregel. Die Regel '
                                                             'verändert die Chance um das 6,5-Fache.'},
             'Invasionsregel: dieselben Hubs im Nachteil': {'n': 60,
                                                            'm': 60,
                                                            'edges': 161,
                                                            'ones0': 10,
                                                            'steps': 3220,
                                                            'winner': 0,
                                                            'probs': {'node': 0.3789, 'edge': 0.1667, 'invasion': 0.0584},
                                                            'degroot': 0.3789,
                                                            'pred_sweeps': 40.85,
                                                            'kind': 'success',
                                                            'verdict': 'Verfahren 1 beginnt in 10 von 60 Betrieben; seine Gewinnchance ist bei der Invasionsregel 5,8 % '
                                                                       '(alle Regeln: Knotenregel 37,9 %, Kantenregel 16,7 %, Invasionsregel 5,8 %). Nach 3220 Schritten '
                                                                       '(53,7 Sweeps) nutzen alle Betriebe Verfahren 0; das war in 94,2 % der Fälle zu erwarten, der '
                                                                       'Konsens selbst war sicher. Der DeGroot-Konsens (Stück 9) zum selben Start ist 0,379: genau die '
                                                                       'Chance der Knotenregel. Die Regel verändert die Chance um das 6,5-Fache.'},
             'Kantenregel: nur der Anteil zählt': {'n': 60,
                                                   'm': 60,
                                                   'edges': 161,
                                                   'ones0': 10,
                                                   'steps': 2980,
                                                   'winner': 0,
                                                   'probs': {'node': 0.3789, 'edge': 0.1667, 'invasion': 0.0584},
                                                   'degroot': 0.3789,
                                                   'pred_sweeps': 40.85,
                                                   'kind': 'success',
                                                   'verdict': 'Verfahren 1 beginnt in 10 von 60 Betrieben; seine Gewinnchance ist bei der Kantenregel 16,7 % (alle '
                                                              'Regeln: Knotenregel 37,9 %, Kantenregel 16,7 %, Invasionsregel 5,8 %). Nach 2980 Schritten (49,7 Sweeps) '
                                                              'nutzen alle Betriebe Verfahren 0; das war in 83,3 % der Fälle zu erwarten, der Konsens selbst war sicher. '
                                                              'Der DeGroot-Konsens (Stück 9) zum selben Start ist 0,379: genau die Chance der Knotenregel. Die Regel '
                                                              'verändert die Chance um das 6,5-Fache.'},
             'Ring: die Regel ändert wenig': {'n': 60,
                                          'm': 60,
                                          'edges': 188,
                                          'ones0': 10,
                                          'steps': 661,
                                          'winner': 0,
                                          'probs': {'node': 0.1941, 'edge': 0.1667, 'invasion': 0.1427},
                                          'degroot': 0.1941,
                                          'pred_sweeps': 59.55,
                                          'kind': 'info',
                                          'verdict': 'Verfahren 1 beginnt in 10 von 60 Betrieben; seine Gewinnchance ist bei der Knotenregel 19,4 % (alle Regeln: '
                                                     'Knotenregel 19,4 %, Kantenregel 16,7 %, Invasionsregel 14,3 %). Nach 661 Schritten (11,0 Sweeps) nutzen alle '
                                                     'Betriebe Verfahren 0; das war in 80,6 % der Fälle zu erwarten, der Konsens selbst war sicher. Der DeGroot-Konsens '
                                                     '(Stück 9) zum selben Start ist 0,194: genau die Chance der Knotenregel.'},
             'Mehrheit am Rand verliert oft': {'n': 60,
                                               'm': 60,
                                               'edges': 161,
                                               'ones0': 30,
                                               'steps': 3380,
                                               'winner': 0,
                                               'probs': {'node': 0.2795, 'edge': 0.5, 'invasion': 0.6988},
                                               'degroot': 0.2795,
                                               'pred_sweeps': 40.85,
                                               'kind': 'success',
                                               'verdict': 'Verfahren 1 beginnt in 30 von 60 Betrieben; seine Gewinnchance ist bei der Knotenregel 28,0 % (alle Regeln: '
                                                          'Knotenregel 28,0 %, Kantenregel 50,0 %, Invasionsregel 69,9 %). Nach 3380 Schritten (56,3 Sweeps) nutzen alle '
                                                          'Betriebe Verfahren 0; das war in 72,0 % der Fälle zu erwarten, der Konsens selbst war sicher. Der '
                                                          'DeGroot-Konsens (Stück 9) zum selben Start ist 0,280: genau die Chance der Knotenregel. Die Regel verändert '
                                                          'die Chance um das 2,5-Fache.'}},
 'V_E1': 'Haben nur die zehn Hubs Verfahren 1, gewinnt es in „Potenzgesetz-Netz“ mit 34,2 % bei der Knotenregel, 10,9 % bei der Kantenregel und 1,9 % bei der '
         'Invasionsregel (Formeln: 32,6 / 10,0 / 2,6 %). Kaum ein Unterschied (unter dem 1,5-Fachen) zwischen den Regeln besteht in: „Ring mit Abkürzungen“, „Gitter“. '
         'Beginnt die Hälfte der Betriebe am Rand mit Verfahren 1, gewinnt sie in „Potenzgesetz-Netz“ bei der Knotenregel nur in 26,3 % der Fälle (Formel 26,6 %), '
         'obwohl sie die Hälfte der Betriebe stellt.',
 'V_E2': 'Auf 10 kleinen Netzen (8 Betriebe, 11 Partnerschaften) weicht die exakte Gewinnwahrscheinlichkeit der Kette bei jeder Startmenge um höchstens 1,1 · 10⁻¹⁴ von '
         'der Formel ab. Im Netz mit 10 Betrieben gewinnt ein einzelner Hub (Grad 5) mit 15,6 / 10,0 / 5,0 % (Knoten / Kante / Invasion), die fünf Betriebe mit den '
         'wenigsten Partnern mit 31,3 / 50,0 / 71,1 %. Erwartete Schritte bei der Knotenregel: exakt 45,4, simuliert 45,3 ± 0,9.',
 'V_E3': 'Die mittlere Konsenszeit der Knotenregel geteilt durch n μ₁² / μ₂ liegt bei n = 40, 80, 160, 320 in „Zufallsnetz“ bei 0,74 bis 0,85; „Potenzgesetz-Netz“ bei '
         '0,85 bis 0,99; „Skalenfreies Netz (BA)“ bei 0,75 bis 0,89; „Verbünde“ bei 0,90 bis 0,95; „Ring mit Abkürzungen“ bei 1,13 bis 1,37 (ungefähr konstant); dagegen '
         'in „Gitter“ von 1,09 auf 1,79 (die Vorhersage trifft hier nicht).'}


@lru_cache(maxsize=None)
def _e1():
    return ev.rules_rows(N, CC, seeds=SW, runs=C.SWEEP_RUNS)


@lru_cache(maxsize=None)
def _e2():
    return ev.exact_rows()


@lru_cache(maxsize=None)
def _e3():
    return ev.time_rows(CC, sizes=TIME_SIZES, seeds=SW, runs=TIME_RUNS)


def _p(x, digits=4):
    return pytest.approx(x, abs=0.6 * 10.0**-digits)


# --- E1: Die Regel ändert den Gewinner ---------------------------------------------------------------------------------------------------------------


def test_win_probabilities_formula_and_simulation_per_type_group_and_rule():
    rows = _e1()
    assert len(rows) == len(EXPECT["E1"]) == len(C.ALL_TYPES) * 2 * 3
    for got, exp in zip(rows, EXPECT["E1"]):
        assert (got["typ"], got["group"], got["rule"], got["runs"], got["capped"]) == (exp["typ"], exp["group"], exp["rule"], exp["runs"], exp["capped"]), exp
        assert got["formula"] == _p(exp["formula"]) and got["sim"] == _p(exp["sim"]) and got["se"] == _p(exp["se"]) and got["degroot"] == _p(exp["degroot"]), exp
    assert ev.verdict_rules(rows)[1] == EXPECT["V_E1"]


def test_the_simulation_agrees_with_the_exact_formula_in_every_cell_and_the_degroot_iteration_with_the_node_formula():
    rows = _e1()
    for r in rows:
        assert abs(r["sim"] - r["formula"]) <= 4 * r["se"] + 0.01, (r["typ"], r["group"], r["rule"])
        assert r["degroot"] == pytest.approx(ev.rule_cell(rows, r["typ"], r["group"], C.R_NODE)["formula"], abs=1e-6)       # Brücke zu Stück 9
    assert sum(1 for r in rows if abs(r["sim"] - r["formula"]) > 2 * r["se"]) <= 6                                          # etwa jede zwanzigste Zelle liegt über zwei Standardfehlern


def test_the_rule_changes_the_winner_where_degrees_vary_and_hardly_on_regular_networks():
    rows = _e1()
    for typ in (C.T_RANDOM, C.T_POWER, C.T_BA, C.T_COMMUNITIES):
        h = [ev.rule_cell(rows, typ, "hubs", r)["formula"] for r in C.RULES]
        m = [ev.rule_cell(rows, typ, "rim", r)["formula"] for r in C.RULES]
        assert h[0] > h[1] > h[2] and h[0] >= 3 * h[2] and m[0] < m[1] < m[2], typ
    h = [ev.rule_cell(rows, C.T_POWER, "hubs", r)["formula"] for r in C.RULES]
    assert h[0] > 3 * h[1] > 9 * h[2] and h[0] > 10 * h[2]                                                                   # Potenzgesetz: Knoten gegen Kante gegen Invasion
    for typ in (C.T_RING, C.T_GRID):
        h = [ev.rule_cell(rows, typ, "hubs", r)["formula"] for r in C.RULES]
        assert max(h) / min(h) < 1.5, typ
    for typ in C.ALL_TYPES:
        assert ev.rule_cell(rows, typ, "hubs", C.R_EDGE)["formula"] == pytest.approx(C.HUBS_K / N, abs=0.002) and ev.rule_cell(rows, typ, "rim", C.R_EDGE)["formula"] == pytest.approx(0.5, abs=0.002)
    assert ev.rule_cell(rows, C.T_POWER, "rim", C.R_NODE)["formula"] < 0.3 and ev.rule_cell(rows, C.T_POWER, "rim", C.R_INVASION)["formula"] > 0.65     # die Mehrheit am Rand verliert bei der Knotenregel


# --- E2: exakt auf kleinen Netzen --------------------------------------------------------------------------------------------------------------------


def test_exact_chain_against_formula_hub_against_rim_and_time():
    res = _e2()
    for got, exp in zip(res["dev"], EXPECT["E2"]["dev"]):
        assert got["rule"] == exp["rule"] and got["nets"] == exp["nets"] and got["max_dev"] < 1e-12 and exp["max_dev"] < 1e-12
    for got, exp in zip(res["hub_rim"], EXPECT["E2"]["hub_rim"]):
        assert got["rule"] == exp["rule"] and got["hub"] == _p(exp["hub"]) and got["rim"] == _p(exp["rim"])
    for got, exp in zip(res["time"], EXPECT["E2"]["time"]):
        assert got["rule"] == exp["rule"] and got["runs"] == exp["runs"] and got["exact_time"] == _p(exp["exact_time"], 3) and got["sim_time"] == _p(exp["sim_time"], 3) and got["sim_se"] == _p(exp["sim_se"], 3)
        assert got["exact_win"] == _p(exp["exact_win"]) and got["sim_win"] == _p(exp["sim_win"])
        assert abs(got["sim_time"] - got["exact_time"]) < 3 * got["sim_se"] and abs(got["sim_win"] - got["exact_win"]) < 0.04
    assert res["hub_degree"] == EXPECT["E2"]["hub_degree"] and res["n10"] == EXPECT["E2"]["n10"] == C.EXACT_N10
    assert ev.verdict_exact(res)[1] == EXPECT["V_E2"]


def test_one_hub_loses_to_five_rim_nodes_under_every_rule_and_the_rule_orders_them():
    hr = {x["rule"]: x for x in _e2()["hub_rim"]}
    assert hr[C.R_NODE]["hub"] > hr[C.R_EDGE]["hub"] > hr[C.R_INVASION]["hub"] and hr[C.R_NODE]["rim"] < 0.35 and hr[C.R_INVASION]["rim"] > 0.65
    assert hr[C.R_EDGE]["hub"] == pytest.approx(0.1, abs=1e-9) and hr[C.R_EDGE]["rim"] == pytest.approx(0.5, abs=1e-9)         # Kantenregel: Anteil 1/10 und 5/10 exakt


# --- E3: Konsenszeit ------------------------------------------------------------------------------------------------------------------------------


def test_consensus_time_table():
    rows = _e3()
    assert len(rows) == len(EXPECT["E3"]) == len(C.ALL_TYPES) * len(TIME_SIZES)
    for got, exp in zip(rows, EXPECT["E3"]):
        assert (got["typ"], got["n"], got["runs"]) == (exp["typ"], exp["n"], exp["runs"]) and got["pred"] == pytest.approx(exp["pred"], abs=0.006) and got["ratio"] == _p(exp["ratio"], 3)
        for rule in C.RULES:
            assert got["sweeps"][rule] == pytest.approx(exp["sweeps"][rule], abs=0.006), (exp["typ"], exp["n"], rule)
    assert ev.verdict_time(rows)[1] == EXPECT["V_E3"]


def test_the_sood_redner_prediction_holds_up_to_a_factor_in_random_like_networks_but_not_in_the_grid():
    rows = _e3()
    for typ in (C.T_RANDOM, C.T_POWER, C.T_BA, C.T_COMMUNITIES):
        ratios = [ev.time_cell(rows, typ, n)["ratio"] for n in TIME_SIZES]
        assert all(0.7 <= x <= 1.05 for x in ratios) and max(ratios) / min(ratios) <= 1.25, typ
    ring = [ev.time_cell(rows, C.T_RING, n)["ratio"] for n in TIME_SIZES]
    grid = [ev.time_cell(rows, C.T_GRID, n)["ratio"] for n in TIME_SIZES]
    assert ring == sorted(ring) and 1.1 < ring[0] and ring[-1] < 1.5 and grid == sorted(grid) and grid[-1] / grid[0] > 1.5


def test_the_rule_also_changes_the_time_in_heavy_tailed_networks_but_not_in_the_ring():
    rows = _e3()
    big = ev.time_cell(rows, C.T_POWER, 320)["sweeps"]
    assert big[C.R_INVASION] > 8 * big[C.R_NODE] and big[C.R_EDGE] > 2.5 * big[C.R_NODE]
    for n in TIME_SIZES:
        ring = ev.time_cell(rows, C.T_RING, n)["sweeps"]
        assert max(ring.values()) / min(ring.values()) < 1.4, n


# --- Presets ------------------------------------------------------------------------------------------------------------------------------------------


def test_presets_numbers():
    assert set(EXPECT["presets"]) == set(C.PRESETS)
    for name, exp in EXPECT["presets"].items():
        an = ev.analyse(ev.Settings(**C.PRESETS[name]))
        assert (an.inst.n, an.m, int(sum(len(x) for x in an.inst.adj) // 2), an.ones0, an.steps, an.winner) == (exp["n"], exp["m"], exp["edges"], exp["ones0"], exp["steps"], exp["winner"]), name
        assert {r: round(v, 4) for r, v in an.probs.items()} == pytest.approx(exp["probs"], abs=0.0006) and an.degroot == _p(exp["degroot"]) and an.pred_sweeps == pytest.approx(exp["pred_sweeps"], abs=0.006), name
        assert ev.verdict_main(an) == (exp["kind"], exp["verdict"]), name


def test_the_core_and_the_measured_winners_follow_the_same_formula():
    an = ev.analyse(ev.Settings(**C.PRESETS["Knotenregel: die Hubs im Vorteil"]))
    assert an.probs[C.R_NODE] == pytest.approx(A.win_probability(an.adj, [int(i) for i in an.x0.nonzero()[0]], A.NODE))
