from app.application.exceptions import ForbiddenError
from app.domain.entities.operator import Operator, OperatorRole
from app.domain.repositories.operator_repository import OperatorRepository


def list_operators(operators: OperatorRepository, *, actor: Operator) -> list[Operator]:
    if actor.role is not OperatorRole.ADMIN:
        raise ForbiddenError
    return operators.list()
