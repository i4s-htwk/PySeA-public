# PySeA

PySeA ist ein Python-basiertes Programm zur Erstellung von Tests für ONYX. Die
erstellten Tests werden als ZIP-Datei exportiert und können anschließend in ONYX
bzw. OPAL importiert werden.

Das Programm unterstützt zwei Wege zur Testerstellung:

1. Grafische Testerstellung über eine Benutzeroberfläche
2. Skriptbasierte Testerstellung über Python

* * *

## Voraussetzungen

- Python 3.12
- Git
- pip (wird normalerweise zusammen mit Python installiert)

Es wird empfohlen, PySeA in einer virtuellen Python-Umgebung (`.venv`)
auszuführen.

* * *

## Installation

Alle Befehle werden im Terminal (Windows: PowerShell) ausgeführt.

|  | Schritt | Windows (PowerShell)                              | macOS / Linux                                     |
| - | --- |---------------------------------------------------|---------------------------------------------------|
| 1 | Repository klonen | `git clone https://github.com/i4s-htwk/PySeA-public.git` | `git clone https://github.com/i4s-htwk/PySeA-public.git` |
| 2 | Projektordner öffnen | `cd PySeA-public`                                | `cd PySeA-public`                                |
| 3 | Virtuelle Umgebung erstellen | `py -3.12 -m venv .venv`                          | `python3.12 -m venv .venv`                        |
| 4 | Virtuelle Umgebung aktivieren | `.\.venv\Scripts\Activate.ps1`                    | `source .venv/bin/activate`                       |
| 5 | pip aktualisieren | `python -m pip install --upgrade pip`             | `python -m pip install --upgrade pip`             |
| 6 | Abhängigkeiten installieren | `python -m pip install -r requirements.txt`       | `pip install -r requirements.txt`                 |

Hinweis für Windows: Falls PowerShell die Aktivierung der virtuellen Umgebung aufgrund der Ausführungsrichtlinie blockiert, kann diese für die aktuelle PowerShell-Sitzung temporär angepasst werden:
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Anschließend kann die virtuelle Umgebung erneut aktiviert werden. (Schritt 4)
***

## Verwendung

Vor jeder Nutzung muss die virtuelle Umgebung aktiviert sein (Schritt 4).

### Grafische Benutzeroberfläche

Über die grafische Benutzeroberfläche können Tests ohne eigenes Python-Skript
erstellt und bearbeitet werden.

```bash
python app.py
```

Nach dem Start wird die Adresse der Benutzeroberfläche im Terminal angezeigt
(z. B. `http://127.0.0.1:5000`) und kann im Browser geöffnet werden. 

Beenden mit `Strg + C` im Terminal.

### Skriptbasierte Testerstellung

Alternativ können Tests direkt über Python erstellt werden. Vollständige
Beispielskripte liegen im Ordner [examples](examples). Sie zeigen verschiedene Funktionen
von PySeA und können direkt ausgeführt oder als Ausgangspunkt für eigene Tests
verwendet werden.

Im selben Ordner befindet sich eine [README.md](examples/README.md), die sämtliche Funktionalitäten
des Programms erklärt.

Ein Skript wird wie ein gewöhnliches Python-Skript im Terminal ausgeführt, z. B.:

```bash
python examples/script1.py
```

Der erstellte Test wird dabei als ZIP-Datei exportiert und kann anschließend
in ONYX bzw. OPAL importiert werden.

* * *

## Projektstruktur

```
PySeA/
├── backend/          # Programmlogik und Erstellung der Testpakete
├── frontend/         # Grafische Benutzeroberfläche
├── examples/         # Beispiele für die skriptbasierte Testerstellung
├── tests/            # Unit- und Integrationstests
└── app.py            # Startpunkt der grafischen Benutzeroberfläche
```

---

## Autoren

- [Kjell Bühler](https://github.com/kjellbuehler) (@kjellbuehler)
- [Julian Schmidt](https://github.com/julian-schmidt02) (@julian-schmidt02)

---

## Mitwirken

Wir freuen uns über Beiträge! Bitte halte dich an unsere [Entwicklungsrichtlinien](CONTRIBUTING.md), um die Code-Qualität zu sichern.

---

## Lizenz

Dieses Projekt ist unter der GNU Affero General Public License v3.0 (AGPL-3.0) lizenziert. Details sind in der [LICENSE.txt](LICENSE.txt) zu finden.
