import typing as tp
import uuid
from decimal import Decimal

from fastapi_jsonrpc import *

from act import models
from act.api import schemas

app = API()

api_v1 = Entrypoint(
    '/api/v1/jsonrpc',
    summary='Web JSON-RPC api entrypoint',
    description="""Апи ручки""",
)


class MyError(BaseError):
    CODE = 5000
    MESSAGE = 'My error'

    class DataModel(BaseModel):
        details: str


@api_v1.method(
    summary='Получить баланс виртуального счета',
    description='Специальный счет для оплаты лотов',
)
def get_balance(
    virtual_account_id: uuid.UUID
) -> schemas.api.VirtualAccountBalance:
    virtual_account = models.VirtualAccount.objects.filter(virtual_account_id=virtual_account_id).get_or_none()

    if virtual_account is None:
        return schemas.api.VirtualAccountBalance(
            balance=Decimal(0)
        )
    return schemas.api.VirtualAccountBalance(balance=virtual_account.balance)
