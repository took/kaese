from typing import List, Optional

from kaese.gui.popup_window import PopupWindow


class PopupWindowsQueue:
    """A Last-In First-Out (LIFO) queue implementation.

    This class represents a LIFO queue where elements are added to and removed from the same end,
    similar to a stack. It also exposes an extra property to access the current front `PopupWindow` object.

    Attributes:
        queue: The Queue
        front: The current front `PopupWindow` object in the PopupWindows queue.

    Methods:
        push(item: PopupWindow) -> None:
            Add an item to the PopupWindows queue.

        pop() -> None:
            Remove the topmost item from the PopupWindows queue and update front.

        is_empty() -> bool:
            Returns True if queue is empty.

        get_front() -> PopupWindow:
            Return the topmost item from the PopupWindows queue.

    """

    queue: List[PopupWindow]
    front: Optional[PopupWindow]

    def __init__(self) -> None:
        self.queue = []
        self.front = None

    def push(self, item: PopupWindow) -> None:
        """Add an item to the PopupWindows queue.

        Args:
            item (PopupWindow): The `PopupWindow` object to be added to the PopupWindows queue.

        Returns:
            None
        """
        self.queue.append(item)
        self.front = item

    def pop(self) -> None:
        """Remove the topmost item from the PopupWindows queue.

        Returns:
            None.

        Raises:
            IndexError: If the PopupWindows queue is empty.
        """
        if self.is_empty():
            raise IndexError("PopupWindows queue is empty")
        self.queue.pop()
        if self.is_empty():
            self.front = None
        else:
            self.front = self.queue.pop()
            self.push(self.front)

    def is_empty(self) -> bool:
        """Returns True if queue is empty.

        Returns:
            True if queue is empty
        """
        return not self.queue

    def get_front(self) -> PopupWindow:
        """Return the topmost item from the PopupWindows queue.

        Returns:
            PopupWindow: The topmost `PopupWindow` object from the PopupWindows queue.

        Raises:
            IndexError: If the PopupWindows queue is empty.
        """
        return self.front
