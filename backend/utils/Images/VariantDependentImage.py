class VariantDependentImage:
    """An image that shows different content depending on the variant.

    An instance of this class is returned by
    ``TaskFacade.variant_dependent_image()``. ``add_image()`` assigns an
    ``Image`` to a range of variants. The object can be embedded directly
    into an item body or used as an answer option of a ``Selection``.
    """
    def __init__(self, id):
        self.id = id
        self.images = {}

    def add_image(self, image_id: str="BILD_1", lower: int=0, upper: int=0):
        """Assign an image to a range of variants.
        Args:
            image_id: The ``id`` of the ``Image`` to display (e.g.
                ``images["bild.png"].id``).
            lower: The first variant number for which this image is shown.
            upper: The last variant number for which this image is shown.
        """
        self.images["value_"+str(len(self.images)+1)] = {"image_id": image_id, "lower": lower, "upper": upper}

    def set_image_id(self, value:str,  image_id: str):
        self.images[value]["image_id"] = image_id

    def set_image_bounds(self, value: str, lb:int = None, ub:int = None):
        if lb is not None: self.images[value]["lower"] = lb
        if ub is not None: self.images[value]["upper"] = ub

    def to_dict(self):
        return {
            "id": self.id,
            "images": self.images
        }

    @staticmethod
    def from_dict(data):
        v = VariantDependentImage(data["id"])
        v.images = data["images"]
        return v

    def __str__(self) -> str:
        return "{" + self.id + "}"

    def __radd__(self, other: object) -> str:
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented

    def __add__(self, other: object) -> str:
        if isinstance(other, str):
            return str(self) + other
        return NotImplemented