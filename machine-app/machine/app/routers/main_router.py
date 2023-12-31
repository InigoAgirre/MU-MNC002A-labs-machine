import os
from typing import List
import logging
from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.sql import crud, schemas
from .router_utils import raise_and_log_error
import requests
from app.business_logic.BLConsul import get_consul_service
from app.routers.log_publisher import publish_log_msg
from fastapi.responses import JSONResponse
from app.keys import RsaKeys

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/machine/pieces",
    summary="Retrieve all YOUR pieces by id",
    response_model=List[schemas.PieceBase],
    tags=['Piece', 'List']
)
async def view_deliveries(request: Request, db: AsyncSession = Depends(get_db)):
    logger.debug("GET '/machine' endpoint called.")
    try:
        token = get_jwt_from_request(request)
        keys = RsaKeys()
        keys.verify_jwt(token)
        piece_list = await crud.get_piece_list(db)
        pieces_as_dict = [
            {
                "id": item.id,
                "status": item.status,
                "order_id": item.order_id
            }
            for item in piece_list
        ]
        return JSONResponse(pieces_as_dict)
    except Exception as exc:
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error getting the deliveries: {exc}")


@router.get("/machine/health", summary="Health check", response_model=str)
@router.head("/machine/health", summary="Health check")
def health_check():
    """Health check endpoint."""
    if RsaKeys.get_public_key() is None:
        raise HTTPException(status_code=503, detail="Detalle del error")
    return "OK"


def get_public_key():
    logger.debug("GETTING PUBLIC KEY")
    replicas_auth = get_consul_service("auth")
    endpoint = f"https://{replicas_auth['Address']}/auth/public-key"

    try:
        response = requests.get(endpoint, verify=False)

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
