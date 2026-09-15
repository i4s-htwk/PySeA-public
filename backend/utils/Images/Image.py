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
            width: The new width, in pixels, as a string (e.g. ``"400"``).
        """
        self.width = width
        if width not in ("", "0"):
            self.height = str(float(self.ratio) * float(self.width))

    def set_height(self, height):
        """Set the display height of the image.

        The width is recalculated automatically so the original aspect
        ratio is preserved.
        Args:
            height: The new height, in pixels, as a string.
        """
        self.height = height
        if height not in ("", "0"):
            self.width = str(float(self.height)/ float(self.ratio))

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