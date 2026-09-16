# PySeA Workshop

Willkommen zum **PySeA Workshop**! Dieser Ordner enthält eine Sammlung von Beispielskripten, die die grundlegenden und fortgeschrittenen Funktionen von **PySeA** (Python Scripted e-Assessment) demonstrieren. Die Beispiele sind so strukturiert, dass Sie schrittweise die Möglichkeiten von PySeA kennenlernen: von einfachen Tests bis hin zu komplexen, variantenabhängigen Aufgaben mit Bildern, Tabellen und Feedback.

---

## 📌 Inhaltsverzeichnis

- **[Vortragsfolien](PySeA.pdf)**: Folien zur PySeA-Vorstellung beim 27. Netzwerktreffen Mathematik/Physik + E-Learning (17.09.2026)
- **[PySeA-Setup](#pysea-setup)**: Installation und Grundeinrichtung
- **[PySeA-Hilfe](../README.md)**: Handbuch mit allen Funktionen und dem allgemeinen Workflow

### Aufgaben
1. **[Minimalbeispiel](#1-minimalbeispiel)**: Einfache Teststruktur mit einer Rechenaufgabe
2. **[Feedback & Bilder](#2-feedback--bilder)**: Erweiterung um Bilder und Feedback für richtige/falsche Antworten
3. **[Tabellen & Excel](#3-tabellen--excel)**: Tabellen aus Excel-Dateien einbinden
4. **[Varianten](#4-varianten)**: Variantenabhängige Aufgaben mit Excel-Daten

---

## PySeA-Setup

### ⚡ Schnellstart

Führen Sie diese Schritte im Terminal aus (Windows: PowerShell). Danach können Sie die Skripte in Ihrer IDE (z. B. **VS Code** oder **PyCharm**) bearbeiten.

#### 1️⃣ Repository klonen

```bash
cd /Pfad/zu/Ihrem/Arbeitsordner
git clone https://github.com/i4s-htwk/PySeA-public.git
cd PySeA-public
```

Ohne Git: auf GitHub über **Code > Download ZIP** herunterladen und entpacken.

#### 2️⃣ Virtuelle Umgebung erstellen und aktivieren

Die Workshop-Skripte laufen mit **Python 3.11 bis 3.14** (getestet). Falls Sie noch kein Python haben: aktuelle Version von [python.org](https://www.python.org/downloads/) installieren, unter Windows dabei die Option „Add python.exe to PATH“ anhaken.

| | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Umgebung erstellen | `py -m venv .venv` | `python3 -m venv .venv` |
| Umgebung aktivieren | `.\.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |

Hinweis für Windows: Blockiert PowerShell die Aktivierung, hilft für die aktuelle Sitzung `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

#### 3️⃣ Pakete installieren

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-workshop.txt
```

Die Datei `requirements-workshop.txt` enthält genau die fünf Pakete, die die Skripte brauchen (Installation dauert etwa eine Minute). Die große `requirements.txt` im Projektordner ist nur für die grafische Oberfläche und die Entwicklung nötig.

#### 4️⃣ Skripte ausführen

- Die Skripte liegen im Ordner **`examples/PySeA_workshop/`** (`aufgabe_1.py` bis `aufgabe_4.py`).
- Ausführen **aus dem Projektordner `PySeA-public`** heraus, z. B.:
  `python -m examples.PySeA_workshop.aufgabe_1`
  (unter macOS/Linux ggf. `python3` statt `python`)
- Alternativ in der IDE über den Run-Button: Die Skripte legen am Anfang das Projektverzeichnis als Arbeitsordner und Suchpfad fest, damit `backend` gefunden wird.
- **Ausgabe:** Im Ordner `examples/PySeA_workshop/output/` entstehen eine `.zip`-Datei (der Test) und eine `.json`-Datei (zum Weiterbearbeiten mit PySeA).
- **Upload:** Laden Sie die `.zip`-Datei in **ONYX** hoch, um den Test zu nutzen.

---

## Aufgaben

### 1. Minimalbeispiel

**Ziel:** Erstellen eines einfachen Tests mit einer Rechenaufgabe.

**Lerninhalte:**
- Import der `TestFacade`
- Struktur eines Tests (Test → Sektion → Aufgabe)
- Erstellen von Antwortlücken (`response`)
- Formatierung mit LaTeX (`$$...$$`)

**Übungsaufgaben:**
- Erstellen Sie eine neue Sektion im Test mit einer Aufgabe, die zwei Lücken enthält.
- Ändern Sie die Namen von Test, Sektion und Aufgaben.

📄 **Datei:** [aufgabe_1.py](aufgabe_1.py)

---

### 2. Feedback & Bilder

**Ziel:** Erweiterung des Tests um **Bilder** und **Feedback** für richtige/falsche Antworten.

**Lerninhalte:**
- Bilder laden und einbinden (`test.load_images()`)
- Bildgröße anpassen (`set_width()`)
- Feedback für korrekte (`correct`) und inkorrekte (`incorrect`) Antworten

**Übungsaufgaben:**
- Fügen Sie die Bilder `Feedback_falsch.jpg` und `Feedback_korrekt.png` aus dem Ordner `examples/PySeA_workshop/files` dem jeweiligen Feedback hinzu.
- Erstellen Sie innerhalb des Skripts `aufgabe_2.py` eine Darstellung einer Parabel (z. B. mit Matplotlib) und binden Sie diese als neue Aufgabe ein.

📄 **Datei:** [aufgabe_2.py](aufgabe_2.py)

---

### 3. Tabellen & Excel

**Ziel:** Dynamische Tabellen aus **Excel-Dateien** einbinden und Werte abfragen.

**Lerninhalte:**
- Tabellen in Aufgaben einbinden (`task_1.table("excelTable")`)
- Bereiche aus Excel-Dateien definieren (`add_area()`)
- Werte aus der Tabelle lesen (statt manuell zu berechnen)
- Excel-Dateien mit `openpyxl` erstellen

**Übungsaufgaben:**
- Verringern Sie den Bereich der Tabelle, sodass nur die Variablen A, B, C und D sichtbar sind. Fragen Sie entsprechend nach Produkten dieser Variablen und greifen Sie die Lösung aus der Tabelle ab.
- Erstellen Sie die Tabelle innerhalb des Skripts `aufgabe_3.py` (z. B. mit `openpyxl`, vgl. `aufgabe_3_zusatz_excel-in-python.py`) und nutzen Sie diese in der Aufgabe.

📄 **Datei:** [aufgabe_3.py](aufgabe_3.py)

---

### 4. Varianten

**Ziel:** **Variantenabhängige Aufgaben** erstellen, bei denen Teilnehmende ihre Variante eingeben und unterschiedliche Werte erhalten.

**Lerninhalte:**
- Testwegsteuerung aktivieren (`set_navigation_mode("test_path_control")`)
- Varianten manuell zuweisen (`variants("manual_assignment")`)
- Excel-Daten für Variablen und Ergebnisse nutzen
- Dynamische Zuordnung von Variablen und Ergebnissen pro Variante

**Übungsaufgaben:**
- Erweitern Sie die Anzahl der Varianten auf 3 (die Excel-Datei enthält bereits drei Spalten).
- Fragen Sie das Ergebnis $$B \cdot C$$ variantenabhängig ab.

📄 **Datei:** [aufgabe_4.py](aufgabe_4.py)

---


## 🔧 Technische Hinweise

### Pfade anpassen
- **Bilder:** Legen Sie Bilder im Ordner `examples/PySeA_workshop/files/` ab und passen Sie den Pfad ggf. in `test.load_images()` an.
- **Excel-Dateien:** Speichern Sie Excel-Dateien im selben Ordner und aktualisieren Sie ggf. den Pfad in `excel_file = ...`.
- **Ausgabe:** Der Pfad in `test.create_test()` muss ein **vorhandener Ordner** sein (z. B. `examples/PySeA_workshop/output/`).
- **Testtitel:** Der Titel wird zum Dateinamen der Zip-Datei. Verwenden Sie keine Zeichen wie `:`, `/` oder `\` im Titel.

### Häufige Fehler
| Problem | Lösung |
|---------|--------|
| `ModuleNotFoundError: backend` | Skript aus dem Projektordner `PySeA-public` starten (`python -m examples.PySeA_workshop.aufgabe_1`), nicht aus `examples/` heraus |
| `pip` bricht bei `numpy` mit einem Build-Fehler ab | Es wurde `requirements.txt` statt `requirements-workshop.txt` installiert; für den Workshop reicht die kleine Liste |
| Bilder werden nicht angezeigt | Pfad in `test.load_images()` prüfen und sicherstellen, dass die Bilder im Ordner liegen |
| Excel-Datei nicht gefunden | Pfad prüfen; das Skript muss aus dem Projektordner heraus laufen |
| `KeyError` bei `images["..."]` | Dateiname inklusive Endung exakt wie im Ordner angeben (z. B. `Feedback_korrekt.png`) |

---
*Letzte Aktualisierung: 2026-09-16*
