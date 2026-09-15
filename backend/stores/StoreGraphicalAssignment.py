from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.utils import GraphicalAssignment

@dataclass
class StoreGraphicalAssignments:
    """
    Speichert alle grafischen Zuordnungen.

    Der Schlüssel im Dictionary ist normalerweise die ID der Aufgabe.
    Jede Aufgabe besitzt maximal GraphicalAssignment-Objekt.
    """
    items: Dict[str, GraphicalAssignment] = field(default_factory=dict)

    def add_item(self, task_id: str, original_image_path: str = None, mask_image_path: str = None, correct_image_path: str = None, wrong_image_paths: Optional[List[str]] = None) -> GraphicalAssignment:
        if task_id in self.items:
            raise ValueError(
                f"Für die Aufgabe '{task_id}' existiert bereits "
                f"eine grafische Zuordnung."
            )

        graphical_assignment = GraphicalAssignment(
            original_image_path=original_image_path,
            mask_image_path=mask_image_path,
            correct_image_path=correct_image_path,
            task_id = task_id
        )

        if wrong_image_paths:
            graphical_assignment.add_wrong_images(wrong_image_paths)

        self.items[task_id] = graphical_assignment
        return graphical_assignment

    def get_item(self, task_id: str) -> Optional[GraphicalAssignment]:
        """
        Gibt die grafische Zuordnung einer Aufgabe zurück.
        """
        return self.items.get(task_id)

    def update_item(
        self,
        task_id: str,
        graphical_assignment: GraphicalAssignment
    ) -> None:
        """
        Ersetzt die grafische Zuordnung einer Aufgabe.
        """
        if task_id not in self.items:
            raise KeyError(
                f"Für die Aufgabe '{task_id}' existiert "
                f"keine grafische Zuordnung."
            )

        self.items[task_id] = graphical_assignment

    def delete_item(self, task_id: str) -> None:
        """
        Entfernt eine grafische Zuordnung aus dem Store.
        """
        if task_id not in self.items:
            raise KeyError(
                f"Für die Aufgabe '{task_id}' existiert "
                f"keine grafische Zuordnung."
            )

        del self.items[task_id]

    def remap_items(self, id_map: Dict[str, Optional[str]]) -> None:
        """
        Ändert Aufgaben-IDs.

        Ist der neue Wert einer ID None, wird das zugehörige Element gelöscht.

        Beispiel:
            {
                "task_1": "task_2",
                "task_2": None
            }
        """
        new_items: Dict[str, GraphicalAssignment] = {}

        for old_id, graphical_assignment in self.items.items():
            new_id = id_map.get(old_id, old_id)

            if new_id is None:
                continue

            if new_id in new_items:
                raise ValueError(
                    f"Die neue Aufgaben-ID '{new_id}' ist mehrfach vorhanden."
                )

            new_items[new_id] = graphical_assignment

        self.items = new_items

    def all_items(self) -> Dict[str, GraphicalAssignment]:
        """
        Gibt alle gespeicherten grafischen Zuordnungen zurück.
        """
        return self.items

    def prepare_item(self, task_id: str) -> None:
        """
        Validiert eine grafische Zuordnung und erzeugt ihre Schnipsel.
        """
        graphical_assignment = self.get_required_item(task_id)
        graphical_assignment.prepare()

    def prepare_all(self) -> None:
        """
        Validiert alle grafischen Zuordnungen und erzeugt alle Schnipsel.
        """
        for graphical_assignment in self.items.values():
            graphical_assignment.prepare()

    def get_required_item(self, task_id: str) -> GraphicalAssignment:
        """
        Gibt ein Element zurück und wirft einen Fehler,
        falls die Aufgaben-ID nicht existiert.
        """
        graphical_assignment = self.items.get(task_id)

        if graphical_assignment is None:
            raise KeyError(
                f"Für die Aufgabe '{task_id}' existiert "
                f"keine grafische Zuordnung."
            )

        return graphical_assignment

    def get_all_media_paths(self) -> List[str]:
        """
        Gibt die Mediendateien aller grafischen Zuordnungen zurück.

        Doppelte Pfade werden entfernt, die Reihenfolge bleibt erhalten.
        """
        paths: List[str] = []

        for graphical_assignment in self.items.values():
            paths.extend(graphical_assignment.get_media_paths())

        return list(dict.fromkeys(paths))

    def to_dict(self) -> Dict[str, Any]:
        """
        Wandelt den Store in ein serialisierbares Dictionary um.
        """
        return {
            "items": {
                task_id: graphical_assignment.to_dict()
                for task_id, graphical_assignment in self.items.items()
            }
        }

    @classmethod
    def from_dict(
        cls,
        data: Optional[Dict[str, Any]]
    ) -> "StoreGraphicalAssignments":
        """
        Erstellt den Store aus einem Dictionary.
        """
        store = cls()

        if not data:
            return store

        for task_id, assignment_data in data.get("items", {}).items():
            store.items[task_id] = GraphicalAssignment.from_dict(
                assignment_data
            )

        return store