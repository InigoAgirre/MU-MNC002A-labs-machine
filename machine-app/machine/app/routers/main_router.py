import logging
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.sql import crud, schemas
from .router_utils import raise_and_log_error
import requests
from app.keys import RsaKeys
from ..business_logic.machine import Machine
from app.dependencies import get_db, get_machine

logger = logging.getLogger(__name__)
router = APIRouter()


# Pieces ###########################################################################################
@router.get(
    "/piece",
    response_model=List[schemas.Piece],
    summary="retrieve piece list",
    tags=["Piece", "List"]
)
async def get_piece_list(
        db: AsyncSession = Depends(get_db)
):
    """Retrieve the list of pieces."""
    logger.debug("GET '/piece' endpoint called.")
    return await crud.get_piece_list(db)


@router.get(
    "/piece/{piece_id}",
    summary="Retrieve single piece by id",
    response_model=schemas.Piece,
    tags=['Piece']
)
async def get_single_piece(
        piece_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Retrieve single piece by id"""
    logger.debug("GET '/piece/%i' endpoint called.", piece_id)
    return await crud.get_piece(db, piece_id)


# Machine ##########################################################################################
@router.get(
    "/machine/status",
    summary="Retrieve machine status",
    response_model=schemas.MachineStatusResponse,
    tags=['Machine']
)
async def machine_status(
        my_machine: Machine = Depends(get_machine)
):
    """Retrieve machine status"""
    logger.debug("GET '/machine/status' endpoint called.")
    working_piece_id = None
    if my_machine.working_piece is not None:
        working_piece_id = my_machine.working_piece['id']

    queue = await my_machine.list_queued_pieces()

    return schemas.MachineStatusResponse(
        status=my_machine.status,
        working_piece=working_piece_id,
        queue=queue
    )


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
