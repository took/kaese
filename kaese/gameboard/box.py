class Box:
    """Dumb container for a single box (holds owner ID and the two lines on the right and below the box)"""
    owner: int = 0
    line_right: int = 0
    line_below: int = 0

    def __init__(self, owner: int = 0, line_right: int = 0, line_below: int = 0) -> None:
        self.owner = owner
        self.line_right = line_right
        self.line_below = line_below


# Doctests for the Box class
def test_box():
    """
    >>> box1 = Box()
    >>> box1.owner
    0
    >>> box1.line_right
    0
    >>> box1.line_below
    0

    >>> box2 = Box(owner=1, line_right=2, line_below=1)
    >>> box2.owner
    1
    >>> box2.line_right
    2
    >>> box2.line_below
    1
    """
