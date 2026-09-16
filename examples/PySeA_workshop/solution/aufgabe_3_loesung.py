###############################
# PySeA Workshop
###############################
# Aufgabe 3 – Tabellen & Excel
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

from openpyxl import load_workbook # Import des Moduls "load_workbook" aus der Bibliothek "openpyxl" - damit können Excel-Dateien gelesen werden
from backend.facades import TestFacade #Import des Moduls "TestFacade" - darin sind alle Funktionen enthalten, die für die Erstellung eines Tests benötigt werden

###############################
# Test-Objekt erstellen & Test benennen
###############################
test = TestFacade(title = "Aufgabe 3 – Tabellen & Excel (Lösung)")

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
area = table.add_area("A1", "C3") # Bereich der Tabelle angeben, der in der Aufgabe angezeigt werden soll

# Feste Werte aus Excel einlesen. Dadurch werden keine Varianten benötigt.
workbook = load_workbook(excel_file, data_only=True)
worksheet = workbook["Produkte"]
A, B, C, D, E, F = (worksheet[cell].value for cell in ("B5", "B6", "B7", "B8", "B9", "B10"))
workbook.close()


# Antworten definieren
response_1_1 = task_1.response(A * E) # Erste Antwortlücke der Aufgabe 1
response_1_2 = task_1.response(B * D) # Zweite Antwortlücke der Aufgabe 1
response_1_3 = task_1.response(B * E) # Dritte Antwortlücke der Aufgabe 1


# Aufgabenkörper 
task_1.item_body(
    "Gegeben sind die folgenden Variablen: \n"+
    "$$A="+str(A) + "$$ \n" +
    "$$B="+str(B) + "$$ \n" +
    "$$D="+str(D) + "$$ \n" +
    "$$E="+str(E) + "$$ \n" +
    "Die folgende Tabelle zeigt die Produkte der entsprechenden Spalten- und Zeilenvariable" +
    area + "\n" +
    "Lesen Sie daraus die folgenden Produkte ab: \n"+
    "$$A \cdot E = $$"+response_1_1 + "\n" +
    "$$B \cdot D = $$"+response_1_2 + "\n" +
    "$$B \cdot E = $$"+response_1_3 + "\n"
)


###############################
# Aufgabe 2 erstellen mit einer Tabelle, die innerhalb des Pythonskripts erstellt wird
###############################

task_2 = section_1.add_task(title = "Aufgabe 2 (Quotienten)")

###############################
# Excel-Datei erstellen
###############################
from openpyxl import Workbook
from openpyxl.styles import numbers


# Variablen für Spalten und Zeilen
A, B, C = 1,2,3
D, E, F = 4,5,6

# Excel-Datei erstellen
wb = Workbook()
ws = wb.active

# Blatt umbenennen
ws.title = "Quotienten"

# Spalten- und Zeilenüberschriften schreiben
ws['B1'] = '$$A$$'
ws['C1'] = '$$B$$'
ws['D1'] = '$$C$$'
ws['A2'] = '$$D$$'
ws['A3'] = '$$E$$'
ws['A4'] = '$$F$$'
ws['A5'] = 'Variable A = '
ws['A6'] = 'Variable B = '
ws['A7'] = 'Variable C = '
ws['A8'] = 'Variable D = '
ws['A9'] = 'Variable E = '
ws['A10'] = 'Variable F = '

# Variablen in die Tabelle schreiben
ws['B5'] = A
ws['B6'] = B
ws['B7'] = C
ws['B8'] = D
ws['B9'] = E
ws['B10'] = F

# Produkte berechnen und in die Tabelle schreiben
ws['B2'] = A / D
ws['C2'] = B / D
ws['D2'] = C / D

ws['B3'] = A / E
ws['C3'] = B / E
ws['D3'] = C / E

ws['B4'] = A / F
ws['C4'] = B / F
ws['D4'] = C / F

# Formatierung für Nachkommastellen anwenden
for row in ws.iter_rows(min_row=2, max_row=4, min_col=2, max_col=4):
    for cell in row:
        cell.number_format = numbers.FORMAT_NUMBER_00

# Excel-Datei speichern
excel_file_2 = "examples/PySeA_workshop/files/quotienten_tabelle.xlsx"# Pfad zur Excel-Datei
wb.save(excel_file_2)
print("Excel-Datei wurde erstellt: quotienten_tabelle.xlsx")
###############################


# Tabelle aus Excel-Datei erstellen
table_2 = task_2.table("excelTable") # Tabelle als "excelTable" erstellen
table_2.excel_file = excel_file_2 # Excel-Datei zuweisen
table_2.page = "Quotienten" # Verwendetes Blatt in der Excel-Datei angeben
area = table_2.add_area("A1", "D4") # Bereich der Tabelle angeben, der in der Aufgabe angezeigt werden soll (von Zelle A1 bis D4)

# Feste Werte aus Excel einlesen. Dadurch werden keine Varianten benötigt.
workbook = load_workbook(excel_file_2, data_only=True)
worksheet = workbook["Quotienten"]
A, B, C, D, E, F = (worksheet[cell].value for cell in ("B5", "B6", "B7", "B8", "B9", "B10"))
workbook.close()


# Antworten definieren
response_2_1 = task_2.response(A / F) # Erste Antwortlücke der Aufgabe 2
response_2_2 = task_2.response(B / E) # Zweite Antwortlücke der Aufgabe 2
response_2_3 = task_2.response(C / D) # Dritte Antwortlücke der Aufgabe 2


# Aufgabenkörper 
task_2.item_body(
    "Gegeben sind die folgenden Variablen: \n"+
    "$$A="+str(A) + "$$ \n" +
    "$$B="+str(B) + "$$ \n" +
    "$$C="+str(C) + "$$ \n" +
    "$$D="+str(D) + "$$ \n" +
    "$$E="+str(E) + "$$ \n" +
    "$$F="+str(F) + "$$ \n" +
    "Die folgende Tabelle zeigt die Quotienten der ersten Zeile (Dividend) und ersten Spalte (Divisor) " +
    area + "\n" +
    "Lesen Sie daraus die folgenden Quotienten ab: \n"+
    "$$A / F = $$"+response_2_1 + "\n" +
    "$$B / E = $$"+response_2_2 + "\n" +
    "$$C / D = $$"+response_2_3 + "\n"
)




###############################
# Test erstellen und exportieren (*.zip Datei für Upload in ONYX)
###############################
test.create_test("examples/PySeA_workshop/output/")


###############################
# Übungsaufgaben
###############################
# Aufgabe 1:
# - Verringern Sie den Bereich der Tabelle, sodass nur die Bereiche der Variablen "A", "B", "D" und "C" in der Aufgabe sichtbar sind und fragen Sie nach Produkten dieser Variablen und greifen Sie die entsprechende Lösung aus der Tabelle ab
# - Erstellen Sie die Tabelle innerhalb des Pythonskripts (z. B. mit Hilfe der openpyxl-Bibliothek, vgl. auch "aufgabe_3_zusatz_excel-in-python.py") und nutzen Sie diese in der Aufgabe