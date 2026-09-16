###############################
# PySeA Workshop
###############################
# Aufgabe 1 – Minimalbeispiel
###############################

###############################
# Module einladen
###############################
# Projektordner (PySeA-public) als Suchpfad und Arbeitsordner setzen, damit das Skript auch
# ueber den Run-Button der IDE funktioniert (nicht nur mit "python -m ...")
import os, sys, pathlib
PROJEKT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJEKT))
os.chdir(PROJEKT)

from backend.facades import TestFacade #Import des Moduls "TestFacade" - darin sind alle Funktionen enthalten, die für die Erstellung eines Tests benötigt werden

###############################
# Test-Objekt erstellen & Test benennen
###############################
test = TestFacade(title = "Aufgabe 1 – Minimalbeispiel (Lösung)") # Erstellen eines Test-Objekts mit dem Titel "Aufgabe 1 – Minimalbeispiel (Lösung)"

###############################
# Struktur des Tests definieren
###############################
section_1 = test.add_section(title = "Minimalbeispiel") # Erstellen der Sektion "Minimalbeispiel"
task_1 = section_1.add_task(title = "Aufgabe 1") # Erstellen einer Aufgabe innerhalb der Sektion

###############################
# Aufgabe 1 editieren
###############################

# Antworten definieren
response_1 = task_1.response(5) # Erstellen einer Antwort/Lösung für eine Lücke mit dem Wert "5"

# Aufgabenkörper erstellen
task_1.item_body(
    "Eine kleine Rechenaufgabe:"+"\n"
    "$$2 + 3 = $$"+response_1) # Körper der Aufgabe mit Text und der Lücke, die mit der Variable "response_1" verknüpft ist
# Erklärung:
# "\n" -> Zeilenumbruch
# "$$...$$" -> LaTeX-Formatierung für mathematische Formeln
# "response_1" -> Variable, die die Antwort/Lösung für die Lücke enthält

###############################
# Sektion 2 mit Aufgabe 2 erstellen
###############################
section_2 = test.add_section(title = "Sektion 2") # Erstellen der Sektion "Sektion 2"
# Aufgabe 2 in Sektion 2 erstellen
task_2 = section_2.add_task(title = "Aufgabe 2") # Erstellen der Aufgabe 2 innerhalb der Sektion 2


###############################
# Aufgabe 2 editieren
###############################
# 2 Antworten definieren
response_2 = task_2.response(100) # Erstellen einer Antwort/Lösung "response_2"
response_3 = task_2.response(1000) # Erstellen einer Antwort/Lösung "response_3"

# Aufgabenkörper erstellen
task_2.item_body(
    "Zehnerpotenzen:"+"\n"
    "$$10^2 = $$"+ response_2 +"\n"
    "$$10^3 = $$"+ response_3 )


###############################
# Test erstellen und exportieren (*.zip Datei für Upload in ONYX)
###############################
test.create_test("examples/PySeA_workshop/output") # Relativer Pfad von dort, wo das Skript ausgeführt wird, zum Ordner, in dem die Testdatei erstellt werden soll


###############################
# Übungsaufgaben
###############################
# Aufgabe 1:
# - Erstellen Sie eine neue Sektion im Test mit einer Aufgabe, die zwei Lücken enthält.
# - Ändern Sie die Namen von: Test, Sektion und Aufgaben