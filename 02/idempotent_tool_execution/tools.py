import uuid
from typing import Literal

from pydantic import BaseModel, Field


class TransactionCreationError(BaseException):
    transaction_id: str

    def __init__(self, message: str | None, transaction_id: str) -> None:
        self.transaction_id = transaction_id
        self.message = message or f"Internal Server Error while creating new transaction with id {transaction_id}"


class BankTransactionSchema(BaseModel):
    """ Bank Transaction schema """
    id: str = Field(description="Bank Transaction ID")
    amount: float = Field(description="Bank Transaction Amount")
    currency: Literal['INR', 'USD'] = Field(description="Bank Transaction Currency", default='INR')
    transaction_type: Literal['debit', 'credit'] = Field(description="Bank Transaction Type")


transactions: list[BankTransactionSchema] = [
    BankTransactionSchema(
        id="7f79aea5-3ff7-42e1-8b9d-22bfaefdaddf",
        amount=100,
        transaction_type='credit',
    ),
    BankTransactionSchema(
        id="686ade26-13ba-4bf0-8482-30679cf1fd55",
        amount=50,
        transaction_type='debit',
    )
]


def create_new_transaction(amount: float, transaction_type: Literal['debit', 'credit'],
                           currency: Literal['INR', 'USD']) -> str:
    """ Create new transaction in a bank

    Args:
        amount (float): Amount to be created
        transaction_type (str): Type of transaction to be created
        currency (str): Currency to be used

    Returns:
        str: Transaction ID

    """
    transaction_id = str(uuid.uuid4())
    transactions.append(BankTransactionSchema(
        id=transaction_id,
        amount=amount,
        transaction_type=transaction_type,
        currency=currency,
    ))
    raise TransactionCreationError("", transaction_id=transaction_id)
    return transaction_id


def view_transactions() -> list[BankTransactionSchema]:
    """ View transactions in a bank

    :returns: list of BankTransactionSchema

    """
    return transactions.copy()


def view_transaction(transaction_id: str) -> BankTransactionSchema | None:
    """ View transactions in a bank

    :returns: list of BankTransactionSchema

    """
    for tr in transactions:
        if tr.id == transaction_id:
            return tr
    raise Exception(f"Transaction with id {transaction_id} not found")
