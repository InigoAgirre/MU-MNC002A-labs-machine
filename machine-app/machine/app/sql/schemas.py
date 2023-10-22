# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
# pylint: disable=too-few-public-methods
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


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


class MachineStatusResponse(BaseModel):
    """machine status schema definition."""
    status: str = Field(
        description="Machine's current status",
        default=None,
        example="Waiting"
    )
    working_piece: Optional[int] = Field(
        description="Current working piece id. None if not working piece.",
        example=1
    )
    queue: List[int] = Field(description="Queued piece ids")
