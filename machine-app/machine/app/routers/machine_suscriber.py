import asyncio
import json
import logging
from random import randint
from time import sleep
from app.business_logic.machine import Machine
from app.routers.machine_publisher import publish_msg
from app.sql.database import SessionLocal
import os
import aio_pika
from fastapi import status
from app.sql import crud, schemas
from .router_utils import raise_and_log_error
import requests
from app.keys import RsaKeys
from app.business_logic.BLConsul import get_consul_service
from app.routers.log_publisher import publish_log_msg

logger = logging.getLogger(__name__)
my_machine = Machine()


class AsyncConsumer:

    def __init__(self, exchange_name, routing_key, callback_func):
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.callback_func = callback_func

    async def start_consuming(self):
        logger.info("Waiting for RabbitMQ")
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@192.168.17.46/",
            port=5671,
            loop=asyncio.get_event_loop(),
            ssl=True,
        )

        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)  # Recibir un mensaje a la vez
            exchange = await channel.declare_exchange(self.exchange_name, type=aio_pika.ExchangeType.TOPIC)
            queue = await channel.declare_queue("", exclusive=True)
            await queue.bind(exchange, routing_key=self.routing_key)

            async with queue.iterator() as queue_iterator:
                async for message in queue_iterator:
                    async with message.process():
                        await self.callback_func(message.body, exchange)

    @staticmethod
    async def consume_order(body, exchange):
        logger.debug("Consume order has been called")
        db = SessionLocal()
        content = json.loads(body)
        order_id = content['id']
        num_pieces_ordered = content['number_of_pieces']
        logger.info(f"Received order for Order ID: {order_id}")
        piece_schema = schemas.PieceBase(status="Queued", order_id=content['id'])

        for _ in range(num_pieces_ordered):
            piece = await crud.add_new_piece(db, piece_schema)
            logger.info(f"Performing piece ID:{piece.id}")
            await crud.update_piece_status(db, piece.id, piece.STATUS_MANUFACTURING)
            sleep(randint(5, 10))
            await crud.update_piece_status(db, piece.id, piece.STATUS_MANUFACTURED)
            await crud.update_piece_manufacturing_date_to_now(db, piece.id)

            message_body = {
                'order_id': order_id
            }
            await publish_msg(exchange, "machine.processed", json.dumps(message_body))
            logger.info(f"Piece ID:{piece.id} done")

        logger.info(f"Pieces for order {order_id} done")


    @staticmethod
    async def ask_public_key(body, exchange):
        logger.debug("GETTING PUBLIC KEY RABBITMQ")
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
            await publish_log_msg(e, "ERROR", os.path.basename(__file__))
            print(f"Error de solicitud: {e}")
