from backend.facades import TestFacade

### load test-object #####################################################################################################################
# This script can only be executed after running script1.py first.
# Insert the file path to the JSON file of the test created by script1.py into TestFacade().load_test("...").
test = TestFacade().load_test("...")

### load/ create images ##################################################################################################################
# Load all image files from the folder `files/media_script2` into the test object.
# `.map()` creates a dictionary-like structure so images can be accessed by filename, for example: images["lastbild.png"]
images = test.load_images("files/media_script2").map()

### excel-file used ######################################################################################################################
# Path to the Excel file that will later be used as the source for the table task.
excel_file = "files/Beispiel.xlsx"

### define test-structure ################################################################################################################
section_2 = test.add_section()
task_2 = section_2.add_task("Lückentext")
task_3 = section_2.add_task("Auswahlaufgabe")
task_4 = section_2.add_task("Tabelle mit Lücken")
task_5 = section_2.add_task("Zuordnungsaufgabe")

### edit tasks ###########################################################################################################################

# task_2: task with image
# Create a response field with the correct answer of '12'.
response_1 = task_2.response(12)
# Insert the task text an image and the response field into the task body.
task_2.item_body(
    "Wie groß ist die Schnittkraft im angegebenen System? \n" +
    images["lastbild.png"] + "\n"
    "Antwort: " + response_1)

# task_3: task with selection and feedback
# Create a single-choice selection element.
selection_1 = task_3.selection("singleChoice")
# Define which image is the correct answer option.
selection_1.set_correct([images["schnittkraft1.png"]])
# Define which images are incorrect answer options.
selection_1.set_incorrect([images["schnittkraft2.png"], images["schnittkraft3.png"]])
# Insert the task text and the selection element into the task body.
task_3.item_body(
    "Wählen sie den richtigen Schnittkraftverlauf aus: \n"+
    selection_1)

# Feedback shown when the learner selects the correct answer.
task_3.feedback("correct", "das war richtig ")
# Feedback shown when the learner selects a wrong answer,
# including the correct image as part of the explanation.
task_3.feedback("incorrect", "das war falsch, hier ist die richtige Antwort: \n" +
                images["schnittkraft1.png"])

# task_4: task with table from excel-file
# Create a table element based on Excel data.
table = task_4.table("excelTable")
# Assign the Excel file that contains the table content.
table.excel_file = excel_file
# Select the worksheet named `Tabelle` from the Excel file.
table.page = "Tabelle"
# Automatically generate response fields for cells only containing numbers in the selected area.
table.automatic_responses = True
# Define the cell range from C4 to H8 as the table area used in the task.
area = table.add_area("C4", "H8")

# Add the instruction text and the generated table area to the task body.
task_4.item_body(
    "Füllen Sie die Lücken in der Tabelle aus: \n"+
    area)


# task_5: task with matching
# Create a matching element for assigning terms to images.
matching = task_5.matching()

# Add two correct matching pairs.
matching.add_pair("Lastbild", images["lastbild.png"])
matching.add_pair("Schnittkraftverlauf", images["schnittkraft1.png"])

# Add the instruction text and the matching interaction to the task body.
task_5.item_body(
    "Ordnen Sie den Bildern die richtigen Begriffe zu: \n" +
    matching)

### set global settings ##################################################################################################################
# Access the global test settings object.
settings = test.get_settings()
# Set the title of the exported test.
settings.set_title("Script Test 2")

### export test ##########################################################################################################################
test.create_test("...")