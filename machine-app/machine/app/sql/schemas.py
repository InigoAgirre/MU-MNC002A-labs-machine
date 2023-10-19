from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    detail: Optional[str] = Field(example="error or success message")

class Piece(BaseModel):
    piece_id: int = Field(
        description="Identificador de la pieza",
        example="1"
    )
    manufacturing_date: datetime = Field(
        description="Fecha en que se fabricó la pieza",
        example="2022-07-22T17:32:32.193211"
    )
    status: str = Field(
        description="Estado actual de la pieza",
        default="Queued",
        example="Manufactured"
    )
    order_id: int = Field(
        description="Identificador del pedido al que pertenece la pieza",
        example="1"
    )
