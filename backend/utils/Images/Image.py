def _to_str(value):
    """Accepts numbers as well as strings, since the XML export only serializes strings."""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip()


class Image:
    """A single image loaded into the test.

    Instances are held in ``StoreImages`` and accessed via the dictionary
    returned by ``StoreImages.map()`` (e.g. ``images["bild.png"]``).
    ``set_width()`` / ``set_height()`` resize the image while keeping its
    aspect ratio. The object can be embedded directly into an item body.
    """
    def __init__ (self, href, id, width, height, ratio):
        self.href = href
        self.id = id
        self.width = width
        self.height = height
        self.ratio = ratio

    def set_width(self, width):
        """Set the display width of the image.

        The height is recalculated automatically so the original aspect
        ratio is preserved.
        Args:
            width: The new width, in pixels (e.g. ``"400"`` or ``400``).
        """
        width = _to_str(width)
        self.width = width
        if width not in ("", "0"):
            self._check_ratio()
            self.height = str(float(self.ratio) * float(self.width))

    def set_height(self, height):
        """Set the display height of the image.

        The width is recalculated automatically so the original aspect
        ratio is preserved.
        Args:
            height: The new height, in pixels (e.g. ``"300"`` or ``300``).
        """
        height = _to_str(height)
        self.height = height
        if height not in ("", "0"):
            self._check_ratio()
            self.width = str(float(self.height)/ float(self.ratio))

    def _check_ratio(self):
        if float(self.ratio or 0) <= 0:
            raise ValueError(
                f"Seitenverhältnis von '{self.href}' unbekannt: Die Bildmaße konnten nicht ermittelt werden "
                f"(bei SVG: width/height oder viewBox im <svg>-Tag fehlen). "
                f"Bitte image.width und image.height direkt setzen.")

    def to_dict(self):
        return {
            "href": self.href,
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "ratio": self.ratio
        }

    @staticmethod
    def from_dict(data):
        return Image(data["href"], data["id"], data["width"], data["height"], data["ratio"])

    def __str__(self) -> str:
        return "{"+self.id+"}"

    def __radd__(self, other: object) -> str:
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented

    def __add__(self, other: object) -> str:
        if isinstance(other, str):
            return str(self) + other
        return NotImplemented