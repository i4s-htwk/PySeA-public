import json
import os

class EditorData:
    def __init__(self, store_configurations, store_feedback, store_images, store_item_body, store_responses, store_selections, store_matchings, store_graphical_assignment, store_tables, store_variants, teststructure, output_path):
        self.data = {
            "store_configurations": store_configurations.to_dict(),
            "store_feedback": store_feedback.to_dict(),
            "store_images": store_images.to_dict(),
            "store_item_body": store_item_body.items,
            "store_responses": store_responses.to_dict(),
            "store_selections": store_selections.to_dict(),
            "store_matchings": store_matchings.to_dict(),
            "store_graphical_assignment": store_graphical_assignment.to_dict(),
            "store_tables": store_tables.to_dict(),
            "store_variants": store_variants.to_dict(),
            "teststructure": teststructure.to_dict()
        }

        path = os.path.join(output_path ,store_configurations.title.replace(" ", "")+".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)