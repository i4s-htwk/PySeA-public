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
PROJEKT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJEKT))
os.chdir(PROJEKT)

from backend.facades import TestFacade #Import des Moduls "TestFacade" - darin sind alle Funktionen enthalten, die für die Erstellung eines Tests benötigt werden

###############################
# Test-Objekt erstellen & Test benennen
###############################
test = TestFacade(title = "Aufgabe 2 – Feedback & Bilder (Lösung)")

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
task_1.feedback("correct", "Sehr gut, das war korrekt!" + images["Feedback_korrekt.png"]) # Feedback für korrekte Antworten, inkl. Bild

# falsche Antworten
task_1.feedback("incorrect", "Das war leider falsch. Versuchen Sie es noch einmal!" + images["Feedback_falsch.jpg"]) # Feedback für falsche Antworten, inkl. Bild



###############################
# Aufgabe 2 erstellen und Parabel mit matplotlib erstellen
###############################
# Aufgabe 2 in Sektion 1 erstellen
task_2 = section_1.add_task(title = "Scheitelpunkt einer Parabel") # Erstellen der Aufgabe 2 innerhalb der Sektion 1

# Parabel mit Matplotlib erstellen und als Bild einbinden
###############################
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

# Funktion als String definieren (hier kann man die Funktion aendern)
f_str = "(x-3.3)**2 + 4.7*x - 1.7"  # Beispielparabel

# Symbolischen Ausdruck erstellen
x_sym = sp.symbols('x')  # Erstellt das symbolische Variable-Objekt x
f_expr = sp.sympify(f_str)  # Konvertiert den String f_str in einen symbolischen Ausdruck

# Funktion für numerische Berechnung erstellen
f = sp.lambdify(x_sym, f_expr, 'numpy')  # Erstellt eine numerische Funktion aus f_expr, die mit NumPy-Arrays arbeitet

# Scheitelpunkt berechnen (x-Koordinate über Ableitung)
f_ableitung = sp.diff(f_expr, x_sym)  # Ableitung der Funktion
scheitelpunkt_x = sp.solve(sp.Eq(f_ableitung, 0), x_sym)[0]  # x-Wert des Scheitelpunkts
scheitelpunkt_x = float(scheitelpunkt_x)  # Als Float für die Antwort
print(f"Der Scheitelpunkt liegt bei x = {scheitelpunkt_x}")

# Daten für die Parabel erstellen
x_vals = np.linspace(0, 2.5, 50)  # Erstellen von 50 x-Werten zwischen 0 und 2,5
y = f(x_vals)  # Berechnet y-Werte durch Anwendung von f auf alle x_vals

# Parabel plotten
plt.plot(x_vals, y)  # Zeichnet die Funktion y = f(x)

# Achsen deutlich einzeichnen
plt.axhline(0, color='black', linewidth=1.5)  # x-Achse (y=0)
plt.axvline(0, color='black', linewidth=1.5)  # y-Achse (x=0)

# Scheitelpunkt markieren (optional)
plt.plot(scheitelpunkt_x, f(scheitelpunkt_x), 'ro')  # Roter Punkt am Scheitelpunkt

plt.title(f"Parabel: y = {f_str}")  # Titel mit dem Funktionsstring
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True, linestyle='--', alpha=0.7)  # Gestricheltes Gitter

# Bild speichern
plt.savefig("examples/PySeA_workshop/files/Parabel.png")
plt.close()
###############################

###############################
# Bilder in die Aufgabe einbinden (nochmal, da jetzt ein neues Bild erstellt wurde)
images = test.load_images("examples/PySeA_workshop/files").map()

# 2 Antworten definieren
response_2 = task_2.response(scheitelpunkt_x) # Dynamisch berechnete x-Koordinate des Scheitelpunkts

# Aufgabenkörper mit Bild erstellen
task_2.item_body(
    "Bestimmen Sie die x-Koordinate des Scheitelpunkts der gezeigten Parabel \n"+
    images["Parabel.png"] + "\n"
    "Der Scheitelpunkt liegt bei x = "+response_2)



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