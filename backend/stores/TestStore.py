import json

from . import *
from backend.validation import TestValidator
from backend.CreateTest import CreateTest
from backend.TestStructure import TestStructure
from .StoreGraphicalAssignment import StoreGraphicalAssignments


class TestStore:
    __test__ = False

    def __init__(self):
        self.test_structure = TestStructure()
        self.store_item_body = StoreItemBody()
        self.store_responses = StoreResponses()
        self.store_configurations = StoreConfigurations()
        self.store_tables = StoreTables()
        self.store_feedback = StoreFeedback()
        self.store_selections = StoreSelections()
        self.store_matchings = StoreMatchings()
        self.store_graphical_assignment = StoreGraphicalAssignments()
        self.store_variants = StoreVariants()
        self.store_images = StoreImages()

    def create_test(self, output_dir):
        TestValidator(self).validate_before_export()
        CreateTest(
            self.test_structure,
            self.store_images,
            self.store_item_body,
            self.store_responses,
            self.store_configurations,
            self.store_tables,
            self.store_feedback,
            self.store_selections,
            self.store_matchings,
            self.store_graphical_assignment,
            self.store_variants,
            output_dir
        )

    @staticmethod
    def load_test(path_file):
        test_store = TestStore()
        with open(path_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        test_store.test_structure = TestStructure().from_dict(data["teststructure"])
        test_store.store_images = StoreImages().from_dict(data["store_images"])
        test_store.store_item_body = StoreItemBody({})
        test_store.store_item_body.items = data["store_item_body"]
        test_store.store_responses = StoreResponses().from_dict(data["store_responses"])
        test_store.store_tables = StoreTables().from_dict(data["store_tables"])
        test_store.store_feedback = StoreFeedback().from_dict(data["store_feedback"])
        test_store.store_selections = StoreSelections("single_choice").from_dict(data["store_selections"])
        test_store.store_matchings = StoreMatchings.from_dict(data.get("store_matchings", {"items": {}}))
        test_store.store_graphical_assignment = StoreGraphicalAssignments.from_dict(data.get("store_graphical_assignment", {"items": {}}))
        test_store.store_configurations = StoreConfigurations().from_dict(data["store_configurations"])
        test_store.store_variants = StoreVariants().from_dict(data["store_variants"])

        return test_store

    @staticmethod
    def from_dict(data):
        test_store = TestStore()
        test_store.test_structure = TestStructure().from_dict(data["test_structure"])
        test_store.store_images = StoreImages().from_dict(data["store_images"])
        test_store.store_item_body = StoreItemBody({})
        test_store.store_item_body.items = data["store_item_body"]
        test_store.store_responses = StoreResponses().from_dict(data["store_responses"])
        test_store.store_tables = StoreTables().from_dict(data["store_tables"])
        test_store.store_feedback = StoreFeedback().from_dict(data["store_feedback"])
        test_store.store_selections = StoreSelections("single_choice").from_dict(data["store_selections"])
        test_store.store_matchings = StoreMatchings.from_dict(data["store_matchings"])
        test_store.store_graphical_assignment = StoreGraphicalAssignments.from_dict(data["store_graphical_assignment"])
        test_store.store_configurations = StoreConfigurations().from_dict(data["store_configurations"])
        test_store.store_variants = StoreVariants().from_dict(data["store_variants"])

        return test_store

    def to_dict(self):
        return {
            'test_structure': self.test_structure.to_dict(),
            'store_item_body': self.store_item_body.items,
            'store_responses': self.store_responses.to_dict(),
            'store_configurations': self.store_configurations.to_dict(),
            'store_tables': self.store_tables.to_dict(),
            'store_feedback': self.store_feedback.to_dict(),
            'store_selections': self.store_selections.to_dict(),
            'store_matchings': self.store_matchings.to_dict(),
            'store_graphical_assignment': self.store_graphical_assignment.to_dict(),
            'store_variants': self.store_variants.to_dict(),
            'store_images': self.store_images.to_dict()
        }
