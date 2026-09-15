###############################
# PySeA Workshop
###############################
# Aufgabe 1 – Minimalbeispiel
###############################

###############################
# Module einladen
###############################
from backend.facades import TestFacade #Import des Moduls "TestFacade" - darin sind alle Funktionen enthalten, die für die Erstellung eines Tests benötigt werden

###############################
# Test-Objekt erstellen & Test benennen
###############################
test = TestFacade(title = "Aufgabe 1 – Minimalbeispiel")

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
# Test erstellen und exportieren (*.zip Datei für Upload in ONYX)
###############################
test.create_test("examples/PySeA_workshop/output") # Relativer Pfad von dort, wo das Skript ausgeführt wird, zum Ordner, in dem die Testdatei erstellt werden soll


###############################
# Übungsaufgaben
###############################
# Aufgabe 1:
# - Erstellen Sie eine neue Sektion im Test mit einer Aufgabe, die zwei Lücken enthält.
# - Ändern Sie die Namen von: Test, Sektion und Aufgaben