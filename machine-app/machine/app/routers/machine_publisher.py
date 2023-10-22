import pika
import aio_pika
import logging
import asyncio

logger = logging.getLogger(__name__)


async def publish_msg(exchange, routing_key, message):
    logger.debug("enter publish_msg")

    try:
        await exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=routing_key,
        )
    except Exception as e:
        logger.debug(e)

    logger.debug(f" [x] Sent {routing_key}:{message}")