from dataclasses import dataclass, field
from typing import Dict, List, Any

from backend.utils import Selection

@dataclass
class StoreSelections:
    type: str = "single Choice"
    items: Dict[str, Selection] = field(default_factory=dict)

    def add_item(self, id: str, type: str, correct=None, incorrect: List[str] = None):
        if correct is None: correct = [None]
        if incorrect is None: incorrect = [None]
        selection = Selection(id="SELECTION",type=type, correct=correct, incorrect=incorrect)
        self.items[id] = selection
        return selection

    def add_selection(self, id: str, type: str, selection):
        if id in self.items:
            selection_obj = self.items[id]
            if type=="incorrect":
                selection_obj.incorrect.append(selection)
            elif type=="correct":
                selection_obj.correct.append(selection)
            self.items[id] = selection_obj

    def delete_item(self, id_map: Dict[str, str]):
        new_items = {}
        for old_id, selection_obj in self.items.items():
            new_id = id_map.get(old_id, old_id)
            if new_id is None:
                continue
            new_items[new_id] = selection_obj
        self.items = new_items

    def update_item(self, id: str, new_correct: List[str] = None, new_incorrect: List[str] = None):
        if id not in self.items:
            self.add_item(id, "singleChoice")
        selection_obj = self.items[id]
        if new_correct is not None:
            selection_obj.correct = new_correct
        if new_incorrect is not None:
            selection_obj.incorrect = new_incorrect
        self.items[id] = selection_obj

    def get_selection(self, id: str) -> Selection:
        return self.items.get(id)

    def all_selections(self) -> Dict[str, Selection]:
        return self.items

    def to_dict(self) -> Dict[str, object]:
        items = {key: selection.to_dict() for key, selection in self.items.items()}
        type = self.type
        return {"items": items, "type": type}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoreSelections":
        data = data or {"items": {}, "type": "single Choice"}
        store = cls(data.get("type", "single Choice"))
        for key, selection_data in data["items"].items():
            store.items[key] = Selection.from_dict(selection_data)
        return store