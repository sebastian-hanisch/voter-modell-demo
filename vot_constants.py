"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# --- Netztypen -----------------------------------------------------------------------------------------------------------------------------------
T_RANDOM = "Zufallsnetz"
T_POWER = "Potenzgesetz-Netz"
T_BA = "Skalenfreies Netz (BA)"
T_COMMUNITIES = "Verbünde"
T_RING = "Ring mit Abkürzungen"
T_GRID = "Gitter"
ALL_TYPES = (T_RANDOM, T_POWER, T_BA, T_COMMUNITIES, T_RING, T_GRID)
BLOCKS = 6

C_MEANING = {
    T_RANDOM: "mittlerer Grad des Zufallsnetzes",
    T_POWER: "mittlerer Grad (Gradfolge mit Potenzgesetz-Exponent 2,5, Konfigurationsmodell)",
    T_BA: "zwei Kanten je neuem Knoten, also m = c / 2 gerundet (jeder Knoten hat mindestens m Nachbarn)",
    T_COMMUNITIES: "mittlerer Grad; 80 % der Kanten bleiben im eigenen Verbund (6 Verbünde)",
    T_RING: "Nachbarn auf dem Ring (c gerade gerundet), dazu Abkürzungen mit 5 % je Ringkante",
    T_GRID: "Nachbarschaft: unter 6 vier Nachbarn, 6 bis 7 mit einer Diagonale, ab 8 mit beiden Diagonalen",
}

N_MIN, N_MAX, DEFAULT_N = 40, 120, 60
C_MIN, C_MAX, DEFAULT_C = 3, 12, 6
SEED_MAX, DEFAULT_SEED = 999999, 35
SWEEP_SEEDS = tuple(range(100000, 100008))         # feste Netze für alle Messreihen: nie ein einzelner Seed als Befund
LIVE_SEEDS = SWEEP_SEEDS[:4]                       # so viele feste Netze je Zelle rechnet die App live (die README-Zahlen nutzen alle acht)

# --- Regeln ----------------------------------------------------------------------------------------------------------------------------------------
R_NODE, R_EDGE, R_INVASION = "node", "edge", "invasion"
RULES = (R_NODE, R_EDGE, R_INVASION)
RULE_LABEL = {R_NODE: "Knotenregel", R_EDGE: "Kantenregel", R_INVASION: "Invasionsregel"}
LABEL_RULE = {v: k for k, v in RULE_LABEL.items()}
RULE_HELP = {
    R_NODE: "Ein zufälliger Betrieb übernimmt das Verfahren eines zufälligen Partners (das klassische Voter-Modell).",
    R_EDGE: "Eine zufällige Partnerschaft wird gewählt, einer der beiden Betriebe übernimmt das Verfahren des anderen.",
    R_INVASION: "Ein zufälliger Betrieb gibt sein Verfahren an einen zufälligen Partner weiter.",
}
RULE_WEIGHT_TEXT = {
    R_NODE: "Gewicht = Zahl der Partner",
    R_EDGE: "alle Betriebe gleich",
    R_INVASION: "Gewicht = 1 / Zahl der Partner",
}

# --- Anfangsverteilungen ---------------------------------------------------------------------------------------------------------------------------
M_HALF, M_HUBS, M_RIM, M_SINGLE = "Zufällig die Hälfte", "Die zehn Hubs", "Die Hälfte am Rand", "Ein einzelner Betrieb"
MODES = (M_HALF, M_HUBS, M_RIM, M_SINGLE)
DEFAULT_MODE = M_HALF
MODE_HELP = {
    M_HALF: "Eine zufällige Hälfte der Betriebe beginnt mit Verfahren 1, die andere mit Verfahren 0.",
    M_HUBS: "Die zehn Betriebe mit den meisten Partnern beginnen mit Verfahren 1, alle anderen mit 0.",
    M_RIM: "Die Hälfte der Betriebe mit den wenigsten Partnern beginnt mit Verfahren 1, die andere Hälfte (mit den Hubs) mit 0.",
    M_SINGLE: "Ein zufälliger Betrieb beginnt mit Verfahren 1, alle anderen mit 0.",
}
HUBS_K = 10                                         # Zahl der Betriebe im Modus „Die zehn Hubs“ und in Experiment 1
EXACT_MAX_N = 10                                    # die exakte Kette hat 2^n Zustände (dichte Rechnung)

# --- Läufe und Messungen -----------------------------------------------------------------------------------------------------------------------------
MAX_STEPS = 400_000                                 # Schutz: Obergrenze der Schritte eines Laufs (n <= 120 braucht Zehntausende)
FRAMES = 120                                        # Zahl der Bilder im Schritt-Regler
LIVE_RUNS = 60                                      # Läufe je Netz und Zelle in der App
SWEEP_RUNS = 200                                    # Läufe je Netz und Zelle in der README
TIME_SIZES = (40, 80, 160)                          # Netzgrößen in Experiment 3 (160 über dem Regler: nur Messreihe)
TIME_RUNS_LIVE = 30
EXACT_NETS, EXACT_SMALL_N, EXACT_SMALL_M = 10, 8, 11
EXACT_N10, EXACT_M10 = 10, 16
EXACT_SIM_RUNS = 2000

# --- Darstellung ---------------------------------------------------------------------------------------------------------------------------------
COLOR_EDGE = "rgba(120,120,120,0.30)"
COLOR_0 = "#4c78a8"                                 # Verfahren 0
COLOR_1 = "#c4623b"                                 # Verfahren 1
COLOR_A = "#2F6B65"
COLOR_C = "#6b5b95"
RULE_COLORS = {R_NODE: "#2F6B65", R_EDGE: "#6b5b95", R_INVASION: "#c4623b"}
TYPE_COLORS = {T_RANDOM: "#2F6B65", T_POWER: "#c4623b", T_BA: "#6b5b95", T_COMMUNITIES: "#9d755d", T_RING: "#4c78a8", T_GRID: "#8c8c8c"}

STORY_SEED = 1                                      # Seed der Potenzgesetz-Presets: Knotenregel gewinnen die Hubs, Kanten- und Invasionsregel verlieren sie (Lauf einer Ziehung, per Scan gewählt)
PRESETS = {
    "Zufallsnetz: die Hälfte gegen die Hälfte (Voreinstellung)": {"netztyp": T_RANDOM, "n": DEFAULT_N, "c": DEFAULT_C, "seed": DEFAULT_SEED, "rule": R_NODE, "mode": DEFAULT_MODE},
    "Knotenregel: die Hubs im Vorteil": {"netztyp": T_POWER, "n": DEFAULT_N, "c": DEFAULT_C, "seed": STORY_SEED, "rule": R_NODE, "mode": M_HUBS},
    "Invasionsregel: dieselben Hubs im Nachteil": {"netztyp": T_POWER, "n": DEFAULT_N, "c": DEFAULT_C, "seed": STORY_SEED, "rule": R_INVASION, "mode": M_HUBS},
    "Kantenregel: nur der Anteil zählt": {"netztyp": T_POWER, "n": DEFAULT_N, "c": DEFAULT_C, "seed": STORY_SEED, "rule": R_EDGE, "mode": M_HUBS},
    "Ring: die Regel ist egal": {"netztyp": T_RING, "n": DEFAULT_N, "c": DEFAULT_C, "seed": DEFAULT_SEED, "rule": R_NODE, "mode": M_HUBS},
    "Mehrheit am Rand verliert oft": {"netztyp": T_POWER, "n": DEFAULT_N, "c": DEFAULT_C, "seed": STORY_SEED, "rule": R_NODE, "mode": M_RIM},
}
PRESET_HELP = {
    "Zufallsnetz: die Hälfte gegen die Hälfte (Voreinstellung)": "Eine zufällige Hälfte beginnt mit Verfahren 1: der Konsens ist sicher, der Gewinner ein Münzwurf.",
    "Knotenregel: die Hubs im Vorteil": "Die zehn Hubs des Potenzgesetz-Netzes beginnen mit Verfahren 1: bei der Knotenregel haben sie das Gewicht ihrer Partnerzahl.",
    "Invasionsregel: dieselben Hubs im Nachteil": "Dasselbe Netz und derselbe Start, aber die Invasionsregel gewichtet mit 1 / Partnerzahl: die Hubs haben kaum eine Chance.",
    "Kantenregel: nur der Anteil zählt": "Dasselbe Netz und derselbe Start: bei der Kantenregel zählt jeder Betrieb gleich, die zehn Hubs haben die Chance 10 / n.",
    "Ring: die Regel ist egal": "Im fast regulären Ring sind alle Gewichte ähnlich: alle drei Regeln geben ungefähr dieselbe Chance.",
    "Mehrheit am Rand verliert oft": "Die Hälfte der Betriebe am Rand beginnt mit Verfahren 1, die Hubs mit 0: die Mehrheit gewinnt bei der Knotenregel weniger als in der Hälfte der Fälle.",
}
DEFAULT_PRESET_NAME = "Zufallsnetz: die Hälfte gegen die Hälfte (Voreinstellung)"
