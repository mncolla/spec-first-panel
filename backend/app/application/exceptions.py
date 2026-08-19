class NotFoundError(Exception):
    def __init__(self, message: str = "Department not found") -> None:
        super().__init__(message)
        self.message = message


class UnauthorizedError(Exception):
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message)
        self.message = message


class ForbiddenError(Exception):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message)
        self.message = message
