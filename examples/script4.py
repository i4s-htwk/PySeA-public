from backend.facades import TestFacade
from backend.utils import Cell

### create test-object ###################################################################################################################
test = TestFacade("Script Test 4")

### excel-file used ######################################################################################################################
# Path to the Excel file that is used as the data source for the tasks.
excel_file = "files/Beispiel.xlsx"

### enable use of variants ###############################################################################################################
# Enable the variant system for the test.
variants = test.variants("student_id_to_variant_assignment")
variants.assignment.count_variants = 9

# Define the text shown in the variant input task.
# `{RESPONSE}` will be replaced by an input field.
variants.item_body = "Geben Sie ihre Matrikelnummer ein: {RESPONSE}"

### define test-structure ################################################################################################################
section = test.add_section("Sektion 1")
task = section.add_task("Grafische Zuordnungsaufgabe")

### edit sections ########################################################################################################################
# Create an Excel-variable manager for this section.
# The generated variables can later be printed in the section text or inside tables.
ev = section.add_excel_variables()

# Assign the Excel file and worksheet from which the variant-dependent values are read.
ev.excel_file = excel_file
ev.page = "Varianten"

# Create five Excel variables.
# The first variable starts at cell C10, the second at C11, and so on.
for i in range(0, 5):
    ev.add_variable("C" + str(10 + i))

# Create a custom table for the section.
# This table is later inserted into the section text by adding `table` to `section.item_body(...)`.
table = section.table("customTable")

# Fill the table with one header row and one row per Excel variable.
for i in range(0, len(ev.variables)):
    if i == 0:
        # Add the header row.
        table.cells.append([Cell("Stäbe"), Cell("Stablänge [m]")])
    else:
        # Add one row per Excel variable.
        # The left cell contains a label such as "Stab 1".
        # The right cell contains the corresponding Excel variable.
        table.cells.append([Cell("Stab " + str(i)), Cell(ev.variables[i - 1])])

# Define the section text.
# The table is inserted directly into the text.
# The last Excel variable is printed again after "F =" and followed by the unit "kN".
section.item_body("Bitte rechnen Sie in den Aufgaben mit folgenden Werten weiter: \n" +
                  table +
                  "\n $$F =$$" + ev.variables[-1] + "kN")

### edit tasks ###########################################################################################################################
graphical_assignment = task.graphical_assignment()

graphical_assignment.original_image_path = ("files/GrafischeZuordnung/Original.excalidraw.png")
graphical_assignment.mask_image_path = ("files/GrafischeZuordnung/Maske.excalidraw.png")
graphical_assignment.correct_image_path = ("files/GrafischeZuordnung/Richtig.excalidraw.png")
graphical_assignment.add_wrong_images([
    "files/GrafischeZuordnung/Falsch.excalidraw.png"])

task.item_body(
    "Ordnen Sie die Bildausschnitte den richtigen Bereichen "
    "im Hintergrundbild zu:\n" +
    graphical_assignment)

### set global settings #################################################################################################################
# Access the global settings object of the test.
settings = test.get_settings()

# Set the navigation mode of the test.
# "test_path_control" means that the predefined test path controls how the participant moves through the test.
settings.set_navigation_mode("test_path_control")

# Set the accepted answer accuracy for numerical gap responses.
# "relative" means that the tolerance is interpreted relatively, here with a value of 2%.
settings.set_answer_acc("relative", 2)

# Define how many points are awarded for gap-input interactions.
# In this example, each gap response is worth 1 point.
settings.set_point_distribution("gap", 1)

# Define how many points are awarded for selection interactions.
# In this example, each selection response is worth 2 points.
settings.set_point_distribution("selection", 2)

# Define the point deduction for repeated answer attempts.
# For each answer attempt, 0.5 points are deducted.
# If the question is answered completely correctly, at least 40% of the points are still awarded.
settings.set_point_deduction(0.5, 40)

# Set the minimum score percentage required to pass the test.
# In this example, the participant must reach at least 40 percent.
settings.set_pass_score_percentage(40)

# Define the feedback text shown when the test is passed.
# {SCORE} is a placeholder that will be replaced by the achieved score.
settings.set_feedback("correct", "Sie haben {SCORE} Punkte erreicht und damit den Test bestanden")

# Define the feedback text shown when the test is not passed.
# {SCORE} is a placeholder that will be replaced by the achieved score.
settings.set_feedback("incorrect", "Sie haben {SCORE} Punkte erreicht und damit den Test leider nicht bestanden")

# By default, the participant's previously entered responses are kept.
# Disable this explicitly so that previous answers are not shown again on a new answer attempt.
settings.keep_responses(False)

### export test #########################################################################################################################
test.create_test("...")