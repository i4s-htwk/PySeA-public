###############################
# PySeA Workshop
###############################
# Aufgabe 3 – Tabellen & Excel
###############################

###############################
# Module einladen
###############################
from openpyxl import load_workbook # Import des Moduls "load_workbook" aus der Bibliothek "openpyxl" - damit können Excel-Dateien gelesen werden
from backend.facades import TestFacade #Import des Moduls "TestFacade" - darin sind alle Funktionen enthalten, die für die Erstellung eines Tests benötigt werden

###############################
# Test-Objekt erstellen & Test benennen
###############################
test = TestFacade(title = "Aufgabe 3 – Tabellen & Excel")

###############################
# Struktur des Tests erweitern
###############################
section_1 = test.add_section(title = "Tabelle aus Excel-Datei")
task_1 = section_1.add_task(title = "Aufgabe 1")

###############################
# Aufgabe 1 editieren
###############################

# Tabelle aus Excel-Datei erstellen
excel_file = "examples/PySeA_workshop/files/produkte_tabelle.xlsx" # Pfad zur Excel-Datei

table = task_1.table("excelTable") # Tabelle als "excelTable" erstellen
table.excel_file = excel_file # Excel-Datei zuweisen
table.page = "Produkte" # Verwendetes Blatt in der Excel-Datei angeben
area = table.add_area("A1", "D4") # Bereich der Tabelle angeben, der in der Aufgabe angezeigt werden soll (von Zelle A1 bis D4)

# Feste Werte aus Excel einlesen. Dadurch werden keine Varianten benötigt.
workbook = load_workbook(excel_file, data_only=True)
worksheet = workbook["Produkte"]
A, B, C, D, E, F = (worksheet[cell].value for cell in ("B5", "B6", "B7", "B8", "B9", "B10"))
workbook.close()


# Antworten definieren
response_1_1 = task_1.response(A * F) # Erste Antwortlücke der Aufgabe 1
response_1_2 = task_1.response(B * E) # Zweite Antwortlücke der Aufgabe 1
response_1_3 = task_1.response(C * D) # Dritte Antwortlücke der Aufgabe 1


# Aufgabenkörper 
task_1.item_body(
    "Gegeben sind die folgenden Variablen: \n"+
    "$$A="+str(A) + "$$ \n" +
    "$$B="+str(B) + "$$ \n" +
    "$$C="+str(C) + "$$ \n" +
    "$$D="+str(D) + "$$ \n" +
    "$$E="+str(E) + "$$ \n" +
    "$$F="+str(F) + "$$ \n" +
    "Die folgende Tabelle zeigt die Produkte der entsprechenden Spalten- und Zeilenvariable" +
    area + "\n" +
    "Lesen Sie daraus die folgenden Produkte ab: \n"+
    "$$A \cdot F = $$"+response_1_1 + "\n" +
    "$$B \cdot E = $$"+response_1_2 + "\n" +
    "$$C \cdot D = $$"+response_1_3 + "\n"
)

###############################
# Test erstellen und exportieren (*.zip Datei für Upload in ONYX)
###############################
test.create_test("examples/PySeA_workshop/output/")


###############################
# Übungsaufgaben
###############################
# Aufgabe 1:
# - Verringern Sie den Bereich der Tabelle, sodass nur die Bereiche der Variablen "A", "B", "D" und "C" in der Aufgabe sichtbar sind und fragen Sie entsprechend nach Produkten dieser Variablen und greifen Sie die entsprechende Lösung aus der Tabelle ab
# - Erstellen Sie die Tabelle innerhalb des Pythonskripts (z. B. mit Hilfe der openpyxl-Bibliothek, vgl. auch "aufgabe_3_zusatz_excel-in-python.py") und nutzen Sie diese in der Aufgabe