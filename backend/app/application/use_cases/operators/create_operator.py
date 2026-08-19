from app.application.exceptions import ForbiddenError
from app.application.ports.password_hasher import PasswordHasher
from app.domain.entities.operator import Operator, OperatorRole
from app.domain.exceptions import DomainError
from app.domain.repositories.operator_repository import OperatorRepository


def create_operator(
    operators: OperatorRepository,
    hasher: PasswordHasher,
    *,
    actor: Operator,
    email: str,
    password: str,
    role: OperatorRole,
) -> Operator:
    if actor.role is not OperatorRole.ADMIN:
        raise ForbiddenError
    if role is OperatorRole.ADMIN:
        raise DomainError("A second admin cannot be created")
    if operators.get_by_email(email.strip().lower()) is not None:
        raise DomainError("Operator email already exists")
    created = Operator.create(
        email=email,
        password_hash=hasher.hash(password),
        role=role,
    )
    return operators.add(created)
