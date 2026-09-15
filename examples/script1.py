from backend.facades import TestFacade

# create test-object
test = TestFacade("Script Test 1")

# define test-structure
section_1 = test.add_section()
task_1 = section_1.add_task()

# edit tasks
response_1 = task_1.response(5)
task_1.item_body(
    "Hallo hier ist eine Lücke: "+response_1+"\n" 
    "und hier ein neuer Absatz")

# export test
test.create_test("...")
