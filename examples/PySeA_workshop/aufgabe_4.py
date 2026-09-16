###############################
# PySeA Workshop
###############################
# Aufgabe 4 – Varianten
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
test = TestFacade(title = "Aufgabe 4 – Varianten")

settings = test.get_settings()
settings.set_navigation_mode("test_path_control")

###############################
# Varianten aktivieren und definieren
###############################

variants = test.variants("manual_assignment")
variants.assignment.count_variants = 2
variants.item_body = "Geben Sie ihre Variante ein: {RESPONSE}"

# Feedback definieren um die gewählte Variante anzuzeigen
# korrekte Antworten
variants.set_feedback("Sie haben Variante {Variante} gewählt.", "feedback_correct") # {Variante} ist die gewählte Variante
# falsche Antworten
variants.set_feedback("Ungültige Eingabe. Wählen Sie eine gültige Variante. (1-"+str(variants.assignment.count_variants)+")", "feedback_incorrect") # 1 bis {count} ist die Anzahl der Varianten, die in der Aufgabe definiert wurden.

###############################
# Struktur des Tests definieren
###############################
section_1 = test.add_section(title = "Varianten")
task_1 = section_1.add_task(title = "Aufgabe 4")

###############################
# Aufgabe 1 editieren
###############################
excel_file = "examples/PySeA_workshop/files/var_ergebnisse.xlsx" # Pfad zur Excel-Datei

# Variantenabhängige Variablen aus Excel-Datei erstellen
###############################
excel_variablen = task_1.add_excel_variables()
excel_variablen.excel_file = excel_file # Excel-Datei zuweisen
excel_variablen.page = "Ergebnisse" # Verwendetes Blatt in der Excel-Datei angeben

excel_variablen.add_variable("B2") # Variable A, gespeichert als excel_variablen.variables[0]
excel_variablen.add_variable("B3") # Variable B, gespeichert als excel_variablen.variables[1]
excel_variablen.add_variable("B4") # Variable C, gespeichert als excel_variablen.variables[2]

# Variantenabhängige Antworten aus Excel-Datei erstellen
###############################
excel_responses = task_1.excel_responses()
excel_responses.excel_file = excel_file # Excel-Datei zuweisen
excel_responses.page = "Ergebnisse" # Verwendetes Blatt in der Excel-Datei angeben
excel_responses.add_response("B5") # Antwort 1, gespeichert als excel_responses.responses[0]
excel_responses.add_response("B6") # Antwort 2, gespeichert als excel_responses.responses[1]


# Aufgabenkörper
task_1.item_body(
    "Ihre Variablen lauten:\n" +
    "$$A = " + str(excel_variablen.variables[0]) + "$$ \n" +
    "$$B = " + str(excel_variablen.variables[1]) + "$$ \n" +
    "$$C = " + str(excel_variablen.variables[2]) + "$$ \n" +
    "Lösen Sie die folgenden Aufgaben:\n" +
    "$$(A + B) \\cdot C = $$" + str(excel_responses.responses[0]) + "\n" +
    "$$A + B \\cdot C = $$" + str(excel_responses.responses[1]) + "\n"
)

###############################
# Test erstellen und exportieren (*.zip Datei für Upload in ONYX)
###############################
test.create_test("examples/PySeA_workshop/output/")


###############################
# Übungsaufgaben
###############################
# Aufgabe 1:
# - Erweitern Sie die Anzahl der Varianten auf 3
# - Fragen Sie das Ergebnis $$B \cdot C$$ variantenabhängig ab
