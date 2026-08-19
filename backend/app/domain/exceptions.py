class DomainError(Exception):
    """Raised when a domain invariant is violated."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
