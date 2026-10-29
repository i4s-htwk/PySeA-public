import os
import shutil
import re
import xml.etree.ElementTree as ET
from PIL import Image as Img

from backend.utils import Image

# Umrechnungsfaktoren absoluter SVG-Längeneinheiten in px (CSS: 96 px pro Zoll)
_SVG_EINHEITEN = {"": 1.0, "px": 1.0, "pt": 4 / 3, "pc": 16.0, "in": 96.0, "cm": 96 / 2.54, "mm": 96 / 25.4}


def _svg_laenge(wert):
    """Wandelt eine SVG-Längenangabe (z. B. ``"123.4pt"``) in px um.
    Gibt ``None`` zurück bei fehlender, relativer (``%``, ``em``) oder ungültiger Angabe."""
    if not wert:
        return None
    m = re.fullmatch(r"\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*([a-zA-Z%]*)\s*", wert)
    if not m or m.group(2).lower() not in _SVG_EINHEITEN:
        return None
    laenge = float(m.group(1)) * _SVG_EINHEITEN[m.group(2).lower()]
    return laenge if laenge > 0 else None


def _svg_masse(pfad):
    """Liest Breite und Höhe (in px) aus dem ``<svg>``-Wurzelelement.
    Nutzt ``width``/``height``, fehlende Werte werden über die ``viewBox`` ergänzt.
    Gibt ``(0, 0)`` zurück, wenn sich keine Maße bestimmen lassen."""
    try:
        _, wurzel = next(ET.iterparse(pfad, events=("start",)))
    except (ET.ParseError, StopIteration, OSError):
        return 0, 0

    breite = _svg_laenge(wurzel.get("width"))
    hoehe = _svg_laenge(wurzel.get("height"))

    vb_breite = vb_hoehe = None
    viewbox = wurzel.get("viewBox")
    if viewbox:
        teile = re.split(r"[\s,]+", viewbox.strip())
        try:
            if len(teile) == 4 and float(teile[2]) > 0 and float(teile[3]) > 0:
                vb_breite, vb_hoehe = float(teile[2]), float(teile[3])
        except ValueError:
            pass

    if breite and hoehe:
        return breite, hoehe
    if vb_breite:
        if breite:
            return breite, breite * vb_hoehe / vb_breite
        if hoehe:
            return hoehe * vb_breite / vb_hoehe, hoehe
        return vb_breite, vb_hoehe
    return 0, 0


def _bildmasse(pfad):
    """Gibt ``(breite, hoehe)`` einer Bilddatei in px zurück (SVG oder Rastergrafik)."""
    if pfad.lower().endswith(".svg"):
        return _svg_masse(pfad)
    with Img.open(pfad) as img:
        return img.size

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

                    img_breite, img_hoehe = _bildmasse(ziel)
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

                    img_breite, img_hoehe = _bildmasse(ziel)
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

