from dataclasses import dataclass, field
from typing import Dict, Any

from backend.utils import Matching

@dataclass
class StoreMatchings:
    items: Dict[str, Matching] = field(default_factory=dict)

    def add_item(self, id: str, response_identifier: str = "RESPONSE_1") -> Matching:
        matching = Matching(response_identifier=response_identifier)
        self.items[id] = matching
        return matching

    def add_pair(self, id: str, source_text: str, target_text: str):
        if id not in self.items:
            self.add_item(id)
        matching = self.items[id]
        source_id, target_id = matching.add_pair(source_text, target_text)
        self.items[id] = matching
        return source_id, target_id

    def delete_item(self, id_map: Dict[str, str]):
        new_items = {}
        for old_id, matching_obj in self.items.items():
            new_id = id_map.get(old_id, old_id)
            if new_id is None:
                continue
            new_items[new_id] = matching_obj
        self.items = new_items

    def update_item(self, id: str, new_matching: Matching):
        self.items[id] = new_matching

    def get_matching(self, id: str) -> Matching | None:
        return self.items.get(id)

    def all_matchings(self) -> Dict[str, Matching]:
        return self.items

    def to_dict(self) -> Dict[str, object]:
        items = {
            key: matching.to_dict()
            for key, matching in self.items.items()}
        return {
            "items": items}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoreMatchings":
        data = data or {"items": {}}
        store = cls()
        for key, matching_data in data.get("items", {}).items():
            store.items[key] = Matching.from_dict(matching_data)
        return store