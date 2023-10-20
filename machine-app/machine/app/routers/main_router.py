import logging
from typing import List
from fastapi import APIRouter, Depends, status, Request, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.sql import crud, schemas
from .router_utils import raise_and_log_error
import requests
from app.keys import RsaKeys

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/pieces",
    summary="Get a list of pieces",
    response_model=List[schemas.Piece],
    tags=["Pieces"]
)
async def get_pieces(
        db: AsyncSession = Depends(get_db),
):
    """Endpoint to retrieve a list of pieces."""
    logger.debug("GET '/pieces' endpoint called.")
    pieces = await crud.get_pieces(db)
    return pieces


@router.get(
    "/pieces/{piece_ref}",
    summary="Get a single piece by ID",
    response_model=schemas.Piece,
    tags=["Pieces"]
)
async def get_piece(
        piece_ref: int = Path(..., description="The ID of the piece to retrieve"),
        db: AsyncSession = Depends(get_db),
):
    """Endpoint to retrieve a single piece by ID."""
    logger.debug(f"GET '/piece/{piece_ref}' endpoint called.")
    piece = await crud.get_piece_by_id(db, piece_ref)
    if piece is None:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, "Piece not found")
    return piece


def get_public_key():
    logger.debug("GETTING PUBLIC KEY")
    endpoint = "http://192.168.17.11/auth/public-key"

    try:
        response = requests.get(endpoint)

        if response.status_code == 200:
            x = response.json()["public_key"]
            RsaKeys.set_public_key(x)
        else:
            print(f"Error al obtener la clave pública. Código de respuesta: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error de solicitud: {e}")


def get_jwt_from_request(request):
    auth = request.headers.get('Authorization')
    if auth is None:
        raise_and_log_error(logger, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "NO JWT PROVIDED")
    jwt_token = auth.split(" ")[1]
    return jwt_token
