import asyncio
import json
import logging
from random import randint
from time import sleep

import aio_pika
import requests

from app.keys import RsaKeys
from app.business_logic.machine import Machine
from app.routers.machine_publisher import publish_msg
from app.sql import schemas

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
        content = json.loads(body)
        order_id = content['order_id']
        num_pieces_ordered = content['number_of_pieces']

        logger.info(f"Received order for Order ID: {order_id}")

        for step in range(num_pieces_ordered):
            logger.info(f"Performing piece {step + 1}")
            sleep(randint(5, 20))
            logger.info(f"Piece {step + 1} done")
            #piece = schemas.Piece(order_id=order_id)
            #await my_machine.add_piece_to_queue(piece)

        message_body = {
            'order_id': order_id
        }
        await publish_msg(exchange, "machine.processed", json.dumps(message_body))
        logger.info(f"Processed order for Order ID: {order_id}")

    @staticmethod
    async def ask_public_key(body, exchange):
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
