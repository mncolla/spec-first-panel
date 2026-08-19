class InMemoryStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.deleted: list[str] = []
        self.bucket_ensured = False

    def ensure_bucket(self) -> None:
        self.bucket_ensured = True

    def public_url(self, key: str) -> str:
        return f"https://memory.local/{key}"

    def put(self, key: str, body: bytes, content_type: str) -> str:
        self.ensure_bucket()
        self.objects[key] = body
        return self.public_url(key)

    def delete(self, key: str) -> None:
        self.objects.pop(key, None)
        self.deleted.append(key)
