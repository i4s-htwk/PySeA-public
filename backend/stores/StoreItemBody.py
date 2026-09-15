from dataclasses import dataclass, field

@dataclass
class StoreItemBody:
    items: dict[str, str] = field(default_factory=dict)

    def add_item(self, id: str):
        self.items[id] = ""

    def delete_item(self, id_map: dict[str, str]):
        new_items = {}
        for old_id, value in self.items.items():
            new_id = id_map.get(old_id, old_id)
            if new_id is None:
                continue
            new_items[new_id] = value
        self.items = new_items

    def update_item(self, id: str, new_text: str):
        if id not in self.items:
            self.add_item(id)
        self.items[id] = new_text

    def get_item(self, id: str) -> str:
        return self.items.get(id, "")

    def all_items(self) -> dict[str, str]:
        return self.items

