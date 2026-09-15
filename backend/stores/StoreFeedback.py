from dataclasses import dataclass, field
from backend.utils import Feedback

@dataclass
class StoreFeedback:
    items: dict[str, dict[str, list[Feedback] | Feedback | None]] = field(default_factory=dict)

    def add_item(self, id: str):
        self.items[id] = {"feedback_incorrect": [], "feedback_correct": Feedback("FEEDBACK_CORRECT", "correct")}

    def delete_item(self, id_map: dict[str, str]):
        new_items = {}
        for old_id, value in self.items.items():
            new_id = id_map.get(old_id, old_id)
            if new_id is None:
                continue
            new_items[new_id] = value
        self.items = new_items

    def add_feedback_incorrect(self, id: str, value:str, condition=None):
        if id not in self.items:
            self.add_item(id)
        len_fbi = len(self.items[id]["feedback_incorrect"])
        fb = Feedback("FEEDBACK_INCORRECT_"+str(len_fbi+1), "incorrect", condition)
        fb.value = value
        self.items[id]["feedback_incorrect"].append(fb)

    def set_feedback_correct(self, id: str, value:str):
        if id not in self.items:
            self.add_item(id)
        self.items[id]["feedback_correct"].value = value

    def get_feedback_incorrect(self, id: str) -> list[Feedback]:
        return self.items.get(id, {}).get("feedback_incorrect", [])

    def get_feedback_correct(self, id: str) -> Feedback | None:
        return self.items.get(id, {}).get("feedback_correct", None)

    def get_item(self, id:str):
        if id not in self.items:
            return None
        else:
            return self.items[id]

    def all_items(self) -> dict[str, dict[str, list[Feedback] | Feedback | None]]:
        return self.items

    def to_dict(self) -> dict[str, dict[str, object]]:
        result = {}
        for item_id, data in self.items.items():
            result[item_id] = {
                "feedback_incorrect": [fb.to_dict() for fb in data["feedback_incorrect"]],
                "feedback_correct": data["feedback_correct"].to_dict() if data["feedback_correct"] else None}
        return result

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, object]]) -> "StoreFeedback":
        instance = cls()

        for item_id, item_data in data.items():
            feedback_incorrect_data = item_data.get("feedback_incorrect", item_data.get("feedbacks_incorrect", []))
            feedback_correct_data = item_data.get("feedback_correct")
            instance.items[item_id] = {
                "feedback_incorrect": [Feedback.from_dict(feedback) for feedback in feedback_incorrect_data],
                "feedback_correct": (Feedback.from_dict(feedback_correct_data) if feedback_correct_data else None),}

        return instance