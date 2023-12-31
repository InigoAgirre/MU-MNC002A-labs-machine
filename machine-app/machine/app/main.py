import logging
import os
import asyncio
from fastapi import FastAPI, BackgroundTasks
from app.routers import main_router
from app.sql import models, database
from app.routers.machine_suscriber import AsyncConsumer
from app.business_logic.BLConsul import register_consul_service
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Configure logging ################################################################################
logger = logging.getLogger(__name__)

# OpenAPI Documentation ############################################################################
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
logger.info("Running app version %s", APP_VERSION)
DESCRIPTION = """
Monolithic manufacturing order application - Machine Microservice.
"""

tag_metadata = [

    {
        "name": "Machine",
        "description": "Endpoints related to machine",
    },

]

app = FastAPI(
    redoc_url=None,  # disable redoc documentation.
    title="FastAPI - Authentication app",
    description=DESCRIPTION,
    version=APP_VERSION,
    servers=[
        {"url": "/", "description": "Development"}
    ],
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/"
    },
    openapi_tags=tag_metadata,

)

app.include_router(main_router.router)

# Configuración de TLS
cert_path = "/app/certs/fastapi_cert.pem"
key_path = "/app/certs/fastapi_key.pem"

# Configuración de middleware para redireccionar HTTP a HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# Configuración de middleware para Trusted Host (opcional pero recomendado)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

rabbitmq_consumer = AsyncConsumer('event_exchange', 'order.piece', AsyncConsumer.consume_order)
rabbitmq_consumer2 = AsyncConsumer('event_exchange', 'auth.publickey', AsyncConsumer.ask_public_key)


@app.on_event("startup")
async def startup_event():
    """Configuration to be executed when fastapi server starts."""
    logger.info("Creating database tables")
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    main_router.get_public_key()

    logger.debug("WAITING FOR RABBITMQ")
    consumer_tasks = [
        asyncio.create_task(rabbitmq_consumer.start_consuming()),
        asyncio.create_task(rabbitmq_consumer2.start_consuming())
    ]
    asyncio.gather(*consumer_tasks)

    register_consul_service()


# Main #############################################################################################
# If application is run as script, execute uvicorn on port 8000
if __name__ == "__main__":
    import uvicorn

    logger.debug("App run as script")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config='logging.yml',
        ssl_keyfile=key_path,
        ssl_certfile=cert_path
    )

    logger.debug("App finished as script")
