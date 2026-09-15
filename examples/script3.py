from backend.facades import TestFacade
from backend.utils import Cell

### create test-object ###################################################################################################################
test = TestFacade("Script Test 3")

### load/ edit images ####################################################################################################################
# Load all image files from the folder `files/media_script3` into the test object.
# `.map()` creates a dictionary-like structure so images can be accessed by filename, for example: images["Bild1.png"]
images = test.load_images("files/media_script3").map()
# Set the display width of every loaded image to 400.
for key, value in images.items():
    value.set_width("400")

### excel-file used ######################################################################################################################
# Path to the Excel file that is used as the data source for the tasks.
excel_file = "files/Beispiel.xlsx"

### enable use of variants ###############################################################################################################
# Enable the variant system for the test.
variants = test.variants("variable_dependent_assignment")
# Define the text shown in the variant input task.
# `{RESPONSE}` will be replaced by an input field.
variants.item_body = "Geben Sie ihre Matrikelnummer ein: {RESPONSE}"

# Define variant rules for the variables `a` and `b`.
# The variables `a` and `b` depend on specific digits of the entered student ID number.
# For example, if the relevant digit is between 4 and 7, the variable `a` takes the value 1.
data = {
    "a": [{0: [0, 3]}, {1: [4, 7]}, {2: [8, 9]}],
    "b": [{5: [0, 2]}, {5.5: [3, 5]}, {6: [6, 9]}]}

# Create variant variables and assign value ranges.
for i, (key, ranges) in enumerate(data.items()):
    variable = variants.assignment.add_variable()
    # Use the digit at position `i + 1` of the entered student ID number as the value source for this variable.
    variable.value_response = i+1
    # Register the variable name inside the variant system.
    variable.add_variable(key)
    for d in ranges:
        cond_value, (lo, hi) = next(iter(d.items()))
        condition = variable.add_condition()
        # Apply this condition when the response value is within the given bounds.
        condition.lower_bound = lo
        condition.upper_bound = hi
        # Set the resulting variable value for this range.
        condition.values = {key: cond_value}

### define test-structure ################################################################################################################
section_1 = test.add_section()
task_1 = section_1.add_task("Tabelle mit Antworten aus Exceldatei")
task_2 = section_1.add_task("Auswahlaufgabe mit Variantenabhängigen Bildern")
task_3 = section_1.add_task("Aufgabe mit variantenabhängigen Tabellen")

### edit tasks ###########################################################################################################################

# task_1: task with responses from excel-file
# Create a response collection based on Excel cells.
excel_responses = task_1.excel_responses()
# Assign the Excel file containing the response values.
excel_responses.excel_file = excel_file
# Select the worksheet named `Varianten`.
excel_responses.page = "Varianten"
# Add response fields linked to cells C3, C5, and C7.
for i in range(0,3):
    excel_responses.add_response("C"+str(2*i+3))

# Create a custom table for displaying the responses.
table = task_1.table("customTable")
for i in range (0,len(excel_responses.responses)+1):
    if i == 0:
        # Add the header row.
        table.cells.append([Cell("Stäbe"), Cell("Schnittkraft")])
    else:
        # Add one row per response field.
        # The left cell contains the label, the right cell contains the response field.
        table.cells.append([Cell("Stab "+str(i)), Cell(excel_responses.responses[i-1])])

# Add the instruction text and the custom table to the task body.
task_1.item_body(
    "Füllen sie die Lücken in der Tabelle: "+
    table)

task_1.feedback("correct", "das war richtig")
task_1.feedback("incorrect", "das war das erste mal falsch", [1,1])
task_1.feedback("incorrect", "2. mal oder öfter falsch", 2)
task_1.feedback("incorrect", "Lücke 1 ist falsch", excel_responses.responses[0])

# task_2: task with variant dependent selection
# Define the filenames of the images used in this task.
image_map = ["Bild1.svg", "Bild2.jpg", "Bild3.gif", "Bild4.jpeg", "Bild5.png", "Bild6.png", "Bild7.png", "Bild8.png", "Bild9.png"]
# Store the created variant-dependent image objects.
vdi_list = []
for i in range(0, 3):
    # Create a variant-dependent image container.
    vdi = task_2.variant_dependent_image()
    vdi_list.append(vdi)
    for j in range(0, 3):
        # Assign images to specific variant ranges.
        vdi.add_image(images[image_map[3*i+j]].id, j*3+1, (j+1)*3)

# Create a single-choice selection element.
selection = task_2.selection("singleChoice")
# The first variant-dependent image is the correct answer.
selection.set_correct([vdi_list[0]])
# The remaining variant-dependent images are incorrect answers.
selection.set_incorrect([vdi_list[1], vdi_list[2]])
# Show only one incorrect answer option in addition to the correct answer.
selection.set_wrong_count(1)

# Add the instruction text and the selection element to the task body.
task_2.item_body(
    "Wählen sie das richtige Lastbild aus: \n" +
    selection)

# task_3: task with variant dependent table
# Define the Excel cell ranges used for the three table variants.
areas_excel_file = [("J4", "L7"), ("N4", "P7"), ("R4", "T7")]
# Create a variant-dependent table container.
vdt = task_3.variant_dependent_table()
for i in range(0,3):
    # Create a table based on Excel data.
    table = task_3.table("excelTable")
    table.excel_file = excel_file
    table.page = "Tabelle"
    # Automatically generate response fields in the selected area.
    table.automatic_responses = True
    tl, br = areas_excel_file[i]
    # Select the Excel area for this table variant.
    area = table.add_area(tl, br)
    # Assign the table area to a specific variant range.
    vdt.add_table(area.id, 3*i +1, (i+1)*3)

# Add the instruction text and the variant-dependent table to the task body.
task_3.item_body(
    "Füllen Sie die Lücken in der Tabelle aus: \n"+
    vdt)

### set global settings #################################################################################################################
# Access the global test settings.
settings = test.get_settings()
# Set the navigation mode for the test.
settings.set_navigation_mode("test_path_control")

### export test #########################################################################################################################
test.create_test("...")
