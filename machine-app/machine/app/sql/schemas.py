# -*- coding: utf-8 -*-
"""Classes for Request/Response schema definitions."""
# pylint: disable=too-few-public-methods
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class PieceBase(BaseModel):
    status: str = Field(
        description="Estado actual de la pieza",
        default="Created",
        example="Finished"
    )
    order_id: int = Field(
        description="Identificador del pedido al que pertenece la pieza",
        default=None,
        example=1
    )
