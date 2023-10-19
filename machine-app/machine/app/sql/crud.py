from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from models import Piece


async def get_pieces(db: AsyncSession):
    pieces = await db.execute(select(Piece))
    return pieces.scalars().all()


async def get_piece_by_id(db: AsyncSession, piece_id: int):
    piece = await db.execute(select(Piece).filter(Piece.c.piece_id == piece_id))
    return piece.scalar()
