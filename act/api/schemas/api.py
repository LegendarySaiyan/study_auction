from decimal import Decimal

from pydantic import BaseModel
from pydantic import Field


class VirtualAccountBalance(BaseModel):
    balance: Decimal = Field(..., title='Баланс')
