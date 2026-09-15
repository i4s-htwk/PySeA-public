import os
import shutil
from PIL import Image as Img

from backend.utils import Image

class StoreImages:
    """Manages the images loaded into a test.

    An instance of this class is returned by ``TestFacade.load_images()``.
    It copies image files into the project's ``assets`` folder, wraps each
    of them in an ``Image`` object, and offers ``map()`` to access those
    ``Image`` objects by filename.
    """
    def __init__(self):
        self.path_images = ""
        self.images = []

    def load_images(self, path):
        """Load all image files from the given directory into the test.

        Existing images are replaced. Each loaded file is copied into the
        project's ``assets`` folder and wrapped in an ``Image`` object.
        Args:
            path: Path to the directory containing the image files
                (``.png``, ``.jpg``, ``.jpeg``, ``.svg``, ``.gif``).
        Returns:
            This ``StoreImages`` instance, so ``.map()`` can be chained
            directly onto the call.
        """
        self.path_images = path
        self.images = []

        os.makedirs("assets", exist_ok=True)
        for f in os.listdir("assets"):
            pfad = os.path.join("assets", f)
            if os.path.isfile(pfad):
                os.remove(pfad)

        types = (".png", ".jpg", ".jpeg", ".svg", ".gif")
        if os.path.isdir(self.path_images):
            i = 0
            for fname in os.listdir(self.path_images):
                if fname.lower().endswith(types):
                    quelle = os.path.join(self.path_images, fname)
                    ziel = os.path.join("assets", fname)
                    shutil.copy2(quelle, ziel)

                    img_breite, img_hoehe = 0, 0
                    if not fname.lower().endswith(".svg"):
                        with Img.open(ziel) as img:
                            img_breite, img_hoehe = img.size

                    verhaeltnis = img_hoehe / img_breite if img_breite else 0
                    self.images.append(
                        Image(str(fname), f"BILD_{i + 1}", str(img_breite), str(img_hoehe), str(verhaeltnis)))
                    i += 1
        return self

    def add_images (self, path):
        os.makedirs("assets", exist_ok=True)

        types = (".png", ".jpg", ".jpeg", ".svg", ".gif")
        if os.path.isdir(path):
            i = len(self.images)
            for fname in os.listdir(path):
                if fname.lower().endswith(types):
                    quelle = os.path.join(path, fname)
                    ziel = os.path.join("assets", fname)
                    shutil.copy2(quelle, ziel)

                    img_breite, img_hoehe = 0, 0
                    if not fname.lower().endswith(".svg"):
                        with Img.open(ziel) as img:
                            img_breite, img_hoehe = img.size

                    verhaeltnis = img_hoehe / img_breite if img_breite else 0
                    self.images.append(
                        Image(str(fname), f"BILD_{i + 1}", str(img_breite), str(img_hoehe), str(verhaeltnis)))
                    i += 1
        return self

    def map(self):
        """Return the loaded images as a dictionary keyed by filename.
        Returns:
            A dict mapping each image's filename (e.g. ``"bild.png"``) to
            its ``Image`` object.
        """
        idx = {}
        for p in self.images:
            idx[p.href] = p
        return idx

    def get_image(self, href):
        """Return a loaded image by filename.
        Args:
            href: The filename of the image (e.g. ``"bild.png"``).
        Returns:
            The matching ``Image`` object, or ``None`` if no image with
            that filename was loaded.
        """
        for image in self.images:
            if image.href == href:
                return image
        return None

    @staticmethod
    def from_dict(data):
        store_obj = StoreImages()
        store_obj.path_images = data["path_images"]
        for b in data.get("images", []):
            store_obj.images.append(Image.from_dict(b))
        return store_obj

    def to_dict(self):
        return {
            "path_images": self.path_images,
            "images": [b.to_dict() for b in self.images]
        }

