# PySeA Workshop

Willkommen zum **PySeA Workshop**! Dieser Ordner enthält eine Sammlung von Beispielskripten, die die grundlegenden und fortgeschrittenen Funktionen von **PySeA** (Python-Based ONYX Test Generator) demonstrieren. Die Beispiele sind so strukturiert, dass Sie schrittweise die Möglichkeiten von PySeA kennenlernen – von einfachen Tests bis hin zu komplexen, variantenabhängigen Aufgaben mit Bildern, Tabellen und Feedback.

---

## 📌 Inhaltsverzeichnis

- **[PySeA-Setup](#pysea-setup)** – Installation und Grundeinrichtung

### Aufgaben
1. **[Minimalbeispiel](#1-minimalbeispiel)** – Einfache Teststruktur mit einer Rechenaufgabe
2. **[Feedback & Bilder](#2-feedback--bilder)** – Erweiterung um Bilder und Feedback für richtige/falsche Antworten
3. **[Tabellen & Excel](#3-tabellen--excel)** – Tabellen aus Excel-Dateien einbinden
4. **[Varianten](#4-varianten)** – Variantenabhängige Aufgaben mit Excel-Daten
5. **[Grafische Zuordnung](#5-grafische-zuordnung)** – (Inhalt folgt)

---

## PySeA-Setup

### ⚡ Schnellstart

Führen Sie diese Schritte aus, um PySeA in Ihrer IDE (z. B. **PyCharm**, **VS Code**, **Jupyter Notebook**) einzurichten:

#### 1️⃣ Repository klonen
cd /Pfad/zu/Ihrem/Arbeitsordner
git clone https://github.com/i4s-htwk/PySeA.git

#### 2️⃣ Abhängigkeiten installieren
`cd PySeA`

##### Virtuelle Umgebung erstellen und aktivieren (empfohlen, um Konflikte zu vermeiden)
`python -m venv venv`

`source venv/bin/activate  # Linux/Mac`

`venv\Scripts\activate     # Windows`

##### Installieren Sie die benötigten Pakete (Python 3.8+ empfohlen)
`pip install -r requirements.txt`

#### 3️⃣ Skripte ausführen
- Legen Sie Ihre Skripte (z. B. `aufgabe_1.py`) im Ordner **`examples/PySeA_workshop/`** ab.
- Führen Sie das Skript aus:z.B.:
  `python3 -m examples.PySeA_workshop.aufgabe_1`
- **Ausgabe:** Eine `.zip`-Datei wird im angegebenen Pfad erstellt (z. B. `output/aufgabe_1.zip`).
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
- Ändern Sie die Namen von: Test, Sektion und Aufgaben

📄 **Datei:** [aufgabe_1.py](aufgabe_1.py)

---

### 2. Feedback & Bilder

**Ziel:** Erweiterung des Tests um **Bilder** und **Feedback** für richtige/falsche Antworten.

**Lerninhalte:**
- Bilder laden und einbinden (`test.load_images()`)
- Bildgröße anpassen (`set_width()`)
- Feedback für korrekte (`correct`) und inkorrekte (`incorrect`) Antworten

**Übungsaufgaben:**
- Fügen Sie die Bilder "Feedback_falsch.jpg" und "Feedback_korrekt.jpg" aus dem "examples/PySeA_workshop/files" Ordner dem entsprechenden Feedback hinzu.
- Erstellen Sie innerhalb des Pythonskripts "aufgabe_2.py" eine Darstellung einer Parabel (z. B. mit Matplotlib) und binden Sie diese als neue Aufgabe ein

📄 **Datei:** [aufgabe_2.py](aufgabe_2.py)

---

### 3. Tabellen & Excel

**Ziel:** Dynamische Tabellen aus **Excel-Dateien** einbinden und Werte abfragen.

**Lerninhalte:**
- Tabellen in Aufgaben einbinden (`task_3.table()`)
- Bereiche aus Excel-Dateien definieren (`add_area()`)
- Werte aus Tabellen ablesen (statt manuell zu berechnen)
- Excel-Dateien mit `openpyxl` erstellen

**Übungsaufgaben:**
- Verringern Sie den Bereich der Tabelle, sodass nur die Bereiche der Variablen "A", "B", "D" und "C" in der Aufgabe sichtbar sind und fragen Sie entsprechend nach Produkten dieser Variablen und greifen Sie die entsprechende Lösung aus der Tabelle ab
- Erstellen Sie die Tabelle innerhalb des Pythonskripts "aufgabe_3.py" (z. B. mit Hilfe der openpyxl-Bibliothek, vgl. auch "aufgabe_3_zusatz_excel-in-python.py") und nutzen Sie diese in der Aufgabe

📄 **Datei:** [aufgabe_3.py](aufgabe_3.py)

---
### 4. Varianten

**Ziel:** **Variantenabhängige Aufgaben** erstellen, bei denen Nutzer:innen ihre Variante eingeben und unterschiedliche Werte erhalten.

**Lerninhalte:**
- Testwegsteuerung aktivieren (`set_navigation_mode("test_path_control")`)
- Varianten manuell zuweisen (`variants("manual_assignment")`)
- Excel-Daten für Variablen und Ergebnisse nutzen
- Dynamische Zuordnung von Variablen/Ergebnissen pro Variante

**Übungsaufgaben:**
- Erweitern Sie die Anzahl der Varianten auf 3
- Fragen Sie das Ergebnis $$B \cdot C$$ variantenabhängig ab

📄 **Datei:** [aufgabe_4.py](aufgabe_4.py)

---
### 5. Grafische Zuordnung

**Ziel:** (Inhalt folgt – bitte ergänzen Sie die Beschreibung und den Code für diese Aufgabe.)

**Lerninhalte:**


**Übungsaufgaben:**
- Platzhalter für spätere Fragen zu Aufgabe 5

📄 **Datei:** [aufgabe_5.py](aufgabe_5.py)

---
---
## 🔧 Technische Hinweise

### Pfade anpassen
- **Bilder:** Legen Sie Bilder im Ordner `examples/PySeA_workshop/files/` ab und passen Sie den Pfad  ggf. in `test.load_images()` an.
- **Excel-Dateien:** Speichern Sie Excel-Dateien im selben Ordner und aktualisieren Sie ggf. den Pfad in `excel_file = ...`.
- **Ausgabe:** Der Pfad in `test.create_test()` muss ein **vorhandener Ordner** sein (z. B. `output/`)
### Häufige Fehler
| Problem | Lösung |
|---------|--------|
| `ModuleNotFoundError: backend` | Führen Sie das Skript aus dem **PySeA-Stammverzeichnis** aus (nicht aus `examples/`) |
| Bilder werden nicht angezeigt | Prüfen Sie den Pfad in `test.load_images()` und stellen Sie sicher, dass die Bilder im Ordner liegen |
| Excel-Datei nicht gefunden | Prüfen Sie den Pfad und die Schreibrechte |

---
*Letzte Aktualisierung: [Datum] | *Autor: [Ihr Name]*