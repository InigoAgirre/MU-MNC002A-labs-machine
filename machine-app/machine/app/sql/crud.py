from sqlalchemy.sql import select
from app.sql.models import Piece


async def get_pieces(db):
    pieces = await db.execute(select(Piece))
    return pieces.scalars().all()


async def get_piece_by_id(db, piece_id):
    piece = await db.execute(select(Piece).filter(Piece.c.piece_id == piece_id))
    return piece.scalar()
