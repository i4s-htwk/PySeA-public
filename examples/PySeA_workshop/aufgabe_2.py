###############################
# PySeA Workshop
###############################
# Aufgabe 2 – Feedback & Bilder
###############################

###############################
# Module einladen
###############################
# Projektordner (PySeA-public) als Suchpfad und Arbeitsordner setzen, damit das Skript auch
# ueber den Run-Button der IDE funktioniert (nicht nur mit "python -m ...")
import os, sys, pathlib
PROJEKT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJEKT))
os.chdir(PROJEKT)

from backend.facades import TestFacade #Import des Moduls "TestFacade" - darin sind alle Funktionen enthalten, die für die Erstellung eines Tests benötigt werden

###############################
# Test-Objekt erstellen & Test benennen
###############################
test = TestFacade(title = "Aufgabe 2 – Feedback & Bilder")

###############################
# Bilder einladen
###############################
# Lädt alle Bilddateien aus dem Ordner `examples/PySeA_workshop/files` in das Testobjekt.
# `.map()` erstellt eine dictionary-ähnliche Struktur, sodass auf Bilder über den Dateinamen zugegriffen werden kann, z. B.: images["Bild_1.png"]
# Bilder können dann einfach über images["Bildername"] eingebunden werden, z.B. in der Aufgabe oder im Feedback.
images = test.load_images("examples/PySeA_workshop/files").map()
# Breite aller Bilder auf 400 Pixel setzen (optional)
for key, value in images.items():
    value.set_width("400")

###############################
# Struktur des Tests definieren
###############################
section_1 = test.add_section(title = "Bilder und Feedback") # Erstellen der Sektion "Bilder und Feedback"
task_1 = section_1.add_task(title = "Aufgabe 1") # Erstellen einer Aufgabe innerhalb der Sektion

###############################
# Aufgabe 1 editieren
###############################

# Variablen (Das sind noch keine ONYX-Variablen, sondern Python-Variablen, die in der Aufgabe verwendet werden können)
a=2
b=3
c=4

# Antworten
response_1 = task_1.response(a*b*c) # Erstellen einer Antwort/Lösung mit dem Wert "a*b*c"

# Aufgabenkörper mit Text, Variablen, Bildern und Antwortlücke erstellen
task_1.item_body(
    "Bestimmen Sie das Volumen des gezeigten Körpers \n"+
    "$$a=$$"+str(a) + "\n" +
    "$$b=$$"+str(b) + "\n" +
    "$$c=$$"+str(c) + "\n" +
    images["Bild_1.png"] + "\n"
    "Das Ergebnis lautet "+response_1)

# Feedback definieren
# korrekte Antworten
task_1.feedback("correct", "Sehr gut, das war korrekt!")

# falsche Antworten
task_1.feedback("incorrect", "Das war leider falsch. Versuchen Sie es noch einmal!")

###############################
# Test erstellen und exportieren (*.zip Datei für Upload in ONYX)
###############################
test.create_test("examples/PySeA_workshop/output/") # Relativer Pfad von dort, wo das Skript ausgeführt wird, zum Ordner, in dem die Testdatei erstellt werden soll


###############################
# Übungsaufgaben
###############################
# Aufgabe 1:
# - Fügen Sie die Bilder "Feedback_falsch.jpg" und "Feedback_korrekt.png" aus dem "examples/PySeA_workshop/files" Ordner dem entsprechenden Feedback hinzu.
# - Erstellen Sie innerhalb des Pythonskripts eine Darstellung einer Parabel (z. B. mit Matplotlib) und binden Sie diese als neue Aufgabe ein