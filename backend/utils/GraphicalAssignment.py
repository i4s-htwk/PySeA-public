import os
from dataclasses import dataclass
from typing import List, Tuple
from PIL import Image as PILImage
import cv2
import numpy as np
from pathlib import Path
import shutil

from backend.utils.Images import Image

@dataclass
class Snippet:
    """
    Datenklasse für einen ausgeschnittenen Bildbereich.
    """
    index: int
    x: int
    y: int
    width: int
    height: int
    source_image: str
    output_path: str

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "source_image": self.source_image,
            "output_path": self.output_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snippet":
        return cls(
            index=data["index"],
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            source_image=data["source_image"],
            output_path=data["output_path"]
        )

class GraphicalAssignment:
    """A graphical matching task element based on cut-out image snippets.

    An instance of this class is returned by ``TaskFacade.graphical_assignment()``.
    ``original_image_path``, ``mask_image_path`` and ``correct_image_path``
    define the background, mask and correct-content images, and
    ``add_wrong_images()`` adds images used to generate additional
    incorrect snippets. The object can be embedded directly into an item
    body.
    """

    def __init__(self, original_image_path: str, mask_image_path: str, correct_image_path: str, task_id: str):
        self.task_id = task_id
        self.id = "RESPONSE_1"
        self.original_image_path = original_image_path
        self.mask_image_path = mask_image_path
        self.correct_image_path = correct_image_path
        self.wrong_image_paths: List[str] = []

        self.generated_original_path: str | None = None

        project_root = Path(__file__).resolve().parents[2]
        self.output_dir = str(project_root / "tmp_dir" / "graphical_assignments" / task_id)

        self.cut_areas: List[Tuple[int, int, int, int]] = []

        self.correct_snippets: List[Snippet] = []
        self.wrong_snippets: List[Snippet] = []

        # Lokal erzeugte Image-Objekte
        self.images: List[Image] = []

    def add_wrong_images(self, image_paths: List[str]):
        """Add images used to generate additional incorrect snippets.

        At least one wrong image is required. From each image, incorrect
        snippets are cut out at the same positions as the correct
        snippets, based on the mask image.
        Args:
            image_paths: Paths to the wrong-content images. All of them
                must have the same dimensions as the original image.
        """
        for image_path in image_paths:
            self.wrong_image_paths.append(image_path)

    def validate_paths(self):
        required_paths = [
            self.original_image_path,
            self.mask_image_path,
            self.correct_image_path,
            *self.wrong_image_paths
        ]

        for path in required_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Bilddatei wurde nicht gefunden: {path}")

    def validate_image_sizes(self):
        """
        Prüft, ob Originalbild, Maske, Richtig-Bild und alle Falschbilder
        dieselbe Bildgröße haben.
        """
        images = [
            self.original_image_path,
            self.mask_image_path,
            self.correct_image_path,
            *self.wrong_image_paths
        ]

        base_size = PILImage.open(self.original_image_path).size

        for image_path in images:
            current_size = PILImage.open(image_path).size

            if current_size != base_size:
                raise ValueError(
                    f"Alle Bilder müssen dieselbe Größe haben. "
                    f"Erwartet: {base_size}, gefunden: {current_size} bei {image_path}"
                )

    def validate(self):
        """
        Führt alle Validierungen des Stores aus.
        """
        self.validate_paths()
        self.validate_image_sizes()

        if len(self.wrong_image_paths) == 0:
            raise ValueError(
                "Es wurde kein Falschbild angegeben. "
                "Mindestens ein Falschbild ist für die grafische Zuordnung erforderlich."
            )

    def detect_cut_areas(
        self,
        white_threshold: int = 245,
        min_width: int = 20,
        min_height: int = 20,
        border: int = 3
    ):
        """
        Erkennt Schnittbereiche anhand der Maske.

        Alles, was nicht weiß ist, wird als Maskenbereich interpretiert.
        """
        mask_image = PILImage.open(self.mask_image_path).convert("RGB")
        mask_np = np.array(mask_image)

        r = mask_np[:, :, 0]
        g = mask_np[:, :, 1]
        b = mask_np[:, :, 2]

        mask = (
            (r < white_threshold) |
            (g < white_threshold) |
            (b < white_threshold)
        ).astype(np.uint8) * 255

        # äußeren Bildrand entfernen
        mask[:border, :] = 0
        mask[-border:, :] = 0
        mask[:, :border] = 0
        mask[:, -border:] = 0

        os.makedirs(self.output_dir, exist_ok=True)

        debug_dir = os.path.join(
            self.output_dir,
            "debug"
        )
        os.makedirs(debug_dir, exist_ok=True)

        PILImage.fromarray(mask).save(
            os.path.join(
                debug_dir,
                "debug_mask.png"
            )
        )

        # Linien etwas dicker machen
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask,
            connectivity=8
        )

        self.cut_areas.clear()

        for label in range(1, num_labels):
            x = int(stats[label, cv2.CC_STAT_LEFT])
            y = int(stats[label, cv2.CC_STAT_TOP])
            w = int(stats[label, cv2.CC_STAT_WIDTH])
            h = int(stats[label, cv2.CC_STAT_HEIGHT])

            if w < min_width or h < min_height:
                continue

            self.cut_areas.append((x, y, w, h))

        self.cut_areas.sort(key=lambda box: box[0])

        if len(self.cut_areas) == 0:
            raise ValueError(
                "In der Maske wurden keine gültigen Schnittbereiche gefunden."
            )

    def generate_snippets(self):
        if len(self.cut_areas) == 0:
            raise ValueError("Es wurden noch keine Schnittbereiche erkannt. Rufe zuerst detect_cut_areas() auf.")

        self.correct_snippets.clear()
        self.wrong_snippets.clear()
        self.images.clear()

        os.makedirs(self.output_dir, exist_ok=True)
        original_extension = Path(self.original_image_path).suffix.lower()
        self.generated_original_path = os.path.join(self.output_dir, f"{self.task_id}_original{original_extension}")
        shutil.copy2(self.original_image_path, self.generated_original_path)
        self.add_local_image(image_path=self.generated_original_path, image_id=f"{self.task_id}_GRAPHICAL_BACKGROUND")

        # Richtige Schnipsel
        with PILImage.open(self.correct_image_path) as opened_image:
            correct_image = opened_image.convert("RGBA")

            for index, (x, y, width, height) in enumerate(self.cut_areas):
                snippet_image = correct_image.crop((x, y, x + width, y + height))
                output_path = os.path.join(self.output_dir, f"{self.task_id}_correct_snippet_{index}.png")
                snippet_image.save(output_path)
                snippet = Snippet(index=index, x=x, y=y, width=width, height=height, source_image=self.correct_image_path, output_path=output_path)

                self.correct_snippets.append(snippet)
                self.add_local_image(image_path=output_path, image_id=f"{self.task_id}_CORRECT_SNIPPET_{index}")

        # Falsche Schnipsel
        for wrong_image_index, wrong_image_path in enumerate(self.wrong_image_paths):
            with PILImage.open(wrong_image_path) as opened_image:
                wrong_image = opened_image.convert("RGBA")

                for snippet_index, (x, y, width, height) in enumerate(self.cut_areas):
                    snippet_image = wrong_image.crop((x, y, x + width, y + height))
                    output_path = os.path.join(self.output_dir, (f"{self.task_id}_wrong_{wrong_image_index}_snippet_{snippet_index}.png"))

                    snippet_image.save(output_path)
                    snippet = Snippet(index=snippet_index, x=x, y=y, width=width, height=height, source_image=wrong_image_path, output_path=output_path)

                    self.wrong_snippets.append(snippet)
                    self.add_local_image(image_path=output_path, image_id=(f"{self.task_id}_WRONG_{wrong_image_index}_SNIPPET_{snippet_index}"))

    def prepare(self):
        self.validate()
        self.detect_cut_areas()
        self.generate_snippets()

    def get_all_snippet_paths(self) -> List[str]:
        paths = []
        for snippet in self.correct_snippets:
            paths.append(snippet.output_path)
        for snippet in self.wrong_snippets:
            paths.append(snippet.output_path)
        return paths

    def get_media_paths(self) -> List[str]:
        paths = []
        if self.generated_original_path is not None:
            paths.append(self.generated_original_path)
        paths.extend(self.get_all_snippet_paths())
        return paths

    def get_image_by_path(self, image_path: str) -> Image | None:
        file_name = os.path.basename(image_path)
        return next((image for image in self.images if image.href == file_name), None)

    def get_background_image(self) -> Image:
        if self.generated_original_path is None: raise ValueError("Die grafische Zuordnung wurde noch nicht vorbereitet.")
        image = self.get_image_by_path(self.generated_original_path)
        if image is None:
            raise ValueError("Das Hintergrundbild wurde nicht in den lokalen Bildern gefunden.")
        return image

    def add_local_image(self, image_path: str, image_id: str) -> Image:
        file_name = os.path.basename(image_path)

        with PILImage.open(image_path) as opened_image:
            width, height = opened_image.size

        ratio = height / width if width else 0

        image = Image(href=file_name, id=image_id, width=str(width), height=str(height), ratio=str(ratio))
        existing_image = next((current_image for current_image in self.images if current_image.id == image.id or current_image.href == image.href), None)
        if existing_image is not None:
            return existing_image

        self.images.append(image)
        return image

    def copy_original_image(self) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        extension = Path(self.original_image_path).suffix.lower()
        output_path = os.path.join(self.output_dir, f"{self.task_id}_original{extension}")
        shutil.copy2(self.original_image_path, output_path)

        return output_path

    def to_dict(self) -> dict:
        return {
            "original_image_path": self.original_image_path,
            "mask_image_path": self.mask_image_path,
            "correct_image_path": self.correct_image_path,
            "wrong_image_paths": list(self.wrong_image_paths),
            "task_id": self.task_id,
            "cut_areas": [
                list(cut_area)
                for cut_area in self.cut_areas
            ],
            "correct_snippets": [
                snippet.to_dict()
                for snippet in self.correct_snippets
            ],
            "wrong_snippets": [
                snippet.to_dict()
                for snippet in self.wrong_snippets
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GraphicalAssignment":
        graphical_assignment = cls(
            original_image_path=data["original_image_path"],
            mask_image_path=data["mask_image_path"],
            correct_image_path=data["correct_image_path"],
            task_id = data["task_id"])

        graphical_assignment.wrong_image_paths = list(data.get("wrong_image_paths", []))
        graphical_assignment.cut_areas = [tuple(cut_area) for cut_area in data.get("cut_areas", [])]
        graphical_assignment.correct_snippets = [Snippet.from_dict(snippet_data) for snippet_data in data.get("correct_snippets", [])]
        graphical_assignment.wrong_snippets = [Snippet.from_dict(snippet_data) for snippet_data in data.get("wrong_snippets", [])]

        return graphical_assignment

    def __radd__(self, other: object) -> str:
        if isinstance(other, str):
            return other + "{GRAPHICAL_ASSIGNMENT}"
        return NotImplemented

    def __add__(self, other: object) -> str:
        if isinstance(other, str):
            return "{GRAPHICAL_ASSIGNMENT}" + other
        return NotImplemented