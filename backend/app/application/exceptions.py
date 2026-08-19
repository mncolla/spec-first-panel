class NotFoundError(Exception):
    def __init__(self, message: str = "Department not found") -> None:
        super().__init__(message)
        self.message = message
