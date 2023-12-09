from sqlalchemy.sql import select

from app.routers.router_utils import raise_and_log_error

# -*- coding: utf-8 -*-
"""Functions that interact with the database."""
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.sql import models
from fastapi import status

logger = logging.getLogger(__name__)


async def add_new_piece(db: AsyncSession, piece):
    """Adds a new piece to the database"""
    db_piece = models.Piece(
        status=piece.status,
        order_id=piece.order_id
    )
    db.add(db_piece)
    await db.commit()
    try:
        await db.refresh(db_piece)
        # The code inside this block will be executed if the operation succeeds.
    except Exception as e:
        # The code inside this block will be executed if an exception (error) occurs during the operation.
        print(f"An error occurred: {e}")
        # You can also handle the error in a more specific way based on the exception type or take appropriate action.
    return db_piece


# Piece functions ##################################################################################
async def get_piece_list_by_status(db: AsyncSession, status):
    """Get all pieces with a given status from the database."""
    # query = db.query(models.Piece).filter_by(status=status)
    # return query.all()
    stmt = select(models.Piece).where(models.Piece.status == status)
    # result = await db.execute(stmt)
    # item_list = result.scalars().all()

    return await get_list_statement_result(db, stmt)


async def update_piece_status(db: AsyncSession, piece_id, status):
    """Persist new piece status on the database."""
    db_piece = await get_element_by_id(db, models.Piece, piece_id)
    if db_piece is not None:
        db_piece.status = status
        await db.commit()
        await db.refresh(db_piece)
    return db_piece


async def update_piece_manufacturing_date_to_now(db: AsyncSession, piece_id):
    """For a given piece_id, sets piece's manufacturing_date to current datetime."""
    db_piece = await get_element_by_id(db, models.Piece, piece_id)
    if db_piece is not None:
        db_piece.manufacturing_date = datetime.now()
        await db.commit()
        await db.refresh(db_piece)
    return db_piece


async def get_piece_list(db: AsyncSession):
    """Load all the orders from the database for a specific user."""
    try:
        # Filtra las entregas por el user_id
        result = await db.execute(select(models.Piece))
        item_list = result.unique().scalars().all()
        if not item_list:
            raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"No tienes ninguna pieza")
        else:
            return item_list
    except Exception as e:
        # Puedes manejar la excepción de la forma que consideres adecuada
        raise_and_log_error(logger, status.HTTP_403_FORBIDDEN, f"Error al conseguir la lista de piezas.")
        return []  # In case of error, return an empty list


async def get_piece(db: AsyncSession, piece_id):
    """Load a piece from the database."""
    return await get_element_by_id(db, models.Piece, piece_id)


# Generic functions ################################################################################
# READ
async def get_list(db: AsyncSession, model):
    """Retrieve a list of elements from database"""
    result = await db.execute(select(model))
    item_list = result.unique().scalars().all()
    return item_list


async def get_list_statement_result(db: AsyncSession, stmt):
    """Execute given statement and return list of items."""
    result = await db.execute(stmt)
    item_list = result.unique().scalars().all()
    return item_list


async def get_element_statement_result(db: AsyncSession, stmt):
    """Execute statement and return a single items"""
    result = await db.execute(stmt)
    item = result.scalar()
    return item


async def get_element_by_id(db: AsyncSession, model, element_id):
    """Retrieve any DB element by id."""
    if element_id is None:
        return None

    element = await db.get(model, element_id)
    return element


# DELETE
async def delete_element_by_id(db: AsyncSession, model, element_id):
    """Delete any DB element by id."""
    element = await get_element_by_id(db, model, element_id)
    if element is not None:
        await db.delete(element)
        await db.commit()
    return element
