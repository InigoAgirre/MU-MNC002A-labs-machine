import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models
from . import schemas

logger = logging.getLogger(__name__)


async def add_money_to_user(db: AsyncSession, user):
    db_user = await get_element_by_id(db, models.Money, user.user_id)
    if db_user is not None:
        db_user.money += user.money
        await db.commit()
        await db.refresh(db_user)
        logger.debug("ACTUALIZADO")
        money_base = schemas.MoneyBase(
            user_id=db_user.user_id,
            money=db_user.money
        )
    else:
        user_post = models.Money(
            user_id=user.user_id,
            money=user.money
        )
        db.add(user_post)
        await db.commit()
        await db.refresh(user_post)
        logger.debug("CREADO")
        money_base = schemas.MoneyBase(
            user_id=user_post.user_id,
            money=user_post.money
        )

    return money_base


async def pay_order(db: AsyncSession, user):
    db_user = await get_element_by_id(db, models.Money, user.user_id)
    if db_user is None:
        return None

    if db_user.money - user.money < 0:
        return 1

    db_user.money -= user.money
    await db.commit()
    await db.refresh(db_user)
    logger.debug("ACTUALIZADO")
    return 2


async def get_element_by_id(db: AsyncSession, model, element_id):
    """Retrieve any DB element by id."""
    if element_id is None:
        return None

    element = await db.get(model, element_id)
    return element
