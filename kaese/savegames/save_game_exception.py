class SaveGameException(Exception):
    """If loading or saving a game raises an exception, it shall be of this type."""

    original_exception: Exception

    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception
