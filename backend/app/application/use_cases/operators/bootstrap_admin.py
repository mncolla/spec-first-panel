from app.application.ports.password_hasher import PasswordHasher
from app.domain.entities.operator import Operator, OperatorRole
from app.domain.repositories.operator_repository import OperatorRepository


def bootstrap_admin(
    operators: OperatorRepository,
    hasher: PasswordHasher,
    *,
    email: str,
    password: str,
) -> Operator | None:
    if not email.strip() or not password:
        return None
    if operators.get_by_role(OperatorRole.ADMIN) is not None:
        return None
    admin = Operator.create(
        email=email,
        password_hash=hasher.hash(password),
        role=OperatorRole.ADMIN,
    )
    return operators.add(admin)
