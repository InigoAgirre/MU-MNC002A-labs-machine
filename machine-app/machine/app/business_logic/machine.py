import json
from random import randint
from time import sleep
from collections import deque
from threading import Thread, Lock, Event
from sqlalchemy.sql import select
from app.sql.models import Piece
from ..routers.machine_publisher import publish_msg
from app.sql.database import SessionLocal


class Machine(Thread):
    STATUS_WAITING = "Waiting"
    STATUS_CHANGING_PIECE = "Changing Piece"
    STATUS_WORKING = "Working"
    __status_lock__ = Lock()
    thread_session = None

    def __init__(self):
        Thread.__init__(self)
        self.queue = deque([])
        self.working_piece = None
        self.status = Machine.STATUS_WAITING
        self.instance = self
        self.queue_not_empty_event = Event()
        self.reload_pieces_at_startup()
        self.order_finished = 0
        self.start()

    async def reload_pieces_at_startup(self):
        self.thread_session = SessionLocal()
        manufacturing_piece = await self.thread_session.execute(
            select(Piece).filter(Piece.c.status == Piece.STATUS_MANUFACTURING))
        manufacturing_piece = manufacturing_piece.scalar()  # Use scalar to get the result
        if manufacturing_piece:
            self.add_piece_to_queue(manufacturing_piece)

        queued_pieces = await self.thread_session.execute(select(Piece).filter(Piece.c.status == Piece.STATUS_QUEUED))
        queued_pieces = queued_pieces.scalars().all()
        if queued_pieces:
            self.add_pieces_to_queue(queued_pieces)
        await self.thread_session.close()

    def run(self):
        while True:
            self.queue_not_empty_event.wait()
            print("Thread notified that the queue is not empty.")
            self.thread_session = SessionLocal()  # Use SessionLocal

            while self.queue.__len__() > 0:
                self.create_piece()

            self.queue_not_empty_event.clear()
            print("Lock thread because the queue is empty.")

            self.instance.status = Machine.STATUS_WAITING
            self.thread_session.close()

    def create_piece(self):
        piece_ref = self.queue.popleft()

        self.working_piece = self.thread_session.query(Piece).get(piece_ref)

        self.working_piece_to_manufacturing()

        sleep(randint(5, 20))

        self.working_piece_to_finished()

        self.working_piece = None

    def working_piece_to_manufacturing(self):
        self.status = Machine.STATUS_WORKING
        self.working_piece.status = Piece.STATUS_MANUFACTURING
        self.thread_session.commit()
        self.thread_session.flush()

    async def working_piece_to_finished(self):
        self.instance.status = Machine.STATUS_CHANGING_PIECE
        self.working_piece.status = Piece.STATUS_MANUFACTURED
        self.thread_session.commit()
        self.thread_session.flush()

        order_id = self.working_piece.order_id

        message_body = {
            'order_id': order_id
        }
        await publish_msg(json.dumps(message_body))

    def add_pieces_to_queue(self, pieces):
        for piece in pieces:
            self.add_piece_to_queue(piece)

    def remove_pieces_from_queue(self, pieces):
        for piece in pieces:
            if piece.status == Piece.STATUS_QUEUED:
                self.queue.remove(piece.ref)
                piece.status = Piece.STATUS_CANCELLED

    def add_piece_to_queue(self, piece):
        self.queue.append(piece.piece_id)
        piece.status = Piece.STATUS_QUEUED
        print("Adding piece to the queue: {}".format(piece.piece_id))
        self.queue_not_empty_event.set()
